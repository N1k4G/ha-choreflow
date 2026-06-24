"""Unit tests for engine/recurrence.py (Pflichtenheft §11.1)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.choreflow.engine.recurrence import (
    due_instances_for,
    instance_id_for,
)
from custom_components.choreflow.models import (
    RecurrenceType,
    TaskSource,
    TaskStatus,
)

from .factories import make_instance, make_rule

_NOW = datetime(2026, 6, 18, 12, 0, tzinfo=UTC)
_MON = date(2026, 6, 15)  # Monday (weekday 0)


def _ids(rules, on_date, existing=None):
    return [i.id for i in due_instances_for(rules, on_date, existing or [], _NOW)]


def test_instance_id_scheme() -> None:
    assert (
        instance_id_for("clean_bathroom_sink", date(2026, 6, 18))
        == "inst_2026_06_18_clean_bathroom_sink"
    )


def test_every_n_days_due_on_anchor_and_interval() -> None:
    rule = make_rule("r", recurrence_interval=3, created_date=_MON)
    assert _ids([rule], _MON) == ["inst_2026_06_15_r"]  # day 0
    assert _ids([rule], date(2026, 6, 18)) == ["inst_2026_06_18_r"]  # day 3
    assert _ids([rule], date(2026, 6, 16)) == []  # day 1
    assert _ids([rule], date(2026, 6, 17)) == []  # day 2


def test_every_n_days_anchor_moves_to_last_completion() -> None:
    rule = make_rule("r", recurrence_interval=3, created_date=_MON)
    # Completed on Tue 06-16 → next due is 06-19, not 06-18.
    completed = make_instance(
        "inst_old",
        rule_id="r",
        status=TaskStatus.COMPLETED,
        completed_at=datetime(2026, 6, 16, 18, 0, tzinfo=UTC),
    )
    assert _ids([rule], date(2026, 6, 18), [completed]) == []
    assert _ids([rule], date(2026, 6, 19), [completed]) == ["inst_2026_06_19_r"]


def test_weekdays_rule() -> None:
    rule = make_rule(
        "r",
        recurrence_type=RecurrenceType.WEEKDAYS,
        recurrence_interval=None,
        recurrence_weekdays=[0, 2],  # Mon, Wed
    )
    assert _ids([rule], _MON) == ["inst_2026_06_15_r"]  # Monday
    assert _ids([rule], date(2026, 6, 16)) == []  # Tuesday
    assert _ids([rule], date(2026, 6, 17)) == ["inst_2026_06_17_r"]  # Wednesday


def test_once_rule_never_recurs() -> None:
    rule = make_rule(
        "r",
        recurrence_type=RecurrenceType.ONCE,
        recurrence_interval=None,
        created_date=_MON,
    )
    assert _ids([rule], _MON) == []


def test_no_duplicate_for_existing_open_instance() -> None:
    rule = make_rule("r", recurrence_interval=1, created_date=_MON)
    existing = make_instance(
        instance_id_for("r", _MON),
        rule_id="r",
        due_date=_MON,
        status=TaskStatus.OPEN,
    )
    assert _ids([rule], _MON, [existing]) == []


def test_no_duplicate_for_completed_same_day() -> None:
    rule = make_rule("r", recurrence_interval=1, created_date=_MON)
    existing = make_instance(
        instance_id_for("r", _MON),
        rule_id="r",
        due_date=_MON,
        status=TaskStatus.COMPLETED,
        completed_at=datetime(2026, 6, 15, 18, 0, tzinfo=UTC),
    )
    # Completed today would re-anchor to today, but dedup prevents re-creation.
    assert _ids([rule], _MON, [existing]) == []


def test_disabled_rule_skipped() -> None:
    rule = make_rule("r", recurrence_interval=1, created_date=_MON, enabled=False)
    assert _ids([rule], _MON) == []


def test_generated_instance_fields() -> None:
    rule = make_rule("r", room="Küche", recurrence_interval=1, created_date=_MON)
    [inst] = due_instances_for([rule], _MON, [], _NOW)
    assert inst.rule_id == "r"
    assert inst.room == "Küche"
    assert inst.due_date == _MON
    assert inst.status == TaskStatus.OPEN
    assert inst.source == TaskSource.RULE
    assert inst.created_at == _NOW
