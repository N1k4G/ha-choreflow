"""Daily window, start times, catch-up and day end (Pflichtenheft §4.5).

Pure schedule arithmetic over an injected ``now`` (from the Clock). Start
times and the day-end come from :class:`ScheduleConfig` (defaults in §12:
weekdays 17:30, weekend 10:00, end 20:00). After the day end nothing starts or
continues (Lastenheft §12.1/AK-07).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

from ..const import (
    DEFAULT_DAY_END_TIME,
    DEFAULT_WEEKDAY_START_TIME,
    DEFAULT_WEEKEND_START_TIME,
)


def parse_hhmm(value: str) -> time:
    """Parse a ``"HH:MM"`` string into a :class:`~datetime.time`."""
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def is_weekend(day: date) -> bool:
    """Saturday or Sunday."""
    return day.weekday() >= 5


@dataclass(frozen=True)
class ScheduleConfig:
    weekday_start: time
    weekend_start: time
    day_end: time

    @classmethod
    def from_strings(
        cls, weekday_start: str, weekend_start: str, day_end: str
    ) -> ScheduleConfig:
        return cls(
            weekday_start=parse_hhmm(weekday_start),
            weekend_start=parse_hhmm(weekend_start),
            day_end=parse_hhmm(day_end),
        )

    @classmethod
    def with_defaults(cls) -> ScheduleConfig:
        return cls.from_strings(
            DEFAULT_WEEKDAY_START_TIME,
            DEFAULT_WEEKEND_START_TIME,
            DEFAULT_DAY_END_TIME,
        )


def start_time_for(day: date, config: ScheduleConfig) -> time:
    """Initial chain start time for the given day (§4.5)."""
    return config.weekend_start if is_weekend(day) else config.weekday_start


def push_enabled_for_day(
    day: date,
    *,
    weekday_push_enabled: bool,
    weekend_push_enabled: bool,
) -> bool:
    """Whether pushes are enabled for the person on this kind of day."""
    return weekend_push_enabled if is_weekend(day) else weekday_push_enabled


def is_within_window(now: datetime, config: ScheduleConfig) -> bool:
    """True between the day's start time and the day end (inclusive)."""
    start = start_time_for(now.date(), config)
    return start <= now.time() <= config.day_end


def is_after_day_end(now: datetime, config: ScheduleConfig) -> bool:
    """True once the daily window has closed (§4.5)."""
    return now.time() > config.day_end


def should_start_chain(
    now: datetime,
    config: ScheduleConfig,
    *,
    is_home: bool,
    push_enabled_today: bool,
    already_started: bool,
) -> bool:
    """Initial start: start time reached, person home, enabled, not started yet."""
    if already_started or not is_home or not push_enabled_today:
        return False
    return is_within_window(now, config)


def should_catchup(
    now: datetime,
    config: ScheduleConfig,
    *,
    is_home: bool,
    push_enabled_today: bool,
    started: bool,
    pending_catchup: bool,
) -> bool:
    """Catch-up: person absent at start returns home within the window (§4.5)."""
    if started or not pending_catchup or not is_home or not push_enabled_today:
        return False
    return is_within_window(now, config)
