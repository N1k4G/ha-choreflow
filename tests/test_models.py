"""Pure round-trip serialisation tests for models.py (Pflichtenheft §11, P1)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from custom_components.choreflow.models import (
    AssignmentMode,
    CalendarRef,
    ExternalRefs,
    Importance,
    LogEvent,
    PushChainState,
    RecurrenceType,
    Reservation,
    TaskInstance,
    TaskRule,
    TaskSource,
    TaskStatus,
    TodoRef,
    UrgencyType,
    VisibilityMode,
)

_TZ = UTC


def test_task_rule_round_trip_full() -> None:
    rule = TaskRule(
        id="clean_bathroom_sink",
        title="Waschbecken wischen",
        description="kurz auswischen",
        room="Bad",
        category="Putzen",
        importance=Importance.NORMAL,
        estimated_duration_minutes=5,
        recurrence_type=RecurrenceType.EVERY_N_DAYS,
        recurrence_interval=3,
        recurrence_weekdays=None,
        urgency_type=None,
        deadline=None,
        visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
        visibility_persons=[],
        assignment_mode=AssignmentMode.RANDOM,
        assignment_person=None,
        created_date=date(2026, 6, 18),
        enabled=True,
    )
    assert TaskRule.from_dict(rule.to_dict()) == rule


def test_task_rule_round_trip_weekdays_and_deadline() -> None:
    rule = TaskRule(
        id="take_meds",
        title="Tabletten",
        description=None,
        room="Allgemein",
        category="Gesundheit",
        importance=Importance.HIGH,
        estimated_duration_minutes=None,
        recurrence_type=RecurrenceType.WEEKDAYS,
        recurrence_interval=None,
        recurrence_weekdays=[0, 2, 4],
        urgency_type=UrgencyType.DEADLINE,
        deadline=date(2026, 7, 1),
        visibility_mode=VisibilityMode.SELECTED_PERSONS,
        visibility_persons=["person.niklas"],
        assignment_mode=AssignmentMode.ASSIGNED,
        assignment_person="person.niklas",
    )
    restored = TaskRule.from_dict(rule.to_dict())
    assert restored == rule
    assert restored.recurrence_weekdays == [0, 2, 4]
    assert restored.enabled is True  # default applied


def test_task_instance_round_trip_with_external_refs() -> None:
    instance = TaskInstance(
        id="inst_2026_06_18_clean_bathroom_sink",
        rule_id="clean_bathroom_sink",
        title="Waschbecken wischen",
        description=None,
        room="Bad",
        category="Putzen",
        importance=Importance.NORMAL,
        urgency_type=None,
        due_date=date(2026, 6, 18),
        deadline=None,
        status=TaskStatus.OPEN,
        source=TaskSource.RULE,
        visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
        visibility_persons=[],
        assignment_mode=AssignmentMode.RANDOM,
        assignment_person=None,
        external_refs=ExternalRefs(
            todo=TodoRef(entity_id="todo.haushalt", item_uid="abc123"),
            calendar=CalendarRef(
                entity_id="calendar.abfuhr",
                event_uid="evt-9",
                task_rule_id="take_out_residual_waste",
            ),
        ),
        created_at=datetime(2026, 6, 18, 17, 30, tzinfo=_TZ),
        completed_at=datetime(2026, 6, 18, 17, 42, tzinfo=_TZ),
        completed_by="person.niklas",
        completion_source="push",
    )
    restored = TaskInstance.from_dict(instance.to_dict())
    assert restored == instance
    assert restored.external_refs is not None
    assert restored.external_refs.calendar is not None
    assert (
        restored.external_refs.calendar.dedup_key
        == "calendar.abfuhr|evt-9|take_out_residual_waste"
    )


def test_task_instance_round_trip_minimal_open() -> None:
    instance = TaskInstance(
        id="task_kellerregal",
        rule_id=None,
        title="Kellerregal ausmessen",
        description=None,
        room="Keller",
        category="Organisation",
        importance=Importance.NORMAL,
        urgency_type=None,
        due_date=None,
        deadline=None,
        status=TaskStatus.OPEN,
        source=TaskSource.TODO_SYNC,
        visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
        visibility_persons=[],
        assignment_mode=AssignmentMode.RANDOM,
        assignment_person=None,
        external_refs=None,
        created_at=datetime(2026, 6, 18, 9, 0, tzinfo=_TZ),
    )
    restored = TaskInstance.from_dict(instance.to_dict())
    assert restored == instance
    assert restored.completed_at is None
    assert restored.external_refs is None


def test_push_chain_state_round_trip_and_key() -> None:
    chain = PushChainState(
        person_entity="person.niklas",
        date=date(2026, 6, 18),
        active=True,
        started=True,
        pending_catchup=False,
        tasks_sent_count=2,
        current_task_id="inst_x",
        last_room="Bad",
        sent_task_ids=["inst_a", "inst_b"],
        ended_reason=None,
    )
    restored = PushChainState.from_dict(chain.to_dict())
    assert restored == chain
    assert restored.key == "person.niklas|2026-06-18"


def test_reservation_round_trip_and_key() -> None:
    reservation = Reservation(
        task_id="inst_x",
        person_entity="person.niklas",
        reserved_at=datetime(2026, 6, 18, 17, 30, tzinfo=_TZ),
        exclusive=False,
    )
    restored = Reservation.from_dict(reservation.to_dict())
    assert restored == reservation
    assert restored.key == "inst_x|person.niklas"


def test_log_event_round_trip() -> None:
    event = LogEvent(
        event_id="evt_2026_06_18_174200_ab12cd",
        event_type="task_completed",
        timestamp=datetime(2026, 6, 18, 17, 42, tzinfo=_TZ),
        task_id="inst_2026_06_18_clean_bathroom_sink",
        task_rule_id="clean_bathroom_sink",
        title="Waschbecken wischen",
        room="Bad",
        category="Putzen",
        importance="normal",
        person_entity="person.niklas",
        source="push_action",
        completion_source="push",
        overdue_days_at_completion=0,
        decision_reason="picked: highest score in top-5",
    )
    assert LogEvent.from_dict(event.to_dict()) == event
