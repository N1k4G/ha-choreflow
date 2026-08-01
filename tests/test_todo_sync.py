"""To-do sync tests for ChoreFlow (Pflichtenheft §11.2, P4).

Drives TodoSync directly with mocked ``todo`` services. Requires Home
Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta
from random import Random
from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.choreflow import _TodoSyncDebouncer
from custom_components.choreflow.const import DOMAIN, EVENT_TASK_DELETED
from custom_components.choreflow.coordinator import ChoreFlowCoordinator
from custom_components.choreflow.engine.clock import FixedClock
from custom_components.choreflow.engine.scheduler import ScheduleConfig
from custom_components.choreflow.engine.selector import PersonContext, is_suitable
from custom_components.choreflow.models import (
    AssignmentMode,
    CalendarRef,
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
    *,
    todo_cfg: dict[str, Any] | None = None,
    enabled_persons: list[str] | None = None,
) -> tuple[ChoreFlowCoordinator, ChoreFlowStore, TodoSync, list[dict], list[str]]:
    items: list[dict[str, Any]] = []
    completed: list[str] = []
    counter = {"n": 0}

    async def _get_items(call: ServiceCall) -> dict[str, Any]:
        return {_ENTITY: {"items": items}}

    async def _update_item(call: ServiceCall) -> None:
        uid = call.data["item"]
        status = call.data.get("status")
        for item in items:
            if item.get("uid") == uid:
                if status is not None:
                    item["status"] = status
                break
        if status == "completed":
            completed.append(uid)

    async def _add_item(call: ServiceCall) -> None:
        counter["n"] += 1
        items.append(
            {
                "uid": f"new{counter['n']}",
                "summary": call.data["item"],
                "description": call.data.get("description"),
                "status": "needs_action",
            }
        )

    async def _remove_item(call: ServiceCall) -> None:
        uid = call.data["item"]
        items[:] = [item for item in items if item.get("uid") != uid]

    hass.services.async_register(
        "todo", "get_items", _get_items, supports_response=SupportsResponse.ONLY
    )
    hass.services.async_register("todo", "update_item", _update_item)
    hass.services.async_register("todo", "add_item", _add_item)
    hass.services.async_register("todo", "remove_item", _remove_item)
    hass.states.async_set(_ENTITY, "1")

    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    settings = ChoreFlowSettings(
        name="Home",
        enabled_persons=enabled_persons or [],
        person_settings={},
        schedule=ScheduleConfig.with_defaults(),
        max_tasks_per_person_per_day=5,
        todo=todo_cfg or _todo_cfg(),
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


async def test_removed_imported_item_deletes_without_completion(
    hass: HomeAssistant,
) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})
    await todo_sync.async_sync()
    items.clear()

    await todo_sync.async_sync()
    await hass.async_block_till_done()

    inst = store.task_instances["task_todo_u1"]
    assert inst.status == TaskStatus.DELETED
    assert inst.completed_at is None
    assert inst.completion_source is None
    rows, total = await coordinator.log_store.async_query_history(
        event_types=[EVENT_TASK_DELETED],
        person_entity=None,
        room=None,
        category=None,
        limit=10,
        offset=0,
    )
    assert total == 1
    assert rows[0]["decision_reason"] == "todo item removed"


async def test_removed_exported_item_is_dismissed_without_reexport(
    hass: HomeAssistant,
) -> None:
    _coordinator, store, todo_sync, items, _ = await _build(hass)
    inst = make_instance("native")
    inst.external_refs = ExternalRefs(
        todo=TodoRef(entity_id=_ENTITY, item_uid="missing")
    )
    store.task_instances[inst.id] = inst

    await todo_sync.async_sync()
    await todo_sync.async_sync()
    await hass.async_block_till_done()

    assert inst.status == TaskStatus.OPEN
    assert inst.completed_at is None
    assert inst.external_refs.todo is not None
    assert inst.external_refs.todo.dismissed is True
    assert items == []


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


async def test_export_task_on_creation(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    coordinator.add_task_created_listener(todo_sync.async_on_task_created)

    task_id = await coordinator.async_create_task({"title": "Vacuum"})
    await hass.async_block_till_done()

    assert [i["summary"] for i in items] == ["Vacuum"]
    inst = store.task_instances[task_id]
    assert inst.external_refs.todo.entity_id == _ENTITY
    assert inst.external_refs.todo.item_uid == items[0]["uid"]


async def test_export_preserves_calendar_ref(hass: HomeAssistant) -> None:
    """Exporting a calendar task must keep its calendar ref (no dupe storm)."""
    coordinator, store, todo_sync, items, _ = await _build(hass)

    cal_ref = CalendarRef(
        entity_id="calendar.muell",
        event_uid="restmuell@2026-06-16",
        task_rule_id="cal_calendar-muell",
    )
    inst = make_instance("cal_x")
    inst.external_refs = ExternalRefs(calendar=cal_ref)
    store.task_instances[inst.id] = inst

    await todo_sync.async_on_task_created(inst)
    await hass.async_block_till_done()

    # The task is now linked to a to-do item …
    assert [i["summary"] for i in items] == ["cal_x"]
    assert inst.external_refs.todo is not None
    assert inst.external_refs.todo.item_uid == items[0]["uid"]
    # … without losing the calendar ref the calendar source relies on.
    assert inst.external_refs.calendar == cal_ref

    # A second export attempt must not add a duplicate to-do item.
    await todo_sync.async_on_task_created(inst)
    await hass.async_block_till_done()
    assert len(items) == 1


async def test_future_task_not_exported_until_due(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    coordinator.add_task_created_listener(todo_sync.async_on_task_created)

    future = date(2026, 6, 20)  # _NOW is 2026-06-15
    task_id = await coordinator.async_create_task(
        {"title": "Later", "due_date": future}
    )
    await hass.async_block_till_done()
    assert items == []  # future task is out of scope

    # Once it becomes due, the reconcile export pass picks it up.
    store.task_instances[task_id].due_date = date(2026, 6, 15)
    await todo_sync.async_sync()
    await hass.async_block_till_done()
    assert [i["summary"] for i in items] == ["Later"]


async def test_exported_task_not_reimported(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, _items, _ = await _build(hass)
    coordinator.add_task_created_listener(todo_sync.async_on_task_created)

    await coordinator.async_create_task({"title": "Dishes"})
    await hass.async_block_till_done()

    # A reconcile must not re-import the item we just exported as a new task.
    await todo_sync.async_sync()
    await hass.async_block_till_done()
    todo_instances = [
        i for i in store.task_instances.values() if i.source == TaskSource.TODO_SYNC
    ]
    assert todo_instances == []


async def test_reopen_mirrors_to_todo(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    coordinator.add_task_reopened_listener(todo_sync.async_on_task_reopened)
    items.append({"uid": "u9", "summary": "Mop", "status": "completed"})

    inst = make_instance("task_x", status=TaskStatus.COMPLETED, completed_at=_NOW)
    inst.completed_by = "person.niklas"
    inst.external_refs = ExternalRefs(todo=TodoRef(entity_id=_ENTITY, item_uid="u9"))
    store.task_instances[inst.id] = inst

    await coordinator.async_reopen_task(inst.id)
    await hass.async_block_till_done()

    assert items[0]["status"] == "needs_action"


async def test_delete_mirrors_to_todo(hass: HomeAssistant) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    coordinator.add_task_deleted_listener(todo_sync.async_on_task_deleted)
    items.append({"uid": "u9", "summary": "Trash", "status": "needs_action"})

    inst = make_instance("task_x")
    inst.external_refs = ExternalRefs(todo=TodoRef(entity_id=_ENTITY, item_uid="u9"))
    store.task_instances[inst.id] = inst

    await coordinator.async_delete_task(inst.id)
    await hass.async_block_till_done()

    assert items == []


async def test_assigned_import_is_suitable_only_for_configured_person(
    hass: HomeAssistant,
) -> None:
    cfg = _todo_cfg()
    cfg["import_defaults"]["assignment_mode"] = "assigned"
    cfg["import_defaults"]["assignment_person"] = "person.niklas"
    _coordinator, store, todo_sync, items, _ = await _build(
        hass,
        todo_cfg=cfg,
        enabled_persons=["person.niklas", "person.partner"],
    )
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})

    await todo_sync.async_sync()
    await hass.async_block_till_done()

    inst = store.task_instances["task_todo_u1"]
    assert inst.assignment_mode == AssignmentMode.ASSIGNED
    assert inst.assignment_person == "person.niklas"
    assert is_suitable(inst, PersonContext("person.niklas")) is True
    assert is_suitable(inst, PersonContext("person.partner")) is False


async def test_legacy_assigned_import_without_person_falls_back_to_random(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    cfg = _todo_cfg()
    cfg["import_defaults"]["assignment_mode"] = "assigned"
    _coordinator, store, todo_sync, items, _ = await _build(
        hass, todo_cfg=cfg, enabled_persons=["person.niklas"]
    )
    items.append({"uid": "u1", "summary": "Buy milk", "status": "needs_action"})

    await todo_sync.async_sync()

    inst = store.task_instances["task_todo_u1"]
    assert inst.assignment_mode == AssignmentMode.RANDOM
    assert inst.assignment_person is None
    assert "falling back to random" in caplog.text


async def test_overlapping_sync_requests_coalesce_to_one_trailing_run(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    _coordinator, _store, todo_sync, _items, _ = await _build(hass)
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    async def _blocked_sync_once() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            await release.wait()

    monkeypatch.setattr(todo_sync, "_async_sync_once", _blocked_sync_once)

    first = asyncio.create_task(todo_sync.async_sync())
    await entered.wait()
    await asyncio.gather(*(todo_sync.async_sync() for _ in range(5)))
    release.set()
    await first

    assert calls == 2


async def test_todo_state_bursts_and_self_writes_debounce_to_two_runs(
    hass: HomeAssistant,
) -> None:
    calls = 0
    debouncer: _TodoSyncDebouncer

    async def _sync() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            for _ in range(5):
                debouncer.async_schedule()

    debouncer = _TodoSyncDebouncer(hass, _sync)
    for _ in range(5):
        debouncer.async_schedule()

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=4))
    await hass.async_block_till_done()
    assert calls == 1

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=4))
    await hass.async_block_till_done()
    assert calls == 2
    debouncer.async_cancel()


async def test_retention_pruning_does_not_delete_external_todo_item(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, todo_sync, items, _ = await _build(hass)
    coordinator.add_task_deleted_listener(todo_sync.async_on_task_deleted)
    items.append({"uid": "u9", "summary": "Trash", "status": "completed"})
    inst = make_instance(
        "task_x",
        status=TaskStatus.COMPLETED,
        completed_at=_NOW - timedelta(days=121),
    )
    inst.external_refs = ExternalRefs(todo=TodoRef(entity_id=_ENTITY, item_uid="u9"))
    store.task_instances[inst.id] = inst
    monkeypatch.setattr(store, "async_schedule_save", lambda: None)

    assert coordinator._prune_stale(_NOW.date()) is True

    assert inst.id not in store.task_instances
    assert items == [{"uid": "u9", "summary": "Trash", "status": "completed"}]


async def test_export_skipped_when_disabled(hass: HomeAssistant) -> None:
    cfg = _todo_cfg()
    cfg["sync_completion_to_todo"] = False
    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    items: list[dict[str, Any]] = []

    async def _get_items(call: ServiceCall) -> dict[str, Any]:
        return {_ENTITY: {"items": items}}

    async def _add_item(call: ServiceCall) -> None:
        items.append(
            {"uid": "x", "summary": call.data["item"], "status": "needs_action"}
        )

    hass.services.async_register(
        "todo", "get_items", _get_items, supports_response=SupportsResponse.ONLY
    )
    hass.services.async_register("todo", "add_item", _add_item)
    hass.states.async_set(_ENTITY, "1")

    settings = ChoreFlowSettings(
        name="Home",
        enabled_persons=[],
        person_settings={},
        schedule=ScheduleConfig.with_defaults(),
        max_tasks_per_person_per_day=5,
        todo=cfg,
        calendar_sources=[],
    )
    entry = MockConfigEntry(domain=DOMAIN, data={})
    coordinator = ChoreFlowCoordinator(
        hass, entry, store, log_store, settings, clock=FixedClock(_NOW), rng=Random(1)
    )
    todo_sync = TodoSync(hass, coordinator, settings)
    coordinator.add_task_created_listener(todo_sync.async_on_task_created)

    await coordinator.async_create_task({"title": "Nope"})
    await hass.async_block_till_done()
    assert items == []


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
