"""Builders for engine unit tests (kept HA-free)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.choreflow.models import (
    AssignmentMode,
    Importance,
    RecurrenceType,
    TaskInstance,
    TaskRule,
    TaskSource,
    TaskStatus,
    UrgencyType,
    VisibilityMode,
)

FIXED_NOW = datetime(2026, 6, 18, 17, 30, tzinfo=UTC)


def config_entry_data(
    person: str = "person.niklas",
    notify: str = "notify.mobile_app_niklas",
) -> dict:
    """Minimal-but-complete config entry data for HA setup tests."""
    return {
        "name": "Home",
        "enabled_persons": [person],
        "person_settings": {
            person: {
                "notify_service": notify,
                "presence_required": True,
                "weekday_push_enabled": True,
                "weekend_push_enabled": True,
            }
        },
        "weekday_start_time": "17:30",
        "weekend_start_time": "10:00",
        "day_end_time": "20:00",
        "max_tasks_per_person_per_day": 5,
        "todo_sync": {"enabled": False},
        "calendar_sources": [],
    }


def make_rule(
    rule_id: str,
    *,
    title: str | None = None,
    room: str = "Bad",
    category: str = "Putzen",
    importance: Importance = Importance.NORMAL,
    estimated_duration_minutes: int | None = None,
    recurrence_type: RecurrenceType = RecurrenceType.EVERY_N_DAYS,
    recurrence_interval: int | None = 3,
    recurrence_weekdays: list[int] | None = None,
    created_date: date | None = None,
    last_completed_date: date | None = None,
    deadline: date | None = None,
    urgency_type: UrgencyType | None = None,
    visibility_mode: VisibilityMode = VisibilityMode.ALL_ENABLED_PERSONS,
    visibility_persons: list[str] | None = None,
    assignment_mode: AssignmentMode = AssignmentMode.RANDOM,
    assignment_person: str | None = None,
    enabled: bool = True,
) -> TaskRule:
    return TaskRule(
        id=rule_id,
        title=title or rule_id,
        description=None,
        room=room,
        category=category,
        importance=importance,
        estimated_duration_minutes=estimated_duration_minutes,
        recurrence_type=recurrence_type,
        recurrence_interval=recurrence_interval,
        recurrence_weekdays=recurrence_weekdays,
        urgency_type=urgency_type,
        deadline=deadline,
        visibility_mode=visibility_mode,
        visibility_persons=visibility_persons or [],
        assignment_mode=assignment_mode,
        assignment_person=assignment_person,
        created_date=created_date,
        last_completed_date=last_completed_date,
        enabled=enabled,
    )


def make_instance(
    instance_id: str,
    *,
    rule_id: str | None = None,
    title: str | None = None,
    room: str = "Bad",
    category: str = "Putzen",
    importance: Importance = Importance.NORMAL,
    estimated_duration_minutes: int | None = None,
    urgency_type: UrgencyType | None = None,
    due_date: date | None = None,
    deadline: date | None = None,
    status: TaskStatus = TaskStatus.OPEN,
    source: TaskSource = TaskSource.RULE,
    visibility_mode: VisibilityMode = VisibilityMode.ALL_ENABLED_PERSONS,
    visibility_persons: list[str] | None = None,
    assignment_mode: AssignmentMode = AssignmentMode.RANDOM,
    assignment_person: str | None = None,
    created_at: datetime = FIXED_NOW,
    completed_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> TaskInstance:
    return TaskInstance(
        id=instance_id,
        rule_id=rule_id,
        title=title or instance_id,
        description=None,
        room=room,
        category=category,
        importance=importance,
        estimated_duration_minutes=estimated_duration_minutes,
        urgency_type=urgency_type,
        due_date=due_date,
        deadline=deadline,
        status=status,
        source=source,
        visibility_mode=visibility_mode,
        visibility_persons=visibility_persons or [],
        assignment_mode=assignment_mode,
        assignment_person=assignment_person,
        external_refs=None,
        created_at=created_at,
        completed_at=completed_at,
        deleted_at=deleted_at,
    )
