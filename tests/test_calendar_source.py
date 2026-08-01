"""Calendar source tests for ChoreFlow (Pflichtenheft §11.2, P5).

Drives CalendarSource directly with a mocked ``calendar.get_events``. Requires
Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
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
from custom_components.choreflow.models import Importance, TaskSource, TaskStatus
from custom_components.choreflow.settings import ChoreFlowSettings
from custom_components.choreflow.sources.calendar_source import CalendarSource
from custom_components.choreflow.store import ChoreFlowStore, LogStore

_CAL = "calendar.abfuhr"
_NOW = datetime(2026, 6, 18, 12, 0, tzinfo=UTC)


def _calendar_cfg() -> list[dict[str, Any]]:
    return [
        {
            "entity_id": _CAL,
            "enabled": True,
            "summary_contains": ["Restmüll"],
            "due_offset_days": -1,
        }
    ]


@pytest.fixture(autouse=True)
def _enable(enable_custom_integrations: None) -> None:
    return None


async def _build(
    hass: HomeAssistant,
) -> tuple[ChoreFlowCoordinator, ChoreFlowStore, CalendarSource, list[dict]]:
    events: list[dict[str, Any]] = []

    async def _get_events(call: ServiceCall) -> dict[str, Any]:
        return {_CAL: {"events": events}}

    hass.services.async_register(
        "calendar", "get_events", _get_events, supports_response=SupportsResponse.ONLY
    )
    hass.states.async_set(_CAL, "on")

    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    settings = ChoreFlowSettings(
        name="Home",
        enabled_persons=[],
        person_settings={},
        schedule=ScheduleConfig.with_defaults(),
        max_tasks_per_person_per_day=5,
        todo={},
        calendar_sources=_calendar_cfg(),
    )
    entry = MockConfigEntry(domain=DOMAIN, data={})
    coordinator = ChoreFlowCoordinator(
        hass, entry, store, log_store, settings, clock=FixedClock(_NOW), rng=Random(1)
    )
    return coordinator, store, CalendarSource(hass, coordinator, settings), events


def _calendar_tasks(store: ChoreFlowStore) -> list:
    return [i for i in store.task_instances.values() if i.source == TaskSource.CALENDAR]


async def test_all_day_event_creates_high_task_day_before(
    hass: HomeAssistant,
) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {"uid": "e1", "start": "2026-06-20", "end": "2026-06-21", "summary": "Restmüll"}
    )

    await calendar.async_sync()
    await hass.async_block_till_done()

    tasks = _calendar_tasks(store)
    assert len(tasks) == 1
    assert tasks[0].importance == Importance.HIGH
    assert tasks[0].due_date == date(2026, 6, 19)  # day before
    assert tasks[0].external_refs.calendar.entity_id == _CAL


async def test_non_matching_event_ignored_and_dedup(hass: HomeAssistant) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {"uid": "b1", "start": "2026-06-20", "end": "2026-06-21", "summary": "Biomüll"}
    )
    events.append(
        {"uid": "e1", "start": "2026-06-22", "end": "2026-06-23", "summary": "Restmüll"}
    )

    await calendar.async_sync()
    await calendar.async_sync()  # second run must not duplicate
    await hass.async_block_till_done()

    tasks = _calendar_tasks(store)
    assert len(tasks) == 1
    assert tasks[0].title == "Restmüll"


async def test_recurring_uid_creates_one_task_per_occurrence(
    hass: HomeAssistant,
) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.extend(
        [
            {
                "uid": "weekly-waste",
                "start": "2026-06-20",
                "end": "2026-06-21",
                "summary": "Restmüll",
            },
            {
                "uid": "weekly-waste",
                "start": "2026-06-27",
                "end": "2026-06-28",
                "summary": "Restmüll",
            },
        ]
    )

    await calendar.async_sync()
    await hass.async_block_till_done()

    tasks = _calendar_tasks(store)
    assert {task.due_date for task in tasks} == {
        date(2026, 6, 19),
        date(2026, 6, 26),
    }
    assert {task.external_refs.calendar.event_uid for task in tasks} == {
        "weekly-waste@2026-06-20",
        "weekly-waste@2026-06-27",
    }


async def test_completed_occurrence_does_not_suppress_later_occurrence(
    hass: HomeAssistant,
) -> None:
    coordinator, store, calendar, events = await _build(hass)
    events.append(
        {
            "uid": "weekly-waste",
            "start": "2026-06-20",
            "end": "2026-06-21",
            "summary": "Restmüll",
        }
    )
    await calendar.async_sync()
    first = _calendar_tasks(store)[0]
    await coordinator.async_complete_from_external(first.id, "calendar_test")

    events.append(
        {
            "uid": "weekly-waste",
            "start": "2026-06-27",
            "end": "2026-06-28",
            "summary": "Restmüll",
        }
    )
    await calendar.async_sync()
    await hass.async_block_till_done()

    tasks = _calendar_tasks(store)
    assert len(tasks) == 2
    assert {task.status for task in tasks} == {
        TaskStatus.COMPLETED,
        TaskStatus.OPEN,
    }
    assert {task.due_date for task in tasks} == {
        date(2026, 6, 19),
        date(2026, 6, 26),
    }


async def test_timed_event_ignored(hass: HomeAssistant) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {
            "uid": "t1",
            "start": "2026-06-20T08:00:00+02:00",
            "end": "2026-06-20T09:00:00+02:00",
            "summary": "Restmüll",
        }
    )
    await calendar.async_sync()
    await hass.async_block_till_done()
    assert _calendar_tasks(store) == []


async def test_changed_event_updates_task(hass: HomeAssistant) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {"uid": "e1", "start": "2026-06-20", "end": "2026-06-21", "summary": "Restmüll"}
    )
    await calendar.async_sync()
    await hass.async_block_till_done()
    task_id = _calendar_tasks(store)[0].id

    events[0]["start"] = "2026-06-25"
    await calendar.async_sync()
    await hass.async_block_till_done()

    tasks = _calendar_tasks(store)
    assert len(tasks) == 1
    assert tasks[0].id != task_id  # occurrence-specific identity follows the new date
    assert tasks[0].due_date == date(2026, 6, 24)


async def test_deleted_event_removes_open_task(hass: HomeAssistant) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {"uid": "e1", "start": "2026-06-20", "end": "2026-06-21", "summary": "Restmüll"}
    )
    await calendar.async_sync()
    await hass.async_block_till_done()
    assert len(_calendar_tasks(store)) == 1

    events.clear()
    await calendar.async_sync()
    await hass.async_block_till_done()

    assert all(t.status != TaskStatus.OPEN for t in _calendar_tasks(store))
    assert _calendar_tasks(store) == []  # open calendar task removed


async def test_unavailable_calendar_keeps_tasks(hass: HomeAssistant) -> None:
    _coord, store, calendar, events = await _build(hass)
    events.append(
        {"uid": "e1", "start": "2026-06-20", "end": "2026-06-21", "summary": "Restmüll"}
    )
    await calendar.async_sync()
    await hass.async_block_till_done()
    assert len(_calendar_tasks(store)) == 1

    hass.states.async_set(_CAL, "unavailable")
    await calendar.async_sync()
    await hass.async_block_till_done()

    # Task kept; repair issue raised.
    assert len(_calendar_tasks(store)) == 1
    registry = ir.async_get(hass)
    assert registry.async_get_issue(DOMAIN, f"calendar_unavailable_{_CAL}") is not None
