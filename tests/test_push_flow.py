"""Push-chain tests for ChoreFlow (Pflichtenheft §11.2, P3c).

Drives the coordinator directly with a FixedClock + seeded RNG. Requires Home
Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta
from random import Random

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN
from custom_components.choreflow.coordinator import ChoreFlowCoordinator
from custom_components.choreflow.engine.clock import FixedClock
from custom_components.choreflow.engine.scheduler import ScheduleConfig
from custom_components.choreflow.models import Importance, PushChainState, TaskStatus
from custom_components.choreflow.settings import ChoreFlowSettings, PersonSettings
from custom_components.choreflow.store import ChoreFlowStore, LogStore

from .factories import make_instance, make_rule

_PERSON = "person.niklas"
_PARTNER = "person.partner"
_NOTIFY = "notify.mobile_app_niklas"
_PARTNER_NOTIFY = "notify.mobile_app_partner"
_MON_18 = datetime(2026, 6, 15, 18, 0, tzinfo=UTC)  # Monday, within window
_TODAY = date(2026, 6, 15)
_KEY = f"{_PERSON}|{_TODAY.isoformat()}"


def _settings(
    max_tasks: int = 5,
    skip_push_after_completion: bool = False,
    persons: tuple[str, ...] = (_PERSON,),
) -> ChoreFlowSettings:
    notify_services = {
        _PERSON: _NOTIFY,
        _PARTNER: _PARTNER_NOTIFY,
    }
    return ChoreFlowSettings(
        name="Home",
        enabled_persons=list(persons),
        person_settings={
            person: PersonSettings(
                entity_id=person,
                notify_service=notify_services[person],
                presence_required=True,
                weekday_push_enabled=True,
                weekend_push_enabled=True,
            )
            for person in persons
        },
        schedule=ScheduleConfig.with_defaults(),
        max_tasks_per_person_per_day=max_tasks,
        skip_push_after_daily_completion=skip_push_after_completion,
    )


async def _build(
    hass: HomeAssistant,
    clock: FixedClock,
    *,
    max_tasks: int = 5,
    skip_push_after_completion: bool = False,
    persons: tuple[str, ...] = (_PERSON,),
) -> tuple[ChoreFlowCoordinator, ChoreFlowStore, list[dict]]:
    calls: list[dict] = []
    for person, notify_service in (
        (_PERSON, _NOTIFY),
        (_PARTNER, _PARTNER_NOTIFY),
    ):
        if person not in persons:
            continue
        hass.services.async_register(
            "notify",
            notify_service.split(".", 1)[1],
            lambda call: calls.append(dict(call.data)),
        )
        hass.states.async_set(person, "home")

    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    entry = MockConfigEntry(domain=DOMAIN, data={})
    coordinator = ChoreFlowCoordinator(
        hass,
        entry,
        store,
        log_store,
        _settings(max_tasks, skip_push_after_completion, persons),
        clock=clock,
        rng=Random(1),
    )
    return coordinator, store, calls


@pytest.fixture(autouse=True)
def _enable(enable_custom_integrations: None) -> None:
    return None


async def test_start_sends_one_push(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    for inst in (
        make_instance("a", room="Bad", due_date=_TODAY),
        make_instance("b", room="Bad", due_date=_TODAY),
    ):
        store.task_instances[inst.id] = inst

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()

    assert len(calls) == 1
    chain = store.push_chain_states[_KEY]
    assert chain.started is True
    assert chain.current_task_id is not None
    assert chain.tasks_sent_count == 1


async def test_daily_start_batches_person_refreshes(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, calls = await _build(
        hass, FixedClock(_MON_18), persons=(_PERSON, _PARTNER)
    )
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    store.task_instances["b"] = make_instance("b", due_date=_TODAY)
    refreshes: list[bool] = []

    async def _record_refresh() -> None:
        refreshes.append(True)

    monkeypatch.setattr(coordinator, "async_refresh", _record_refresh)

    await coordinator.async_start_daily_flow()

    assert len(calls) == 2
    assert refreshes == [True]


async def test_concurrent_advances_for_same_person_send_once(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    store.task_instances["b"] = make_instance("b", due_date=_TODAY)
    entered = asyncio.Event()
    release = asyncio.Event()
    pushes: list[str] = []

    async def _blocked_push(hass, notify_service, task, person_slug, today_iso):
        pushes.append(task.id)
        entered.set()
        await release.wait()
        return True

    monkeypatch.setattr(
        "custom_components.choreflow.coordinator.async_send_task_push",
        _blocked_push,
    )

    first = asyncio.create_task(coordinator.async_advance_chain(_PERSON))
    await entered.wait()
    second = asyncio.create_task(coordinator.async_advance_chain(_PERSON))
    await asyncio.sleep(0)
    release.set()
    await asyncio.gather(first, second)

    chain = store.push_chain_states[_KEY]
    assert pushes == [chain.current_task_id]
    assert chain.tasks_sent_count == 1
    assert chain.sent_task_ids == [chain.current_task_id]
    assert len(store.reservations) == 1
    assert store.reservations[0].task_id == chain.current_task_id


async def test_different_persons_advance_concurrently(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, _ = await _build(
        hass, FixedClock(_MON_18), persons=(_PERSON, _PARTNER)
    )
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    store.task_instances["b"] = make_instance("b", due_date=_TODAY)
    first_entered = asyncio.Event()
    both_entered = asyncio.Event()
    release = asyncio.Event()
    pushed_slugs: set[str] = set()

    async def _blocked_push(hass, notify_service, task, person_slug, today_iso):
        pushed_slugs.add(person_slug)
        first_entered.set()
        if len(pushed_slugs) == 2:
            both_entered.set()
        await release.wait()
        return True

    monkeypatch.setattr(
        "custom_components.choreflow.coordinator.async_send_task_push",
        _blocked_push,
    )

    first = asyncio.create_task(coordinator.async_advance_chain(_PERSON))
    await first_entered.wait()
    second = asyncio.create_task(coordinator.async_advance_chain(_PARTNER))
    await asyncio.wait_for(both_entered.wait(), timeout=1)
    release.set()
    await asyncio.gather(first, second)

    assert pushed_slugs == {"niklas", "partner"}


async def test_advance_releases_lock_before_reentrant_refresh(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    refreshes = 0

    async def _reentrant_refresh() -> None:
        nonlocal refreshes
        refreshes += 1
        await coordinator.async_advance_chain(_PERSON)

    monkeypatch.setattr(coordinator, "async_refresh", _reentrant_refresh)

    await asyncio.wait_for(coordinator.async_advance_chain(_PERSON), timeout=1)

    assert refreshes == 1
    assert len(calls) == 1
    assert store.push_chain_states[_KEY].current_task_id == "a"


async def test_waiting_chain_schedules_save_without_refresh(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    chain = coordinator._get_chain(_PERSON, _TODAY)
    chain.current_task_id = "waiting"
    scheduled: list[bool] = []
    refreshes: list[bool] = []
    monkeypatch.setattr(store, "async_schedule_save", lambda: scheduled.append(True))

    async def _record_refresh() -> None:
        refreshes.append(True)

    monkeypatch.setattr(coordinator, "async_refresh", _record_refresh)

    assert await coordinator.async_advance_chain(_PERSON) is False

    assert scheduled == [True]
    assert refreshes == []


async def test_complete_advances_to_next(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    for inst in (
        make_instance("a", room="Bad", due_date=_TODAY),
        make_instance("b", room="Bad", due_date=_TODAY),
    ):
        store.task_instances[inst.id] = inst

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    first = chain.current_task_id
    assert first is not None

    await coordinator.async_complete_task(first, _PERSON, "push")
    await hass.async_block_till_done()

    assert store.task_instances[first].status == TaskStatus.COMPLETED
    assert len(calls) == 2
    assert chain.tasks_sent_count == 2
    assert chain.current_task_id is not None
    assert chain.current_task_id != first


async def test_completion_persists_long_interval_rule_anchor(
    hass: HomeAssistant,
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    rule = make_rule(
        "long-interval",
        recurrence_interval=182,
        created_date=_TODAY - timedelta(days=182),
    )
    task = make_instance("current", rule_id=rule.id, due_date=_TODAY)
    store.task_rules[rule.id] = rule
    store.task_instances[task.id] = task

    await coordinator.async_complete_task(task.id, _PERSON, "push")

    assert rule.last_completed_date == _TODAY
    successors = [
        instance
        for instance in store.task_instances.values()
        if instance.rule_id == rule.id and instance.status == TaskStatus.OPEN
    ]
    assert [instance.due_date for instance in successors] == [
        _TODAY + timedelta(days=182)
    ]


async def test_generation_migrates_legacy_anchor_before_pruning(
    hass: HomeAssistant,
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    completed_at = _MON_18 - timedelta(days=121)
    rule = make_rule(
        "legacy-long-interval",
        recurrence_interval=182,
        created_date=completed_at.date() - timedelta(days=182),
    )
    completed = make_instance(
        "old-completion",
        rule_id=rule.id,
        due_date=completed_at.date(),
        status=TaskStatus.COMPLETED,
        completed_at=completed_at,
    )
    store.task_rules[rule.id] = rule
    store.task_instances[completed.id] = completed

    await coordinator._generate_due_instances()

    assert rule.last_completed_date == completed_at.date()
    assert completed.id not in store.task_instances
    successors = [
        instance
        for instance in store.task_instances.values()
        if instance.rule_id == rule.id and instance.status == TaskStatus.OPEN
    ]
    assert [instance.due_date for instance in successors] == [
        completed_at.date() + timedelta(days=182)
    ]


async def test_reopening_old_completion_keeps_synthetic_recurrence_anchor(
    hass: HomeAssistant,
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    rule = make_rule(
        "changed-recurrence",
        recurrence_interval=30,
        created_date=_TODAY - timedelta(days=60),
    )
    current = make_instance("current", rule_id=rule.id, due_date=_TODAY)
    older = make_instance(
        "older-completion",
        rule_id=rule.id,
        due_date=_TODAY - timedelta(days=30),
        status=TaskStatus.COMPLETED,
        completed_at=_MON_18 - timedelta(days=30),
    )
    store.task_rules[rule.id] = rule
    store.task_instances[current.id] = current
    store.task_instances[older.id] = older

    await coordinator.async_update_task(current.id, {"recurrence_interval": 14})
    assert rule.created_date == _TODAY
    assert rule.last_completed_date == _TODAY

    await coordinator.async_reopen_task(older.id)

    assert rule.last_completed_date == _TODAY


async def test_snooze_normal_ends_chain(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    for inst in (
        make_instance("a", due_date=_TODAY),
        make_instance("b", due_date=_TODAY),
    ):
        store.task_instances[inst.id] = inst

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    current = chain.current_task_id
    assert current is not None

    await coordinator.async_snooze_task(current, _PERSON)
    await hass.async_block_till_done()

    assert chain.active is False
    assert chain.ended_reason == "snooze"
    assert len(calls) == 1  # no further push


async def test_snooze_high_continues(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    store.task_instances["h"] = make_instance(
        "h", importance=Importance.HIGH, due_date=_TODAY
    )
    store.task_instances["n"] = make_instance("n", due_date=_TODAY)

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    # high is preferred first.
    assert chain.current_task_id == "h"

    await coordinator.async_snooze_task("h", _PERSON)
    await hass.async_block_till_done()

    assert chain.active is True  # high snooze keeps the chain going
    assert len(calls) == 2


async def test_high_snooze_outside_window_is_scheduled_for_persistence(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    late = datetime(2026, 6, 15, 21, 0, tzinfo=UTC)
    coordinator, store, _ = await _build(hass, FixedClock(late))
    task = make_instance("h", importance=Importance.HIGH, due_date=_TODAY)
    store.task_instances[task.id] = task
    chain = coordinator._get_chain(_PERSON, _TODAY)
    chain.current_task_id = task.id
    coordinator._book.reserve(task.id, _PERSON, late)
    scheduled: list[bool] = []
    monkeypatch.setattr(store, "async_schedule_save", lambda: scheduled.append(True))

    await coordinator.async_snooze_task(task.id, _PERSON)

    assert task.snooze_until == _TODAY + timedelta(days=1)
    assert chain.current_task_id is None
    assert scheduled
    restored = ChoreFlowStore(hass, "restored")
    restored._deserialize(store._serialize())
    assert restored.task_instances[task.id].snooze_until == task.snooze_until


async def test_presence_arrival_early_exit_is_persisted(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    scheduled: list[bool] = []
    monkeypatch.setattr(store, "async_schedule_save", lambda: scheduled.append(True))

    await coordinator.async_handle_presence(_PERSON, True)

    chain = store.push_chain_states[_KEY]
    assert chain.active is False
    assert chain.ended_reason == "no_tasks"
    assert scheduled


async def test_day_limit_stops_chain(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18), max_tasks=1)
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    store.task_instances["b"] = make_instance("b", due_date=_TODAY)

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    first = chain.current_task_id
    assert first is not None

    await coordinator.async_complete_task(first, _PERSON, "push")
    await hass.async_block_till_done()

    assert len(calls) == 1  # limit reached, no second push
    assert chain.ended_reason == "limit"


async def test_presence_pause_and_return(hass: HomeAssistant) -> None:
    coordinator, store, calls = await _build(hass, FixedClock(_MON_18))
    store.task_instances["a"] = make_instance("a", due_date=_TODAY)
    store.task_instances["b"] = make_instance("b", due_date=_TODAY)

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    assert chain.current_task_id is not None

    # Leaves home → chain pauses, no push even if current task completes elsewhere.
    hass.states.async_set(_PERSON, "not_home")
    await coordinator.async_handle_presence(_PERSON, False)
    await hass.async_block_till_done()
    assert chain.active is False

    # Returns home → chain continues (current task still pending, so no new push
    # until it is actioned); complete it then expect the next push.
    hass.states.async_set(_PERSON, "home")
    first = chain.current_task_id
    assert first is not None
    await coordinator.async_complete_task(first, _PERSON, "push")
    await hass.async_block_till_done()
    assert len(calls) == 2


async def test_day_end_marks_missed_catchup(hass: HomeAssistant) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    task = make_instance("reserved", due_date=_TODAY)
    store.task_instances[task.id] = task
    chain = coordinator._get_chain(_PERSON, _TODAY)
    chain.pending_catchup = True
    chain.started = False
    chain.current_task_id = task.id
    coordinator._book.reserve(task.id, _PERSON, _MON_18)

    await coordinator.async_handle_day_end()
    await hass.async_block_till_done()

    assert chain.active is False
    assert chain.ended_reason == "window_end"
    assert chain.current_task_id is None
    assert store.reservations == []


async def test_stale_reservation_does_not_block_another_person_next_day(
    hass: HomeAssistant,
) -> None:
    next_day = _MON_18 + timedelta(days=1)
    coordinator, store, calls = await _build(
        hass, FixedClock(next_day), persons=(_PERSON, _PARTNER)
    )
    task = make_instance("ignored", due_date=_TODAY)
    store.task_instances[task.id] = task
    coordinator._book.reserve(task.id, _PERSON, _MON_18)

    await coordinator.async_advance_chain(_PARTNER)

    partner_key = f"{_PARTNER}|{next_day.date().isoformat()}"
    assert len(calls) == 1
    assert store.push_chain_states[partner_key].current_task_id == task.id
    assert {r.person_entity for r in store.reservations} == {_PARTNER}


async def test_pruning_bounds_state_and_schedules_save(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    coordinator, store, _ = await _build(hass, FixedClock(_MON_18))
    old = _MON_18 - timedelta(days=121)
    store.task_instances["completed-old"] = make_instance(
        "completed-old", status=TaskStatus.COMPLETED, completed_at=old
    )
    store.task_instances["deleted-old"] = make_instance(
        "deleted-old", status=TaskStatus.DELETED, deleted_at=old
    )
    store.task_instances["deleted-today"] = make_instance(
        "deleted-today", status=TaskStatus.DELETED, deleted_at=_MON_18
    )
    old_chain = PushChainState(person_entity=_PERSON, date=_TODAY - timedelta(days=8))
    current_chain = PushChainState(person_entity=_PERSON, date=_TODAY)
    store.push_chain_states[old_chain.key] = old_chain
    store.push_chain_states[current_chain.key] = current_chain
    coordinator._book.reserve("stale", _PERSON, _MON_18 - timedelta(days=1))
    scheduled: list[bool] = []
    monkeypatch.setattr(store, "async_schedule_save", lambda: scheduled.append(True))

    assert coordinator._prune_stale(_TODAY) is True

    assert "completed-old" not in store.task_instances
    assert "deleted-old" not in store.task_instances
    assert "deleted-today" in store.task_instances
    assert old_chain.key not in store.push_chain_states
    assert current_chain.key in store.push_chain_states
    assert store.reservations == []
    assert scheduled == [True]


async def test_skip_push_after_daily_completion(hass: HomeAssistant) -> None:
    """After completing one task, no further push is sent (Feature 5)."""
    coordinator, store, calls = await _build(
        hass, FixedClock(_MON_18), skip_push_after_completion=True
    )
    for inst in (
        make_instance("a", room="Bad", due_date=_TODAY),
        make_instance("b", room="Bad", due_date=_TODAY),
    ):
        store.task_instances[inst.id] = inst

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    first = chain.current_task_id
    assert first is not None

    await coordinator.async_complete_task(first, _PERSON, "push")
    await hass.async_block_till_done()

    assert store.task_instances[first].status == TaskStatus.COMPLETED
    assert len(calls) == 1  # no second push after daily completion
    assert chain.ended_reason == "daily_completion_reached"


async def test_skip_push_disabled_still_advances(hass: HomeAssistant) -> None:
    """With skip_push disabled, chain still advances after completion."""
    coordinator, store, calls = await _build(
        hass, FixedClock(_MON_18), skip_push_after_completion=False
    )
    for inst in (
        make_instance("a", room="Bad", due_date=_TODAY),
        make_instance("b", room="Bad", due_date=_TODAY),
    ):
        store.task_instances[inst.id] = inst

    await coordinator.async_start_daily_flow(_PERSON)
    await hass.async_block_till_done()
    chain = store.push_chain_states[_KEY]
    first = chain.current_task_id
    assert first is not None

    await coordinator.async_complete_task(first, _PERSON, "push")
    await hass.async_block_till_done()

    assert len(calls) == 2
    assert chain.tasks_sent_count == 2
