"""Service registration and handlers for ChoreFlow (Pflichtenheft §5.7).

MVP 0.1 services: create/update/delete/complete/snooze tasks plus chain control
(start_daily_flow, send_next_task). The to-do, calendar and export services are
added with their features in P4/P5/P6.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_PERSON_ENTITY,
    ATTR_SOURCE,
    ATTR_TASK_ID,
    COMPLETION_SOURCE_DASHBOARD,
    DATA_COORDINATOR,
    DOMAIN,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_TASK,
    SERVICE_SEND_NEXT_TASK,
    SERVICE_SNOOZE_TASK,
    SERVICE_START_DAILY_FLOW,
    SERVICE_UPDATE_TASK,
)
from .coordinator import ChoreFlowCoordinator

_IMPORTANCE = vol.In(["high", "normal", "low"])
_VISIBILITY = vol.In(["all_enabled_persons", "selected_persons"])
_ASSIGNMENT = vol.In(["random", "assigned"])

_CREATE_SCHEMA = vol.Schema(
    {
        vol.Required("title"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("importance"): _IMPORTANCE,
        vol.Optional("due_date"): cv.date,
        vol.Optional("visibility_mode"): _VISIBILITY,
        vol.Optional("visibility_persons"): vol.All(cv.ensure_list, [cv.entity_id]),
        vol.Optional("assignment_mode"): _ASSIGNMENT,
        vol.Optional("assignment_person"): cv.entity_id,
    }
)

_UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_ID): cv.string,
        vol.Optional("title"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("importance"): _IMPORTANCE,
        vol.Optional("due_date"): cv.date,
        vol.Optional("visibility_mode"): _VISIBILITY,
        vol.Optional("visibility_persons"): vol.All(cv.ensure_list, [cv.entity_id]),
        vol.Optional("assignment_mode"): _ASSIGNMENT,
        vol.Optional("assignment_person"): cv.entity_id,
    }
)

_DELETE_SCHEMA = vol.Schema({vol.Required(ATTR_TASK_ID): cv.string})

_COMPLETE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_ID): cv.string,
        vol.Required(ATTR_PERSON_ENTITY): cv.entity_id,
        vol.Optional(ATTR_SOURCE, default=COMPLETION_SOURCE_DASHBOARD): cv.string,
    }
)

_SNOOZE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_ID): cv.string,
        vol.Required(ATTR_PERSON_ENTITY): cv.entity_id,
    }
)

_START_FLOW_SCHEMA = vol.Schema({vol.Optional(ATTR_PERSON_ENTITY): cv.entity_id})

_SEND_NEXT_SCHEMA = vol.Schema({vol.Required(ATTR_PERSON_ENTITY): cv.entity_id})


def _coordinator(hass: HomeAssistant) -> ChoreFlowCoordinator | None:
    """Return the single ChoreFlow coordinator (single-instance integration)."""
    for data in hass.data.get(DOMAIN, {}).values():
        coordinator: ChoreFlowCoordinator | None = data.get(DATA_COORDINATOR)
        if coordinator is not None:
            return coordinator
    return None


def async_register_services(hass: HomeAssistant) -> None:
    """Register ChoreFlow services (idempotent)."""
    if hass.services.has_service(DOMAIN, SERVICE_COMPLETE_TASK):
        return

    async def _create_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_create_task(dict(call.data))

    async def _update_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            changes: dict[str, Any] = {
                k: v for k, v in call.data.items() if k != ATTR_TASK_ID
            }
            await coordinator.async_update_task(call.data[ATTR_TASK_ID], changes)

    async def _delete_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_delete_task(call.data[ATTR_TASK_ID])

    async def _complete_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_complete_task(
                call.data[ATTR_TASK_ID],
                call.data[ATTR_PERSON_ENTITY],
                call.data[ATTR_SOURCE],
            )

    async def _snooze_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_snooze_task(
                call.data[ATTR_TASK_ID], call.data[ATTR_PERSON_ENTITY]
            )

    async def _start_daily_flow(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_start_daily_flow(call.data.get(ATTR_PERSON_ENTITY))

    async def _send_next_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_send_next_task(call.data[ATTR_PERSON_ENTITY])

    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_TASK, _create_task, schema=_CREATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_TASK, _update_task, schema=_UPDATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_TASK, _delete_task, schema=_DELETE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_COMPLETE_TASK, _complete_task, schema=_COMPLETE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SNOOZE_TASK, _snooze_task, schema=_SNOOZE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_START_DAILY_FLOW, _start_daily_flow, schema=_START_FLOW_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_NEXT_TASK, _send_next_task, schema=_SEND_NEXT_SCHEMA
    )


def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove ChoreFlow services."""
    for service in (
        SERVICE_CREATE_TASK,
        SERVICE_UPDATE_TASK,
        SERVICE_DELETE_TASK,
        SERVICE_COMPLETE_TASK,
        SERVICE_SNOOZE_TASK,
        SERVICE_START_DAILY_FLOW,
        SERVICE_SEND_NEXT_TASK,
    ):
        hass.services.async_remove(DOMAIN, service)
