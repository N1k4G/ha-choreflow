"""Push-chain tests for ChoreFlow (Pflichtenheft §11.2, P3c).

Drives the coordinator directly with a FixedClock + seeded RNG. Requires Home
Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from random import Random

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN
from custom_components.choreflow.coordinator import ChoreFlowCoordinator
from custom_components.choreflow.engine.clock import FixedClock
from custom_components.choreflow.engine.scheduler import ScheduleConfig
from custom_components.choreflow.models import Importance, TaskStatus
from custom_components.choreflow.settings import ChoreFlowSettings, PersonSettings
from custom_components.choreflow.store import ChoreFlowStore, LogStore

from .factories import make_instance

_PERSON = "person.niklas"
_NOTIFY = "notify.mobile_app_niklas"
_MON_18 = datetime(2026, 6, 15, 18, 0, tzinfo=UTC)  # Monday, within window
_TODAY = date(2026, 6, 15)
_KEY = f"{_PERSON}|{_TODAY.isoformat()}"


def _settings(
    max_tasks: int = 5, skip_push_after_completion: bool = False
) -> ChoreFlowSettings:
    return ChoreFlowSettings(
        name="Home",
        enabled_persons=[_PERSON],
        person_settings={
            _PERSON: PersonSettings(
                entity_id=_PERSON,
                notify_service=_NOTIFY,
                presence_required=True,
                weekday_push_enabled=True,
                weekend_push_enabled=True,
            )
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
) -> tuple[ChoreFlowCoordinator, ChoreFlowStore, list[dict]]:
    calls: list[dict] = []
    hass.services.async_register(
        "notify", "mobile_app_niklas", lambda call: calls.append(dict(call.data))
    )
    hass.states.async_set(_PERSON, "home")

    store = ChoreFlowStore(hass, "e1")
    log_store = LogStore(hass, ":memory:")
    await log_store.async_setup()
    entry = MockConfigEntry(domain=DOMAIN, data={})
    coordinator = ChoreFlowCoordinator(
        hass,
        entry,
        store,
        log_store,
        _settings(max_tasks, skip_push_after_completion),
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
    chain = coordinator._get_chain(_PERSON, _TODAY)
    chain.pending_catchup = True
    chain.started = False

    await coordinator.async_handle_day_end()
    await hass.async_block_till_done()

    assert chain.active is False
    assert chain.ended_reason == "window_end"


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
