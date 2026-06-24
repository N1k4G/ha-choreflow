"""Unit tests for engine/selector.py (Pflichtenheft §11.1)."""

from __future__ import annotations

from datetime import date
from random import Random

from custom_components.choreflow.const import HIGH_FORCE_AFTER_SKIPPED
from custom_components.choreflow.engine.selector import (
    PersonContext,
    build_urgency_pool,
    is_suitable,
    pick_first,
    pick_next,
    score,
    top_pool_for_person,
)
from custom_components.choreflow.models import (
    AssignmentMode,
    Importance,
    TaskStatus,
    VisibilityMode,
)

from .factories import make_instance

_TODAY = date(2026, 6, 18)


# -- pool building & scoring -------------------------------------------------
def test_pool_excludes_non_open_and_future() -> None:
    open_due = make_instance("a", due_date=_TODAY)
    completed = make_instance("b", due_date=_TODAY, status=TaskStatus.COMPLETED)
    future = make_instance("c", due_date=date(2026, 6, 20))
    no_due = make_instance("d", due_date=None)
    pool = build_urgency_pool([open_due, completed, future, no_due], _TODAY)
    assert {i.id for i in pool} == {"a", "d"}


def test_high_outranks_normal_even_when_normal_is_overdue() -> None:
    high_today = make_instance("h", importance=Importance.HIGH, due_date=_TODAY)
    normal_overdue = make_instance(
        "n", importance=Importance.NORMAL, due_date=date(2026, 5, 1)
    )
    pool = build_urgency_pool([normal_overdue, high_today], _TODAY)
    assert pool[0].id == "h"


def test_overdue_increases_score() -> None:
    fresh = make_instance("f", due_date=_TODAY)
    overdue = make_instance("o", due_date=date(2026, 6, 10))
    assert score(overdue, _TODAY, {}) > score(fresh, _TODAY, {})


def test_recent_push_decreases_score() -> None:
    inst = make_instance("x", due_date=_TODAY)
    assert score(inst, _TODAY, {"x": 3}) < score(inst, _TODAY, {})


# -- suitability -------------------------------------------------------------
def test_suitability_visibility_selected() -> None:
    inst = make_instance(
        "s",
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=["person.a"],
    )
    assert is_suitable(inst, PersonContext("person.a"))
    assert not is_suitable(inst, PersonContext("person.b"))


def test_suitability_assigned_person() -> None:
    inst = make_instance(
        "s", assignment_mode=AssignmentMode.ASSIGNED, assignment_person="person.a"
    )
    assert is_suitable(inst, PersonContext("person.a"))
    assert not is_suitable(inst, PersonContext("person.b"))


def test_suitability_excluded_by_reservation() -> None:
    inst = make_instance("s")
    ctx = PersonContext("person.a", excluded_task_ids={"s"})
    assert not is_suitable(inst, ctx)


def test_top_pool_limit_and_capacity() -> None:
    pool = [make_instance(f"i{n}", due_date=_TODAY) for n in range(8)]
    ctx = PersonContext("person.a")
    assert len(top_pool_for_person(pool, ctx)) == 5
    no_capacity = PersonContext("person.a", has_capacity=False)
    assert top_pool_for_person(pool, no_capacity) == []


# -- pick_first --------------------------------------------------------------
def test_pick_first_empty() -> None:
    assert pick_first([], Random(1)) is None


def test_pick_first_is_deterministic_for_seed() -> None:
    pool = [make_instance(f"i{n}", due_date=_TODAY) for n in range(5)]
    seq_a = [pick_first(pool, Random(42)).id for _ in range(3)]
    seq_b = [pick_first(pool, Random(42)).id for _ in range(3)]
    assert seq_a == seq_b


def test_pick_first_prefers_high() -> None:
    pool = [
        make_instance("high", importance=Importance.HIGH, due_date=_TODAY),
        *[make_instance(f"n{n}", due_date=_TODAY) for n in range(4)],
    ]
    rng = Random(7)
    picks = [pick_first(pool, rng).id for _ in range(200)]
    assert picks.count("high") > 100  # weighted strongly toward high


# -- pick_next ---------------------------------------------------------------
def test_pick_next_bundles_by_room() -> None:
    pool = [
        make_instance("kitchen1", room="Küche", due_date=_TODAY),
        make_instance("bath1", room="Bad", due_date=_TODAY),
    ]
    # Sorted pool; last room was Bad → prefer the Bad task even if not first.
    picked = pick_next(pool, "Bad", Random(1))
    assert picked.id == "bath1"


def test_pick_next_high_forced_over_room_bundling() -> None:
    high = make_instance("high", importance=Importance.HIGH, due_date=_TODAY)
    bath = make_instance("bath", room="Bad", due_date=_TODAY)
    pool = build_urgency_pool([bath, high], _TODAY)
    skips = {"high": HIGH_FORCE_AFTER_SKIPPED}
    # Even though last room is Bad, the starved high task is forced.
    assert pick_next(pool, "Bad", Random(1), skips).id == "high"


def test_pick_next_falls_back_to_rotation() -> None:
    pool = [
        make_instance("a", room="Bad", due_date=_TODAY),
        make_instance("b", room="Bad", due_date=_TODAY),
    ]
    # No task in last_room "Flur" → soft rotation returns a pool member.
    picked = pick_next(pool, "Flur", Random(3))
    assert picked.id in {"a", "b"}


def test_pick_next_empty() -> None:
    assert pick_next([], "Bad", Random(1)) is None
