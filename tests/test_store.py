"""HA Store round-trip tests for ChoreFlowStore (Pflichtenheft §3.2, P1)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from homeassistant.core import HomeAssistant

from custom_components.choreflow.models import (
    AssignmentMode,
    Importance,
    PushChainState,
    RecurrenceType,
    Reservation,
    TaskInstance,
    TaskRule,
    TaskSource,
    TaskStatus,
    VisibilityMode,
)
from custom_components.choreflow.store import ChoreFlowStore

_TZ = UTC


def _sample_rule() -> TaskRule:
    return TaskRule(
        id="clean_bathroom_sink",
        title="Waschbecken wischen",
        description=None,
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
    )


def _sample_instance() -> TaskInstance:
    return TaskInstance(
        id="inst_2026_06_18_clean_bathroom_sink",
        rule_id="clean_bathroom_sink",
        title="Waschbecken wischen",
        description=None,
        room="Bad",
        category="Putzen",
        importance=Importance.NORMAL,
        estimated_duration_minutes=5,
        urgency_type=None,
        due_date=date(2026, 6, 18),
        deadline=None,
        status=TaskStatus.OPEN,
        source=TaskSource.RULE,
        visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
        visibility_persons=[],
        assignment_mode=AssignmentMode.RANDOM,
        assignment_person=None,
        external_refs=None,
        created_at=datetime(2026, 6, 18, 17, 30, tzinfo=_TZ),
    )


async def test_store_save_and_reload(hass: HomeAssistant) -> None:
    """State written by one store instance is restored by a fresh one."""
    store = ChoreFlowStore(hass, "entry1")
    rule = _sample_rule()
    instance = _sample_instance()
    chain = PushChainState(person_entity="person.niklas", date=date(2026, 6, 18))
    reservation = Reservation(
        task_id=instance.id,
        person_entity="person.niklas",
        reserved_at=datetime(2026, 6, 18, 17, 31, tzinfo=_TZ),
    )

    store.task_rules[rule.id] = rule
    store.task_instances[instance.id] = instance
    store.push_chain_states[chain.key] = chain
    store.reservations.append(reservation)
    store.sync_state = {"todo.haushalt": {"seen": ["abc123"]}}
    store.calendar_state = {"calendar.abfuhr|evt-9|waste": instance.id}

    await store.async_save()

    reloaded = ChoreFlowStore(hass, "entry1")
    await reloaded.async_load()

    assert reloaded.task_rules == {rule.id: rule}
    assert reloaded.task_instances == {instance.id: instance}
    assert reloaded.push_chain_states == {chain.key: chain}
    assert reloaded.reservations == [reservation]
    assert reloaded.sync_state == {"todo.haushalt": {"seen": ["abc123"]}}
    assert reloaded.calendar_state == {"calendar.abfuhr|evt-9|waste": instance.id}


async def test_store_load_empty(hass: HomeAssistant) -> None:
    """Loading with nothing persisted yields empty collections."""
    store = ChoreFlowStore(hass, "entry_empty")
    await store.async_load()
    assert store.task_rules == {}
    assert store.task_instances == {}
    assert store.push_chain_states == {}
    assert store.reservations == []
