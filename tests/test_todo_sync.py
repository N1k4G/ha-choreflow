"""To-do sync tests for ChoreFlow (Pflichtenheft §11.2, P4).

Drives TodoSync directly with mocked ``todo`` services. Requires Home
Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from datetime import UTC, datetime
from random import Random
from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN
from custom_components.choreflow.coordinator import ChoreFlowCoordinator
from custom_components.choreflow.engine.clock import FixedClock
from custom_components.choreflow.engine.scheduler import ScheduleConfig
from custom_components.choreflow.models import (
    ExternalRefs,
    TaskSource,
    TaskStatus,
    TodoRef,
)
from custom_components.choreflow.settings import ChoreFlowSettings
from custom_components.choreflow.sources.todo_sync import TodoSync
from custom_components.choreflow.store import ChoreFlowStore, LogStore

from .factories import make_instance

_ENTITY = "todo.haushalt"
_NOW = datetime(2026, 6, 15, 18, 0, tzinfo=UTC)


def _todo_cfg() -> dict[str, Any]:
    return {
        "enabled": True,
        "entity_id": _ENTITY,
        "import_new_items": True,
        "sync_completion_from_todo": True,
        "sync_completion_to_todo": True,
        "import_defaults": {
            "room": "Allgemein",
            "category": "Allgemein",
            "importance": "normal",
            "assignment_mode": "random",
        },
    }


@pytest.fixture(autouse=True)
def _enable(enable_custom_integrations: None) -> None:
    return None


async def _build(
    hass: HomeAssistant,
) -> tuple[ChoreFlowCoordinator, ChoreFlowStore, TodoSync, list[dict], list[str]]:
    items: list[dict[str, Any]] = []
    completed: list[str] = []

    async def _get_items(call: ServiceCall) -> dict[str, Any]:
        return {_ENTITY: {"items": items}}

    async def _update_item(call: ServiceCall) -> None:
        completed.append(call.data["item"])

    hass.services.async_register(
        "todo", "get_items", _get_items, supports_response=SupportsResponse.ONLY
    )
    hass.services.async_register("todo", "update_item", _update_item)
    hass.states.async_set(_ENTITY, "1")

    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    settings = ChoreFlowSettings(
        name="Home",
        enabled_persons=[],
        person_settings={},
        schedule=ScheduleConfig.with_defaults(),
        max_tasks_per_person_per_day=5,
        todo=_todo_cfg(),
        calendar_sources=[],
    )
    entry = MockConfigEntry(domain=DOMAIN, data={})
    coordinator = ChoreFlowCoordinator(
        hass, entry, store, log_store, settings, clock=FixedClock(_NOW), rng=Random(1)
    )
    todo_sync = TodoSync(hass, coordinator, settings)
    return coordinator, store, todo_sync, items, completed


async def test_import_new_items_with_dedup(hass: HomeAssistant) -> None:
    _coord, store, todo_sync, items, _ = await _build(hass)
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})

    await todo_sync.async_sync()
    await hass.async_block_till_done()

    inst = store.task_instances["task_todo_u1"]
    assert inst.title == "Buy milk"
    assert inst.source == TaskSource.TODO_SYNC
    assert inst.external_refs.todo.item_uid == "u1"
    assert inst.room == "Allgemein"

    # Second sync must not create a duplicate.
    await todo_sync.async_sync()
    await hass.async_block_till_done()
    todo_instances = [
        i for i in store.task_instances.values() if i.source == TaskSource.TODO_SYNC
    ]
    assert len(todo_instances) == 1


async def test_completion_from_todo(hass: HomeAssistant) -> None:
    _coord, store, todo_sync, items, _ = await _build(hass)
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})
    await todo_sync.async_sync()
    await hass.async_block_till_done()

    # Item gets checked off in the to-do app.
    items[0]["status"] = "completed"
    await todo_sync.async_sync()
    await hass.async_block_till_done()

    inst = store.task_instances["task_todo_u1"]
    assert inst.status == TaskStatus.COMPLETED
    assert inst.completion_source == "todo"


async def test_completion_to_todo(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, _items, completed = await _build(hass)
    coordinator.add_completion_listener(todo_sync.async_on_completion)

    inst = make_instance("task_x")
    # Attach a to-do ref so completion mirrors back.
    inst.external_refs = ExternalRefs(todo=TodoRef(entity_id=_ENTITY, item_uid="u9"))
    store.task_instances[inst.id] = inst

    await coordinator.async_complete_task(inst.id, "person.niklas", "dashboard")
    await hass.async_block_till_done()

    assert completed == ["u9"]


async def test_unavailable_entity_suspends_and_recovers(
    hass: HomeAssistant,
) -> None:
    _coord, _store, todo_sync, items, _ = await _build(hass)
    hass.states.async_set(_ENTITY, "unavailable")

    await todo_sync.async_sync()
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    issue_id = f"todo_unavailable_{_ENTITY}"
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    # Back online → issue cleared, import resumes.
    hass.states.async_set(_ENTITY, "1")
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})
    await todo_sync.async_sync()
    await hass.async_block_till_done()

    assert registry.async_get_issue(DOMAIN, issue_id) is None
    assert "task_todo_u1" in _store.task_instances
