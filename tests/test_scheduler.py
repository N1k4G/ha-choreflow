"""Unit tests for engine/scheduler.py (Pflichtenheft §11.1)."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from custom_components.choreflow.engine.scheduler import (
    ScheduleConfig,
    is_after_day_end,
    is_weekend,
    is_within_window,
    push_enabled_for_day,
    should_catchup,
    should_start_chain,
    start_time_for,
)

_MON = date(2026, 6, 15)  # weekday 0
_SAT = date(2026, 6, 20)  # weekday 5
_CONFIG = ScheduleConfig.with_defaults()  # 17:30 / 10:00 / 20:00


def _at(day: date, t: time) -> datetime:
    return datetime.combine(day, t, tzinfo=UTC)


def test_is_weekend() -> None:
    assert is_weekend(_MON) is False
    assert is_weekend(_SAT) is True


def test_start_time_weekday_vs_weekend() -> None:
    assert start_time_for(_MON, _CONFIG) == time(17, 30)
    assert start_time_for(_SAT, _CONFIG) == time(10, 0)


def test_push_enabled_for_day() -> None:
    assert push_enabled_for_day(
        _MON, weekday_push_enabled=True, weekend_push_enabled=False
    )
    assert not push_enabled_for_day(
        _SAT, weekday_push_enabled=True, weekend_push_enabled=False
    )


def test_window_bounds_weekday() -> None:
    assert is_within_window(_at(_MON, time(17, 29)), _CONFIG) is False
    assert is_within_window(_at(_MON, time(17, 30)), _CONFIG) is True
    assert is_within_window(_at(_MON, time(20, 0)), _CONFIG) is True
    assert is_within_window(_at(_MON, time(20, 1)), _CONFIG) is False


def test_is_after_day_end() -> None:
    assert is_after_day_end(_at(_MON, time(20, 1)), _CONFIG) is True
    assert is_after_day_end(_at(_MON, time(19, 59)), _CONFIG) is False


def test_should_start_chain_happy_path() -> None:
    now = _at(_MON, time(17, 30))
    assert should_start_chain(
        now, _CONFIG, is_home=True, push_enabled_today=True, already_started=False
    )


def test_should_start_chain_guards() -> None:
    now = _at(_MON, time(17, 30))
    # Not home.
    assert not should_start_chain(
        now, _CONFIG, is_home=False, push_enabled_today=True, already_started=False
    )
    # Already started.
    assert not should_start_chain(
        now, _CONFIG, is_home=True, push_enabled_today=True, already_started=True
    )
    # Push disabled this day.
    assert not should_start_chain(
        now, _CONFIG, is_home=True, push_enabled_today=False, already_started=False
    )
    # Before start time.
    assert not should_start_chain(
        _at(_MON, time(17, 0)),
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        already_started=False,
    )


def test_no_start_after_day_end() -> None:
    assert not should_start_chain(
        _at(_MON, time(20, 30)),
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        already_started=False,
    )


def test_should_catchup_on_return_within_window() -> None:
    now = _at(_MON, time(19, 0))
    assert should_catchup(
        now,
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        started=False,
        pending_catchup=True,
    )


def test_no_catchup_when_not_pending_or_after_end() -> None:
    # Not pending.
    assert not should_catchup(
        _at(_MON, time(19, 0)),
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        started=False,
        pending_catchup=False,
    )
    # After day end.
    assert not should_catchup(
        _at(_MON, time(20, 30)),
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        started=False,
        pending_catchup=True,
    )
    # Already started.
    assert not should_catchup(
        _at(_MON, time(19, 0)),
        _CONFIG,
        is_home=True,
        push_enabled_today=True,
        started=True,
        pending_catchup=True,
    )
