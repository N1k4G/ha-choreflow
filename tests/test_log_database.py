"""Pure SQLite tests for the LogStore core (Pflichtenheft §3.3/§3.4, P1).

Exercise :class:`LogDatabase` against an in-memory database — no Home Assistant
required.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from custom_components.choreflow.const import (
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EVENT_TASK_SNOOZED,
)
from custom_components.choreflow.models import LogEvent
from custom_components.choreflow.store import LogDatabase

_TZ = UTC


def _event(
    event_id: str,
    event_type: str,
    *,
    timestamp: datetime,
    person: str | None = None,
    room: str | None = None,
    category: str | None = None,
    importance: str | None = None,
    task_rule_id: str | None = None,
    task_id: str | None = None,
    completion_source: str | None = None,
    overdue_days: int | None = None,
) -> LogEvent:
    return LogEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=timestamp,
        person_entity=person,
        room=room,
        category=category,
        importance=importance,
        task_rule_id=task_rule_id,
        task_id=task_id,
        completion_source=completion_source,
        overdue_days_at_completion=overdue_days,
    )


@pytest.fixture
def db() -> Iterator[LogDatabase]:
    database = LogDatabase(":memory:")
    database.connect()
    yield database
    database.close()


def _seed(db: LogDatabase) -> None:
    db.insert(
        _event(
            "e1",
            EVENT_TASK_COMPLETED,
            timestamp=datetime(2026, 6, 18, 17, 42, tzinfo=_TZ),
            person="person.niklas",
            room="Bad",
            category="Putzen",
            importance="normal",
            task_rule_id="clean_bathroom_sink",
            completion_source="push",
            overdue_days=0,
        )
    )
    db.insert(
        _event(
            "e2",
            EVENT_TASK_COMPLETED,
            timestamp=datetime(2026, 6, 19, 10, 0, tzinfo=_TZ),
            person="person.niklas",
            room="Küche",
            category="Putzen",
            importance="high",
            task_rule_id="wipe_counter",
            completion_source="dashboard",
            overdue_days=2,
        )
    )
    db.insert(
        _event(
            "e3",
            EVENT_TASK_COMPLETED_FROM_TODO,
            timestamp=datetime(2026, 7, 1, 8, 0, tzinfo=_TZ),
            person="person.partner",
            room="Bad",
            category="Putzen",
            importance="high",
            task_rule_id="clean_bathroom_sink",
            completion_source="todo",
            overdue_days=0,
        )
    )
    db.insert(
        _event(
            "s1",
            EVENT_TASK_SNOOZED,
            timestamp=datetime(2026, 6, 18, 18, 0, tzinfo=_TZ),
            person="person.niklas",
            task_rule_id="clean_bathroom_sink",
        )
    )
    db.insert(
        _event(
            "s2",
            EVENT_TASK_SNOOZED,
            timestamp=datetime(2026, 6, 20, 18, 0, tzinfo=_TZ),
            person="person.niklas",
            task_rule_id="clean_bathroom_sink",
        )
    )


def test_insert_is_idempotent_on_event_id(db: LogDatabase) -> None:
    ev = _event(
        "dup",
        EVENT_TASK_COMPLETED,
        timestamp=datetime(2026, 6, 18, tzinfo=_TZ),
        person="person.niklas",
    )
    db.insert(ev)
    db.insert(ev)  # INSERT OR REPLACE — no duplicate row
    assert db.completed_count_by_person() == {"person.niklas": 1}


def test_completed_count_by_person(db: LogDatabase) -> None:
    _seed(db)
    assert db.completed_count_by_person() == {
        "person.niklas": 2,
        "person.partner": 1,
    }


def test_completed_count_by_room_and_category(db: LogDatabase) -> None:
    _seed(db)
    assert db.completed_count_by_room() == {"Bad": 2, "Küche": 1}
    assert db.completed_count_by_category() == {"Putzen": 3}


def test_completed_count_by_task(db: LogDatabase) -> None:
    _seed(db)
    assert db.completed_count_by_task() == {
        "clean_bathroom_sink": 2,
        "wipe_counter": 1,
    }


def test_snoozed_counts(db: LogDatabase) -> None:
    _seed(db)
    assert db.snoozed_count() == 2
    assert db.most_snoozed_tasks() == [("clean_bathroom_sink", 2)]


def test_completed_by_month_and_year(db: LogDatabase) -> None:
    _seed(db)
    # e1 (06-18) + e2 (06-19) → June; e3 (07-01) → July.
    assert db.completed_count_by_month() == {"2026-06": 2, "2026-07": 1}
    assert db.completed_count_by_year() == {"2026": 3}


def test_high_on_time_vs_overdue(db: LogDatabase) -> None:
    _seed(db)
    # e3 is high & on time; e2 is high but overdue → only e3 counts on time.
    assert db.high_completed_on_time_count() == 1
    # e2 completed while overdue (2 days).
    assert db.overdue_at_completion_count() == 1


def test_completion_source_distribution(db: LogDatabase) -> None:
    _seed(db)
    assert db.completion_source_distribution() == {
        "push": 1,
        "dashboard": 1,
        "todo": 1,
    }


def test_unsupported_group_column_rejected(db: LogDatabase) -> None:
    with pytest.raises(ValueError, match="Unsupported group column"):
        db._completed_group_count("title; DROP TABLE log_events")
