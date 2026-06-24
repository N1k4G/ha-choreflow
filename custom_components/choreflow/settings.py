"""Typed view over a config entry's merged data + options.

Options override the original config data (Pflichtenheft §5.5). This keeps the
rest of the integration free of raw dict access and default handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_CALENDAR_SOURCES,
    CONF_DAY_END_TIME,
    CONF_ENABLED_PERSONS,
    CONF_MAX_TASKS_PER_PERSON_PER_DAY,
    CONF_NAME,
    CONF_NOTIFY_SERVICE,
    CONF_PERSON_SETTINGS,
    CONF_PRESENCE_REQUIRED,
    CONF_SKIP_PUSH_AFTER_DAILY_COMPLETION,
    CONF_TODO_SYNC,
    CONF_WEEKDAY_PUSH_ENABLED,
    CONF_WEEKDAY_START_TIME,
    CONF_WEEKEND_PUSH_ENABLED,
    CONF_WEEKEND_START_TIME,
    DEFAULT_DAY_END_TIME,
    DEFAULT_MAX_TASKS_PER_PERSON_PER_DAY,
    DEFAULT_NAME,
    DEFAULT_PRESENCE_REQUIRED,
    DEFAULT_SKIP_PUSH_AFTER_DAILY_COMPLETION,
    DEFAULT_WEEKDAY_PUSH_ENABLED,
    DEFAULT_WEEKDAY_START_TIME,
    DEFAULT_WEEKEND_PUSH_ENABLED,
    DEFAULT_WEEKEND_START_TIME,
)
from .engine.scheduler import ScheduleConfig


@dataclass(frozen=True)
class PersonSettings:
    entity_id: str
    notify_service: str | None
    presence_required: bool
    weekday_push_enabled: bool
    weekend_push_enabled: bool


@dataclass(frozen=True)
class ChoreFlowSettings:
    name: str
    enabled_persons: list[str]
    person_settings: dict[str, PersonSettings]
    schedule: ScheduleConfig
    max_tasks_per_person_per_day: int
    skip_push_after_daily_completion: bool = DEFAULT_SKIP_PUSH_AFTER_DAILY_COMPLETION
    todo: dict[str, Any] = field(default_factory=dict)
    calendar_sources: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_entry(cls, entry: ConfigEntry) -> ChoreFlowSettings:
        merged: dict[str, Any] = {**entry.data, **entry.options}

        persons: list[str] = list(merged.get(CONF_ENABLED_PERSONS, []))
        raw_person_settings: dict[str, Any] = merged.get(CONF_PERSON_SETTINGS, {})
        person_settings = {
            person: PersonSettings(
                entity_id=person,
                notify_service=cfg.get(CONF_NOTIFY_SERVICE),
                presence_required=cfg.get(
                    CONF_PRESENCE_REQUIRED, DEFAULT_PRESENCE_REQUIRED
                ),
                weekday_push_enabled=cfg.get(
                    CONF_WEEKDAY_PUSH_ENABLED, DEFAULT_WEEKDAY_PUSH_ENABLED
                ),
                weekend_push_enabled=cfg.get(
                    CONF_WEEKEND_PUSH_ENABLED, DEFAULT_WEEKEND_PUSH_ENABLED
                ),
            )
            for person, cfg in raw_person_settings.items()
        }

        schedule = ScheduleConfig.from_strings(
            merged.get(CONF_WEEKDAY_START_TIME, DEFAULT_WEEKDAY_START_TIME),
            merged.get(CONF_WEEKEND_START_TIME, DEFAULT_WEEKEND_START_TIME),
            merged.get(CONF_DAY_END_TIME, DEFAULT_DAY_END_TIME),
        )

        return cls(
            name=merged.get(CONF_NAME, DEFAULT_NAME),
            enabled_persons=persons,
            person_settings=person_settings,
            schedule=schedule,
            max_tasks_per_person_per_day=merged.get(
                CONF_MAX_TASKS_PER_PERSON_PER_DAY,
                DEFAULT_MAX_TASKS_PER_PERSON_PER_DAY,
            ),
            skip_push_after_daily_completion=merged.get(
                CONF_SKIP_PUSH_AFTER_DAILY_COMPLETION,
                DEFAULT_SKIP_PUSH_AFTER_DAILY_COMPLETION,
            ),
            todo=dict(merged.get(CONF_TODO_SYNC, {})),
            calendar_sources=list(merged.get(CONF_CALENDAR_SOURCES, [])),
        )
