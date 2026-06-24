"""Pure tests for the versioned dashboard task contract."""

from __future__ import annotations

from datetime import date, timedelta

from custom_components.choreflow.coordinator import (
    _ordered_open_tasks,
    task_payload,
    task_preview_payload,
)
from custom_components.choreflow.models import (
    AssignmentMode,
    VisibilityMode,
)

from .factories import make_instance


def test_open_task_order_keeps_future_tasks() -> None:
    today = date(2026, 6, 19)
    due = make_instance("due", due_date=today)
    undated = make_instance("undated")
    future = make_instance("future", due_date=today + timedelta(days=7))

    ordered = _ordered_open_tasks([future, undated, due], today)

    assert {task.id for task in ordered} == {"due", "undated", "future"}
    assert ordered[-1].id == "future"


def test_preview_payload_stays_compact() -> None:
    task = make_instance("task", estimated_duration_minutes=5)

    assert task_preview_payload(task) == {
        "task_id": "task",
        "title": "task",
        "room": "Bad",
        "category": "Putzen",
        "importance": "normal",
        "estimated_duration_minutes": 5,
        "due_date": None,
        "snooze_until": None,
    }


def test_full_payload_contains_filter_and_action_metadata() -> None:
    task = make_instance(
        "task",
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=["person.niklas"],
        assignment_mode=AssignmentMode.ASSIGNED,
        assignment_person="person.niklas",
    )

    payload = task_payload(task)

    assert payload["task_id"] == "task"
    assert payload["visibility_mode"] == "selected_persons"
    assert payload["visibility_persons"] == ["person.niklas"]
    assert payload["assignment_mode"] == "assigned"
    assert payload["assignment_person"] == "person.niklas"
