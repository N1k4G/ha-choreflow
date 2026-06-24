"""Injectable time abstraction (Pflichtenheft §4.1).

The core logic never calls ``datetime.now()`` directly. It receives a
:class:`Clock`, so time windows are deterministic and testable via
:class:`FixedClock`. Production uses :class:`SystemClock`, which reads HA's
timezone-aware current time through a lazy import — keeping this module
importable without Home Assistant.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Provides the current time in the Home Assistant timezone."""

    def now(self) -> datetime: ...

    def today(self) -> date: ...


class SystemClock:
    """Production clock backed by Home Assistant's ``dt_util.now()``."""

    def now(self) -> datetime:
        # Lazy import keeps the engine package HA-free at module level.
        from homeassistant.util import dt as dt_util

        return dt_util.now()

    def today(self) -> date:
        return self.now().date()


class FixedClock:
    """Deterministic clock for tests; time only changes when you change it."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def today(self) -> date:
        return self._now.date()

    def set(self, now: datetime) -> None:
        """Jump to an absolute time."""
        self._now = now

    def advance(self, **delta: float) -> None:
        """Advance by a :class:`~datetime.timedelta` keyword delta."""
        self._now += timedelta(**delta)
