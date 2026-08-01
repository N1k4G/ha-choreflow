"""Service + notification-action wiring tests (Pflichtenheft §11.2, P3c).

Exercises the full entry setup so services and the bus listener are registered.
Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    ACTION_PREFIX_DONE,
    DATA_STORE,
    DOMAIN,
    EVENT_MOBILE_APP_NOTIFICATION_ACTION,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
    SERVICE_GET_HISTORY,
    SERVICE_GET_TASKS,
    SERVICE_UPDATE_TASK,
)
from custom_components.choreflow.models import (
    AssignmentMode,
    TaskStatus,
    VisibilityMode,
)
from custom_components.choreflow.notify import build_action_id
from custom_components.choreflow.services import _export_to_calendar

from .factories import config_entry_data, make_instance, make_rule

_PERSON = "person.niklas"


def _prereqs(hass: HomeAssistant) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _find_task_id(hass: HomeAssistant, entry: MockConfigEntry, title: str) -> str:
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    for inst in store.task_instances.values():
        if inst.title == title:
            return inst.id
    raise AssertionError(f"task {title!r} not found")


async def test_services_are_registered(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)
    for service in (
        "create_task",
        "update_task",
        "delete_task",
        "complete_task",
        "snooze_task",
        "start_daily_flow",
        "send_next_task",
        "get_tasks",
        "get_history",
    ):
        assert hass.services.has_service(DOMAIN, service)


async def test_create_and_complete_task_services(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_CREATE_TASK,
        {
            "title": "Wipe sink",
            "room": "Bad",
            "importance": "normal",
            "estimated_duration_minutes": 5,
        },
        blocking=True,
        return_response=True,
    )
    assert response is not None
    task_id = response["task_id"]

    await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_TASK,
        {"task_id": task_id, "estimated_duration_minutes": 8},
        blocking=True,
    )

    await hass.services.async_call(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        {"task_id": task_id, "person_entity": _PERSON, "source": "dashboard"},
        blocking=True,
    )
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    assert store.task_instances[task_id].status == TaskStatus.COMPLETED
    assert store.task_instances[task_id].completion_source == "dashboard"
    assert store.task_instances[task_id].estimated_duration_minutes == 8


async def test_create_task_exports_one_day_all_day_calendar_event(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)
    calendar_calls: list[dict] = []
    hass.services.async_register(
        "calendar",
        "create_event",
        lambda call: calendar_calls.append(dict(call.data)),
    )
    due = date(2026, 6, 20)

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_CREATE_TASK,
        {
            "title": "Take bins out",
            "room": "Outside",
            "category": "Waste",
            "due_date": due,
            "calendar_export_entity_id": "calendar.household",
        },
        blocking=True,
        return_response=True,
    )

    assert response is not None
    assert calendar_calls == [
        {
            "entity_id": "calendar.household",
            "summary": "Take bins out",
            "start_date": "2026-06-20",
            "end_date": "2026-06-21",
            "description": f"[ChoreFlow {response['task_id']}] Outside · Waste",
        }
    ]


async def test_calendar_export_normalizes_datetime_to_date(
    hass: HomeAssistant,
) -> None:
    calendar_calls: list[dict] = []
    hass.services.async_register(
        "calendar",
        "create_event",
        lambda call: calendar_calls.append(dict(call.data)),
    )

    await _export_to_calendar(
        hass,
        "calendar.household",
        {
            "title": "Take bins out",
            "due_date": datetime(2026, 6, 20, 18, 30, tzinfo=UTC),
        },
        "task-1",
    )

    assert calendar_calls[0]["start_date"] == "2026-06-20"
    assert calendar_calls[0]["end_date"] == "2026-06-21"


async def test_update_task_clears_nullable_fields(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    task = make_instance(
        "clear-fields",
        due_date=date.today() + timedelta(days=3),
        estimated_duration_minutes=15,
    )
    task.description = "Clean every surface"
    store.task_instances[task.id] = task

    await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_TASK,
        {
            "task_id": task.id,
            "description": None,
            "due_date": None,
            "estimated_duration_minutes": None,
        },
        blocking=True,
    )

    assert task.description is None
    assert task.due_date is None
    assert task.estimated_duration_minutes is None


async def test_update_task_omitted_due_date_is_unchanged(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    due_date = date.today() + timedelta(days=3)
    task = make_instance("keep-due-date", due_date=due_date)
    store.task_instances[task.id] = task

    await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_TASK,
        {"task_id": task.id, "title": "Updated title"},
        blocking=True,
    )

    assert task.title == "Updated title"
    assert task.due_date == due_date


async def test_update_rule_task_propagates_cleared_fields(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    rule = make_rule("rule-clear-fields", estimated_duration_minutes=20)
    rule.description = "Clean every surface"
    task = make_instance(
        "rule-task-clear-fields",
        rule_id=rule.id,
        estimated_duration_minutes=20,
    )
    task.description = rule.description
    store.task_rules[rule.id] = rule
    store.task_instances[task.id] = task

    await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_TASK,
        {
            "task_id": task.id,
            "description": None,
            "estimated_duration_minutes": None,
        },
        blocking=True,
    )

    assert task.description is None
    assert task.estimated_duration_minutes is None
    assert rule.description is None
    assert rule.estimated_duration_minutes is None


async def test_notification_action_completes_task(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CREATE_TASK,
        {"title": "Take out trash", "room": "Außenbereich"},
        blocking=True,
    )
    task_id = _find_task_id(hass, entry, "Take out trash")

    hass.bus.async_fire(
        EVENT_MOBILE_APP_NOTIFICATION_ACTION,
        {"action": build_action_id(ACTION_PREFIX_DONE, task_id, "niklas")},
    )
    await hass.async_block_till_done()

    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    assert store.task_instances[task_id].status == TaskStatus.COMPLETED
    assert store.task_instances[task_id].completion_source == "push"


async def test_get_tasks_filters_and_paginates(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    visible = make_instance("visible", room="Bad")
    selected = make_instance(
        "selected",
        room="Bad",
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=[_PERSON],
        assignment_mode=AssignmentMode.ASSIGNED,
        assignment_person=_PERSON,
    )
    hidden = make_instance(
        "hidden",
        room="Bad",
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=["person.partner"],
    )
    future = make_instance(
        "future",
        room="Bad",
        due_date=date.today() + timedelta(days=7),
    )
    for task in (visible, selected, hidden, future):
        store.task_instances[task.id] = task

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_TASKS,
        {
            "person_entity": _PERSON,
            "person_scope": "visible",
            "room": "Bad",
            "limit": 1,
            "offset": 0,
        },
        blocking=True,
        return_response=True,
    )
    assert response is not None
    assert response["api_version"] == 1
    assert response["total"] == 3
    assert response["has_more"] is True
    assert len(response["items"]) == 1
    assert "task_id" in response["items"][0]
    assert "snooze_until" in response["items"][0]

    assigned = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_TASKS,
        {
            "person_entity": _PERSON,
            "person_scope": "assigned",
        },
        blocking=True,
        return_response=True,
    )
    assert assigned is not None
    assert [item["task_id"] for item in assigned["items"]] == ["selected"]


async def test_get_history_returns_completed_tasks(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    task = make_instance("history-task", title="Wipe sink", room="Bad")
    store.task_instances[task.id] = task

    await hass.services.async_call(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        {"task_id": task.id, "person_entity": _PERSON, "source": "dashboard"},
        blocking=True,
    )
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_HISTORY,
        {"person_entity": _PERSON, "room": "Bad", "limit": 10},
        blocking=True,
        return_response=True,
    )
    assert response is not None
    assert response["total"] == 1
    assert response["has_more"] is False
    assert response["items"][0]["task_id"] == task.id
    assert response["items"][0]["title"] == "Wipe sink"


async def test_complete_rejects_task_hidden_from_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    task = make_instance(
        "hidden",
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=["person.partner"],
    )
    store.task_instances[task.id] = task

    with pytest.raises(ServiceValidationError, match="not visible"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_COMPLETE_TASK,
            {"task_id": task.id, "person_entity": _PERSON},
            blocking=True,
        )
    assert task.status == TaskStatus.OPEN


async def test_complete_rejects_task_assigned_to_another_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    task = make_instance(
        "assigned",
        assignment_mode=AssignmentMode.ASSIGNED,
        assignment_person="person.partner",
    )
    store.task_instances[task.id] = task

    with pytest.raises(ServiceValidationError, match="assigned to"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_COMPLETE_TASK,
            {"task_id": task.id, "person_entity": _PERSON},
            blocking=True,
        )
    assert task.status == TaskStatus.OPEN


async def test_create_rejects_incomplete_assignment(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)

    with pytest.raises(ServiceValidationError, match="assignment_person"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CREATE_TASK,
            {"title": "Assigned task", "assignment_mode": "assigned"},
            blocking=True,
        )


async def test_complete_rejects_unknown_task(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)

    with pytest.raises(ServiceValidationError, match="Unknown"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_COMPLETE_TASK,
            {"task_id": "missing", "person_entity": _PERSON},
            blocking=True,
        )
