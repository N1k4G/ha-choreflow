"""Data models for ChoreFlow (Pflichtenheft §2).

Pure data structures: dataclasses and ``StrEnum``s plus JSON-friendly
serialisation. This module must stay free of any ``homeassistant`` import
(except typing) so it — and the engine built on top of it — is unit-testable
without a running Home Assistant (Pflichtenheft §1.2, Leitplanke 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any


# ---------------------------------------------------------------------------
# Enums (§2.1)
# ---------------------------------------------------------------------------
class Importance(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class UrgencyType(StrEnum):
    MANDATORY_DATE = "mandatory_date"
    DEADLINE = "deadline"


class TaskStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"
    DELETED = "deleted"


class TaskSource(StrEnum):
    RULE = "rule"
    DASHBOARD = "dashboard"
    TODO_SYNC = "todo_sync"
    CALENDAR = "calendar"
    MANUAL = "manual"


class AssignmentMode(StrEnum):
    ASSIGNED = "assigned"
    RANDOM = "random"


class VisibilityMode(StrEnum):
    ALL_ENABLED_PERSONS = "all_enabled_persons"
    SELECTED_PERSONS = "selected_persons"


class RecurrenceType(StrEnum):
    EVERY_N_DAYS = "every_n_days"
    WEEKDAYS = "weekdays"
    ONCE = "once"


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------
def _date_to_iso(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _date_from_iso(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _dt_to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _dt_from_iso(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


# ---------------------------------------------------------------------------
# External references (§2.4)
# ---------------------------------------------------------------------------
@dataclass
class TodoRef:
    entity_id: str
    item_uid: str

    def to_dict(self) -> dict[str, Any]:
        return {"entity_id": self.entity_id, "item_uid": self.item_uid}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TodoRef:
        return cls(entity_id=data["entity_id"], item_uid=data["item_uid"])


@dataclass
class CalendarRef:
    entity_id: str
    event_uid: str
    task_rule_id: str  # part of the dedup key (§7, Lastenheft §23.5)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "event_uid": self.event_uid,
            "task_rule_id": self.task_rule_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalendarRef:
        return cls(
            entity_id=data["entity_id"],
            event_uid=data["event_uid"],
            task_rule_id=data["task_rule_id"],
        )

    @property
    def dedup_key(self) -> str:
        """Stable external reference used to avoid duplicate calendar tasks."""
        return f"{self.entity_id}|{self.event_uid}|{self.task_rule_id}"


@dataclass
class ExternalRefs:
    todo: TodoRef | None = None
    calendar: CalendarRef | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "todo": self.todo.to_dict() if self.todo else None,
            "calendar": self.calendar.to_dict() if self.calendar else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExternalRefs:
        todo = data.get("todo")
        calendar = data.get("calendar")
        return cls(
            todo=TodoRef.from_dict(todo) if todo else None,
            calendar=CalendarRef.from_dict(calendar) if calendar else None,
        )


# ---------------------------------------------------------------------------
# Task rule (§2.2)
# ---------------------------------------------------------------------------
@dataclass
class TaskRule:
    id: str
    title: str
    description: str | None
    room: str
    category: str
    importance: Importance
    estimated_duration_minutes: int | None
    recurrence_type: RecurrenceType
    recurrence_interval: int | None
    recurrence_weekdays: list[int] | None  # 0=Mon .. 6=Sun
    urgency_type: UrgencyType | None
    deadline: date | None
    visibility_mode: VisibilityMode
    visibility_persons: list[str]
    assignment_mode: AssignmentMode
    assignment_person: str | None
    # Annahme: §4.2 needs an anchor ("Regel-Erstelldatum") for every_n_days
    # recurrence; §2.2 does not list it, so we add it here with a None default.
    # The recurrence engine falls back to this when no completion exists yet.
    created_date: date | None = None
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "room": self.room,
            "category": self.category,
            "importance": self.importance.value,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "recurrence_type": self.recurrence_type.value,
            "recurrence_interval": self.recurrence_interval,
            "recurrence_weekdays": self.recurrence_weekdays,
            "urgency_type": self.urgency_type.value if self.urgency_type else None,
            "deadline": _date_to_iso(self.deadline),
            "visibility_mode": self.visibility_mode.value,
            "visibility_persons": list(self.visibility_persons),
            "assignment_mode": self.assignment_mode.value,
            "assignment_person": self.assignment_person,
            "created_date": _date_to_iso(self.created_date),
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskRule:
        urgency = data.get("urgency_type")
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            room=data["room"],
            category=data["category"],
            importance=Importance(data["importance"]),
            estimated_duration_minutes=data.get("estimated_duration_minutes"),
            recurrence_type=RecurrenceType(data["recurrence_type"]),
            recurrence_interval=data.get("recurrence_interval"),
            recurrence_weekdays=data.get("recurrence_weekdays"),
            urgency_type=UrgencyType(urgency) if urgency else None,
            deadline=_date_from_iso(data.get("deadline")),
            visibility_mode=VisibilityMode(data["visibility_mode"]),
            visibility_persons=list(data.get("visibility_persons", [])),
            assignment_mode=AssignmentMode(data["assignment_mode"]),
            assignment_person=data.get("assignment_person"),
            created_date=_date_from_iso(data.get("created_date")),
            enabled=data.get("enabled", True),
        )


# ---------------------------------------------------------------------------
# Task instance (§2.3)
# ---------------------------------------------------------------------------
@dataclass
class TaskInstance:
    id: str
    rule_id: str | None
    title: str
    description: str | None
    room: str
    category: str
    importance: Importance
    urgency_type: UrgencyType | None
    due_date: date | None
    deadline: date | None
    status: TaskStatus
    source: TaskSource
    visibility_mode: VisibilityMode
    visibility_persons: list[str]
    assignment_mode: AssignmentMode
    assignment_person: str | None
    external_refs: ExternalRefs | None
    created_at: datetime
    estimated_duration_minutes: int | None = None
    completed_at: datetime | None = None
    completed_by: str | None = None
    completion_source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "room": self.room,
            "category": self.category,
            "importance": self.importance.value,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "urgency_type": self.urgency_type.value if self.urgency_type else None,
            "due_date": _date_to_iso(self.due_date),
            "deadline": _date_to_iso(self.deadline),
            "status": self.status.value,
            "source": self.source.value,
            "visibility_mode": self.visibility_mode.value,
            "visibility_persons": list(self.visibility_persons),
            "assignment_mode": self.assignment_mode.value,
            "assignment_person": self.assignment_person,
            "external_refs": (
                self.external_refs.to_dict() if self.external_refs else None
            ),
            "created_at": _dt_to_iso(self.created_at),
            "completed_at": _dt_to_iso(self.completed_at),
            "completed_by": self.completed_by,
            "completion_source": self.completion_source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskInstance:
        urgency = data.get("urgency_type")
        refs = data.get("external_refs")
        created_at = _dt_from_iso(data.get("created_at"))
        if created_at is None:
            raise ValueError("TaskInstance requires created_at")
        return cls(
            id=data["id"],
            rule_id=data.get("rule_id"),
            title=data["title"],
            description=data.get("description"),
            room=data["room"],
            category=data["category"],
            importance=Importance(data["importance"]),
            estimated_duration_minutes=data.get("estimated_duration_minutes"),
            urgency_type=UrgencyType(urgency) if urgency else None,
            due_date=_date_from_iso(data.get("due_date")),
            deadline=_date_from_iso(data.get("deadline")),
            status=TaskStatus(data["status"]),
            source=TaskSource(data["source"]),
            visibility_mode=VisibilityMode(data["visibility_mode"]),
            visibility_persons=list(data.get("visibility_persons", [])),
            assignment_mode=AssignmentMode(data["assignment_mode"]),
            assignment_person=data.get("assignment_person"),
            external_refs=ExternalRefs.from_dict(refs) if refs else None,
            created_at=created_at,
            completed_at=_dt_from_iso(data.get("completed_at")),
            completed_by=data.get("completed_by"),
            completion_source=data.get("completion_source"),
        )


# ---------------------------------------------------------------------------
# Push chain state (§2.5) — runtime, per person and day
# ---------------------------------------------------------------------------
@dataclass
class PushChainState:
    person_entity: str
    date: date
    active: bool = False
    started: bool = False
    pending_catchup: bool = False
    tasks_sent_count: int = 0
    current_task_id: str | None = None
    last_room: str | None = None
    sent_task_ids: list[str] = field(default_factory=list)
    ended_reason: str | None = (
        None  # snooze | left_home | no_tasks | limit | window_end
    )

    @property
    def key(self) -> str:
        """Composite key used to store one chain per person and day."""
        return f"{self.person_entity}|{self.date.isoformat()}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_entity": self.person_entity,
            "date": self.date.isoformat(),
            "active": self.active,
            "started": self.started,
            "pending_catchup": self.pending_catchup,
            "tasks_sent_count": self.tasks_sent_count,
            "current_task_id": self.current_task_id,
            "last_room": self.last_room,
            "sent_task_ids": list(self.sent_task_ids),
            "ended_reason": self.ended_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PushChainState:
        chain_date = _date_from_iso(data["date"])
        if chain_date is None:
            raise ValueError("PushChainState requires date")
        return cls(
            person_entity=data["person_entity"],
            date=chain_date,
            active=data.get("active", False),
            started=data.get("started", False),
            pending_catchup=data.get("pending_catchup", False),
            tasks_sent_count=data.get("tasks_sent_count", 0),
            current_task_id=data.get("current_task_id"),
            last_room=data.get("last_room"),
            sent_task_ids=list(data.get("sent_task_ids", [])),
            ended_reason=data.get("ended_reason"),
        )


# ---------------------------------------------------------------------------
# Reservation (§2.6) — runtime
# ---------------------------------------------------------------------------
@dataclass
class Reservation:
    task_id: str
    person_entity: str
    reserved_at: datetime
    # Time-critical high tasks on the last relevant day may be reserved in
    # parallel by several present persons (§4.4).
    exclusive: bool = True

    @property
    def key(self) -> str:
        """Composite key — high tasks allow several persons per task."""
        return f"{self.task_id}|{self.person_entity}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "person_entity": self.person_entity,
            "reserved_at": self.reserved_at.isoformat(),
            "exclusive": self.exclusive,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reservation:
        reserved_at = _dt_from_iso(data["reserved_at"])
        if reserved_at is None:
            raise ValueError("Reservation requires reserved_at")
        return cls(
            task_id=data["task_id"],
            person_entity=data["person_entity"],
            reserved_at=reserved_at,
            exclusive=data.get("exclusive", True),
        )


# ---------------------------------------------------------------------------
# Log event (§3.3, Lastenheft §17.2) — persisted to SQLite
# ---------------------------------------------------------------------------
@dataclass
class LogEvent:
    event_id: str
    event_type: str
    timestamp: datetime
    task_id: str | None = None
    task_rule_id: str | None = None
    title: str | None = None
    room: str | None = None
    category: str | None = None
    importance: str | None = None
    person_entity: str | None = None
    source: str | None = None
    completion_source: str | None = None
    overdue_days_at_completion: int | None = None
    decision_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "task_rule_id": self.task_rule_id,
            "title": self.title,
            "room": self.room,
            "category": self.category,
            "importance": self.importance,
            "person_entity": self.person_entity,
            "source": self.source,
            "completion_source": self.completion_source,
            "overdue_days_at_completion": self.overdue_days_at_completion,
            "decision_reason": self.decision_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogEvent:
        timestamp = _dt_from_iso(data["timestamp"])
        if timestamp is None:
            raise ValueError("LogEvent requires timestamp")
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            timestamp=timestamp,
            task_id=data.get("task_id"),
            task_rule_id=data.get("task_rule_id"),
            title=data.get("title"),
            room=data.get("room"),
            category=data.get("category"),
            importance=data.get("importance"),
            person_entity=data.get("person_entity"),
            source=data.get("source"),
            completion_source=data.get("completion_source"),
            overdue_days_at_completion=data.get("overdue_days_at_completion"),
            decision_reason=data.get("decision_reason"),
        )
