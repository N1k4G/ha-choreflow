"""Unit tests for engine/reservation.py (Pflichtenheft §11.1)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.choreflow.engine.reservation import (
    ReservationBook,
    allows_parallel,
    is_last_relevant_day,
    relevant_day,
)
from custom_components.choreflow.models import Importance

from .factories import make_instance

_NOW = datetime(2026, 6, 18, 17, 30, tzinfo=UTC)
_TODAY = date(2026, 6, 18)


def test_exclusive_reservation_blocks_others_only() -> None:
    book = ReservationBook()
    book.reserve("t1", "person.a", _NOW)
    assert book.is_reserved_for_other("t1", "person.b") is True
    assert book.is_reserved_for_other("t1", "person.a") is False
    assert book.excluded_task_ids_for("person.b") == {"t1"}
    assert book.excluded_task_ids_for("person.a") == set()


def test_reserve_is_idempotent_per_person() -> None:
    book = ReservationBook()
    book.reserve("t1", "person.a", _NOW)
    book.reserve("t1", "person.a", _NOW)
    assert len(book.items) == 1


def test_parallel_high_reservation_allowed() -> None:
    book = ReservationBook()
    book.reserve("t1", "person.a", _NOW, exclusive=False)
    book.reserve("t1", "person.b", _NOW, exclusive=False)
    # Non-exclusive → nobody is blocked.
    assert book.is_reserved_for_other("t1", "person.c") is False
    assert book.reserved_persons("t1") == {"person.a", "person.b"}


def test_release_paths() -> None:
    book = ReservationBook()
    book.reserve("t1", "person.a", _NOW)
    book.reserve("t1", "person.b", _NOW, exclusive=False)
    book.release_for_person("t1", "person.a")
    assert book.reserved_persons("t1") == {"person.b"}
    book.release("t1")
    assert book.items == []


def test_book_mutates_shared_list_in_place() -> None:
    backing: list = []
    book = ReservationBook(backing)
    book.reserve("t1", "person.a", _NOW)
    assert len(backing) == 1  # same list object → persistable by coordinator


def test_relevant_day_prefers_due_then_deadline() -> None:
    with_due = make_instance("a", due_date=_TODAY, deadline=date(2026, 7, 1))
    with_deadline = make_instance("b", due_date=None, deadline=date(2026, 7, 1))
    assert relevant_day(with_due) == _TODAY
    assert relevant_day(with_deadline) == date(2026, 7, 1)


def test_allows_parallel_only_for_high_on_last_day() -> None:
    high_today = make_instance("h", importance=Importance.HIGH, due_date=_TODAY)
    high_future = make_instance(
        "hf", importance=Importance.HIGH, due_date=date(2026, 6, 20)
    )
    normal_today = make_instance("n", importance=Importance.NORMAL, due_date=_TODAY)
    assert is_last_relevant_day(high_today, _TODAY) is True
    assert allows_parallel(high_today, _TODAY) is True
    assert allows_parallel(high_future, _TODAY) is False
    assert allows_parallel(normal_today, _TODAY) is False
