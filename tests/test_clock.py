"""Unit tests for engine/clock.py (Pflichtenheft §11.1)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.choreflow.engine.clock import Clock, FixedClock, SystemClock


def test_fixed_clock_now_and_today() -> None:
    clock = FixedClock(datetime(2026, 6, 18, 17, 30, tzinfo=UTC))
    assert clock.now() == datetime(2026, 6, 18, 17, 30, tzinfo=UTC)
    assert clock.today() == date(2026, 6, 18)


def test_fixed_clock_set_and_advance() -> None:
    clock = FixedClock(datetime(2026, 6, 18, 17, 30, tzinfo=UTC))
    clock.advance(hours=2, minutes=30)
    assert clock.now() == datetime(2026, 6, 18, 20, 0, tzinfo=UTC)
    clock.set(datetime(2026, 6, 19, 10, 0, tzinfo=UTC))
    assert clock.today() == date(2026, 6, 19)


def test_clocks_satisfy_protocol() -> None:
    assert isinstance(FixedClock(datetime(2026, 1, 1, tzinfo=UTC)), Clock)
    assert isinstance(SystemClock(), Clock)
