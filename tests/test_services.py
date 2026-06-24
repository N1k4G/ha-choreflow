"""Service + notification-action wiring tests (Pflichtenheft §11.2, P3c).

Exercises the full entry setup so services and the bus listener are registered.
Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    ACTION_PREFIX_DONE,
    DATA_STORE,
    DOMAIN,
    EVENT_MOBILE_APP_NOTIFICATION_ACTION,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
)
from custom_components.choreflow.models import TaskStatus
from custom_components.choreflow.notify import build_action_id

from .factories import config_entry_data

_PERSON = "person.niklas"


def _prereqs(hass: HomeAssistant) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _find_task_id(hass: HomeAssistant, entry: MockConfigEntry, title: str) -> str:
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    for inst in store.task_instances.values():
        if inst.title == title:
            return inst.id
    raise AssertionError(f"task {title!r} not found")


async def test_services_are_registered(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)
    for service in (
        "create_task",
        "update_task",
        "delete_task",
        "complete_task",
        "snooze_task",
        "start_daily_flow",
        "send_next_task",
    ):
        assert hass.services.has_service(DOMAIN, service)


async def test_create_and_complete_task_services(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CREATE_TASK,
        {"title": "Wipe sink", "room": "Bad", "importance": "normal"},
        blocking=True,
    )
    task_id = _find_task_id(hass, entry, "Wipe sink")

    await hass.services.async_call(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        {"task_id": task_id, "person_entity": _PERSON, "source": "dashboard"},
        blocking=True,
    )
    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    assert store.task_instances[task_id].status == TaskStatus.COMPLETED
    assert store.task_instances[task_id].completion_source == "dashboard"


async def test_notification_action_completes_task(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    entry = await _setup(hass)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CREATE_TASK,
        {"title": "Take out trash", "room": "Außenbereich"},
        blocking=True,
    )
    task_id = _find_task_id(hass, entry, "Take out trash")

    hass.bus.async_fire(
        EVENT_MOBILE_APP_NOTIFICATION_ACTION,
        {"action": build_action_id(ACTION_PREFIX_DONE, task_id, "niklas")},
    )
    await hass.async_block_till_done()

    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    assert store.task_instances[task_id].status == TaskStatus.COMPLETED
    assert store.task_instances[task_id].completion_source == "push"
