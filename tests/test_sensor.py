"""Sensor / binary_sensor tests for ChoreFlow (Pflichtenheft §11.2, P3b).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    DATA_COORDINATOR,
    DATA_LOG_STORE,
    DATA_STORE,
    DOMAIN,
    EVENT_TASK_COMPLETED,
)
from custom_components.choreflow.models import Importance, LogEvent, PushChainState

from .factories import config_entry_data, make_instance

_PERSON = "person.niklas"
_NOTIFY = "notify.mobile_app_niklas"


def _prereqs(hass: HomeAssistant) -> None:
    hass.states.async_set(_PERSON, "home", {"friendly_name": "Niklas"})
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _state(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    unique_suffix: str,
    platform: str = "sensor",
) -> str:
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        platform, DOMAIN, f"{entry.entry_id}_{unique_suffix}"
    )
    assert entity_id is not None, f"entity for {unique_suffix} not registered"
    state = hass.states.get(entity_id)
    assert state is not None
    return state.state


async def test_global_and_person_sensor_counts(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    today = dt_util.now().date()
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    for inst in (
        make_instance("inst_due", due_date=today),
        make_instance("inst_overdue", due_date=today - timedelta(days=2)),
        make_instance("inst_future", due_date=today + timedelta(days=3)),
    ):
        store.task_instances[inst.id] = inst

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert _state(hass, entry, "open_tasks") == "3"
    assert _state(hass, entry, "due_tasks") == "2"
    assert _state(hass, entry, "overdue_tasks") == "1"
    # Per person sees all (visibility = all enabled persons).
    assert _state(hass, entry, "niklas_open_tasks") == "3"
    assert _state(hass, entry, "niklas_due_tasks") == "2"
    assert _state(hass, entry, "niklas_has_due_tasks", "binary_sensor") == "on"
    assert _state(hass, entry, "niklas_chain_active", "binary_sensor") == "off"
    assert _state(hass, entry, "niklas_tasks_remaining_today") == "5"


async def test_open_tasks_attribute_list(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    today = dt_util.now().date()
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    inst = make_instance(
        "inst_due",
        room="Bad",
        category="Putzen",
        importance=Importance.HIGH,
        due_date=today,
    )
    store.task_instances[inst.id] = inst
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_open_tasks"
    )
    assert entity_id is not None
    attrs = hass.states.get(entity_id).attributes
    assert attrs["api_version"] == 1
    assert attrs["total"] == 1
    assert attrs["truncated"] is False
    [task] = attrs["open_tasks"]
    assert set(task) == {
        "task_id",
        "title",
        "room",
        "category",
        "importance",
        "estimated_duration_minutes",
        "due_date",
        "snooze_until",
    }
    assert task["task_id"] == "inst_due"
    assert task["title"] == "inst_due"
    assert task["room"] == "Bad"
    assert task["category"] == "Putzen"
    assert task["importance"] == "high"
    assert task["due_date"] == today.isoformat()
    assert task["estimated_duration_minutes"] is None


async def test_completed_today_from_log(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    log_store = hass.data[DOMAIN][entry.entry_id][DATA_LOG_STORE]
    now = dt_util.now()
    await log_store.async_add_event(
        LogEvent(
            event_id="e1",
            event_type=EVENT_TASK_COMPLETED,
            timestamp=now,
            person_entity=_PERSON,
            completion_source="push",
        )
    )
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert _state(hass, entry, "completed_today") == "1"
    assert _state(hass, entry, "niklas_completed_today") == "1"


async def test_chain_sensor_exposes_daily_status(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    today = dt_util.now().date()
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    current = make_instance("current", due_date=today)
    store.task_instances[current.id] = current
    store.push_chain_states[f"{_PERSON}|{today.isoformat()}"] = PushChainState(
        person_entity=_PERSON,
        date=today,
        active=True,
        started=True,
        tasks_sent_count=2,
        current_task_id=current.id,
        sent_task_ids=["done", current.id],
    )
    log_store = hass.data[DOMAIN][entry.entry_id][DATA_LOG_STORE]
    await log_store.async_add_event(
        LogEvent(
            event_id="chain-complete",
            event_type=EVENT_TASK_COMPLETED,
            timestamp=dt_util.now(),
            person_entity=_PERSON,
            completion_source="dashboard",
        )
    )

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "binary_sensor", DOMAIN, f"{entry.entry_id}_niklas_chain_active"
    )
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "on"
    assert state.attributes["api_version"] == 1
    assert state.attributes["current_task_id"] == "current"
    assert state.attributes["current_task_title"] == "current"
    assert state.attributes["tasks_sent_today"] == 2
    assert state.attributes["tasks_completed_today"] == 1
    assert state.attributes["daily_limit"] == 5
    assert state.attributes["remaining_today"] == 3


async def test_open_tasks_preview_reports_truncation(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    for index in range(31):
        task = make_instance(f"task-{index:02d}")
        store.task_instances[task.id] = task

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_open_tasks"
    )
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes["total"] == 31
    assert state.attributes["truncated"] is True
    assert len(state.attributes["open_tasks"]) == 30
