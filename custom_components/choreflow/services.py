"""Service registration and handlers for ChoreFlow (Pflichtenheft §5.7).

MVP 0.1 services: create/update/delete/complete/snooze tasks plus chain control
(start_daily_flow, send_next_task). The to-do, calendar and export services are
added with their features in P4/P5/P6.
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_ENTITY_ID,
    ATTR_EXPORT_FORMAT,
    ATTR_PERSON_ENTITY,
    ATTR_SOURCE,
    ATTR_TASK_ID,
    CARD_API_VERSION,
    COMPLETION_SOURCE_DASHBOARD,
    DATA_CALENDAR_SOURCE,
    DATA_COORDINATOR,
    DATA_LOG_STORE,
    DATA_TODO_SYNC,
    DEFAULT_QUERY_LIMIT,
    DOMAIN,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EXPORT_DIRNAME,
    LOG_EVENT_TYPES,
    MAX_QUERY_LIMIT,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_TASK,
    SERVICE_EXPORT_LOG,
    SERVICE_GET_HISTORY,
    SERVICE_GET_TASK,
    SERVICE_GET_TASKS,
    SERVICE_IMPORT_SEED_TASKS,
    SERVICE_REBUILD_CALENDAR_TASKS,
    SERVICE_REOPEN_TASK,
    SERVICE_SEND_NEXT_TASK,
    SERVICE_SNOOZE_TASK,
    SERVICE_START_DAILY_FLOW,
    SERVICE_SYNC_TODO,
    SERVICE_UPDATE_TASK,
)
from .coordinator import ChoreFlowCoordinator
from .models import TaskInstance, TaskStatus, VisibilityMode
from .seed_tasks import build_seed_rules
from .sources.calendar_source import CalendarSource
from .sources.todo_sync import TodoSync
from .store import LogStore

_LOGGER = logging.getLogger(__name__)

_IMPORTANCE = vol.In(["high", "normal", "low"])
_VISIBILITY = vol.In(["all_enabled_persons", "selected_persons"])
_ASSIGNMENT = vol.In(["random", "assigned"])
_DURATION = vol.All(vol.Coerce(int), vol.Range(min=1, max=1440))
_LIMIT = vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_QUERY_LIMIT))
_OFFSET = vol.All(vol.Coerce(int), vol.Range(min=0))

_CREATE_SCHEMA = vol.Schema(
    {
        vol.Required("title"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("importance"): _IMPORTANCE,
        vol.Optional("estimated_duration_minutes"): _DURATION,
        vol.Optional("due_date"): cv.date,
        vol.Optional("visibility_mode"): _VISIBILITY,
        vol.Optional("visibility_persons"): vol.All(cv.ensure_list, [cv.entity_id]),
        vol.Optional("assignment_mode"): _ASSIGNMENT,
        vol.Optional("assignment_person"): cv.entity_id,
        vol.Optional("calendar_export_entity_id"): cv.entity_id,
    }
)

_UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_ID): cv.string,
        vol.Optional("title"): cv.string,
        vol.Optional("description"): vol.Any(None, cv.string),
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("importance"): _IMPORTANCE,
        vol.Optional("estimated_duration_minutes"): vol.Any(None, _DURATION),
        vol.Optional("due_date"): vol.Any(None, cv.date),
        vol.Optional("visibility_mode"): _VISIBILITY,
        vol.Optional("visibility_persons"): vol.All(cv.ensure_list, [cv.entity_id]),
        vol.Optional("assignment_mode"): _ASSIGNMENT,
        vol.Optional("assignment_person"): cv.entity_id,
        vol.Optional("recurrence_type"): vol.In(["every_n_days", "weekdays", "once"]),
        vol.Optional("recurrence_interval"): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Optional("recurrence_weekdays"): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=6))]
        ),
    }
)

_GET_TASK_SCHEMA = vol.Schema({vol.Required(ATTR_TASK_ID): cv.string})

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

_SYNC_TODO_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.entity_id})

_REBUILD_CALENDAR_SCHEMA = vol.Schema({})

_EXPORT_LOG_SCHEMA = vol.Schema(
    {vol.Optional(ATTR_EXPORT_FORMAT, default="json"): vol.In(["json", "csv"])}
)

_GET_TASKS_SCHEMA = vol.Schema(
    {
        vol.Optional("status", default="open"): vol.In(
            ["open", "completed", "deleted", "all"]
        ),
        vol.Optional(ATTR_PERSON_ENTITY): cv.entity_id,
        vol.Optional("person_scope", default="visible"): vol.In(
            ["visible", "assigned"]
        ),
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("limit", default=DEFAULT_QUERY_LIMIT): _LIMIT,
        vol.Optional("offset", default=0): _OFFSET,
    }
)

_GET_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional(
            "event_types",
            default=[EVENT_TASK_COMPLETED, EVENT_TASK_COMPLETED_FROM_TODO],
        ): vol.All(cv.ensure_list, [vol.In(LOG_EVENT_TYPES)]),
        vol.Optional(ATTR_PERSON_ENTITY): cv.entity_id,
        vol.Optional("room"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("limit", default=DEFAULT_QUERY_LIMIT): _LIMIT,
        vol.Optional("offset", default=0): _OFFSET,
    }
)


def _coordinator(hass: HomeAssistant) -> ChoreFlowCoordinator | None:
    """Return the single ChoreFlow coordinator (single-instance integration)."""
    for data in hass.data.get(DOMAIN, {}).values():
        coordinator: ChoreFlowCoordinator | None = data.get(DATA_COORDINATOR)
        if coordinator is not None:
            return coordinator
    return None


def _todo_sync(hass: HomeAssistant) -> TodoSync | None:
    """Return the single ChoreFlow to-do sync, if configured."""
    for data in hass.data.get(DOMAIN, {}).values():
        todo_sync: TodoSync | None = data.get(DATA_TODO_SYNC)
        if todo_sync is not None:
            return todo_sync
    return None


def _calendar_source(hass: HomeAssistant) -> CalendarSource | None:
    """Return the single ChoreFlow calendar source, if configured."""
    for data in hass.data.get(DOMAIN, {}).values():
        calendar_source: CalendarSource | None = data.get(DATA_CALENDAR_SOURCE)
        if calendar_source is not None:
            return calendar_source
    return None


def _log_store(hass: HomeAssistant) -> LogStore | None:
    """Return the single ChoreFlow log store."""
    for data in hass.data.get(DOMAIN, {}).values():
        log_store: LogStore | None = data.get(DATA_LOG_STORE)
        if log_store is not None:
            return log_store
    return None


def _require_coordinator(hass: HomeAssistant) -> ChoreFlowCoordinator:
    coordinator = _coordinator(hass)
    if coordinator is None:
        raise ServiceValidationError("ChoreFlow is not loaded")
    return coordinator


def _require_task(
    coordinator: ChoreFlowCoordinator,
    task_id: str,
    *,
    require_open: bool = False,
) -> TaskInstance:
    task = coordinator.store.task_instances.get(task_id)
    if task is None:
        raise ServiceValidationError(f"Unknown ChoreFlow task: {task_id}")
    if require_open and task.status != TaskStatus.OPEN:
        raise ServiceValidationError(f"ChoreFlow task is not open: {task_id}")
    return task


def _validate_task_definition(
    fields: dict[str, Any], current: TaskInstance | None = None
) -> None:
    visibility_mode = fields.get(
        "visibility_mode",
        current.visibility_mode.value
        if current is not None
        else VisibilityMode.ALL_ENABLED_PERSONS.value,
    )
    visibility_persons = fields.get(
        "visibility_persons",
        current.visibility_persons if current is not None else [],
    )
    assignment_mode = fields.get(
        "assignment_mode",
        current.assignment_mode.value if current is not None else "random",
    )
    assignment_person = fields.get(
        "assignment_person",
        current.assignment_person if current is not None else None,
    )
    if visibility_mode == VisibilityMode.SELECTED_PERSONS.value:
        if not visibility_persons:
            raise ServiceValidationError(
                "Selected-person visibility requires visibility_persons"
            )
        if (
            assignment_mode == "assigned"
            and assignment_person not in visibility_persons
        ):
            raise ServiceValidationError(
                "The assigned person must be included in visibility_persons"
            )
    if assignment_mode == "assigned" and assignment_person is None:
        raise ServiceValidationError("Assigned tasks require assignment_person")


def _validate_can_act(
    coordinator: ChoreFlowCoordinator,
    task: TaskInstance,
    person_entity: str,
) -> None:
    if person_entity not in coordinator.settings.enabled_persons:
        raise ServiceValidationError(
            f"Person is not enabled in ChoreFlow: {person_entity}"
        )
    if (
        task.visibility_mode == VisibilityMode.SELECTED_PERSONS
        and person_entity not in task.visibility_persons
    ):
        raise ServiceValidationError(
            f"Task {task.id} is not visible to {person_entity}"
        )
    if (
        task.assignment_mode.value == "assigned"
        and task.assignment_person != person_entity
    ):
        raise ServiceValidationError(
            f"Task {task.id} is assigned to {task.assignment_person}"
        )


async def _export_to_calendar(
    hass: HomeAssistant,
    calendar_entity_id: str,
    fields: dict[str, Any],
    task_id: str,
) -> None:
    """Create a single all-day calendar event for the task's due date.

    Uses HA's ``calendar.create_event`` service. Compatible with the o365/ms365
    custom integration that supports writing events. Failures are logged but do
    not abort the task creation so the user isn't blocked.
    """
    due: Any = fields.get("due_date")
    if due is None:
        return
    if isinstance(due, datetime):
        due_date = due.date()
    elif isinstance(due, date):
        due_date = due
    else:
        due_date = date.fromisoformat(str(due))
    summary = fields.get("title", "ChoreFlow task")
    description = fields.get("description") or ""
    if not description:
        room = fields.get("room", "")
        category = fields.get("category", "")
        parts = [p for p in (room, category) if p]
        if parts:
            description = " · ".join(parts)

    try:
        await hass.services.async_call(
            "calendar",
            "create_event",
            {
                "entity_id": calendar_entity_id,
                "summary": summary,
                "start_date": due_date.isoformat(),
                "end_date": (due_date + timedelta(days=1)).isoformat(),
                "description": f"[ChoreFlow {task_id}] {description}".strip(),
            },
            blocking=True,
        )
    except Exception:  # noqa: BLE001 — calendar failures must not block the task
        _LOGGER.exception(
            "ChoreFlow: calendar export to %s failed for task %s",
            calendar_entity_id,
            task_id,
        )


def async_register_services(hass: HomeAssistant) -> None:
    """Register ChoreFlow services (idempotent)."""
    if hass.services.has_service(DOMAIN, SERVICE_COMPLETE_TASK):
        return

    async def _create_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        fields = dict(call.data)
        calendar_entity_id: str | None = fields.pop("calendar_export_entity_id", None)
        _validate_task_definition(fields)
        task_id = await coordinator.async_create_task(fields)
        if calendar_entity_id and fields.get("due_date"):
            await _export_to_calendar(hass, calendar_entity_id, fields, task_id)
        return {"success": True, "task_id": task_id}

    async def _update_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        changes: dict[str, Any] = {
            key: value for key, value in call.data.items() if key != ATTR_TASK_ID
        }
        task = _require_task(coordinator, task_id)
        _validate_task_definition(changes, task)
        await coordinator.async_update_task(task_id, changes)
        return {"success": True, "task_id": task_id}

    async def _delete_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        _require_task(coordinator, task_id)
        await coordinator.async_delete_task(task_id)
        return {"success": True, "task_id": task_id}

    async def _complete_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        person = call.data[ATTR_PERSON_ENTITY]
        task = _require_task(coordinator, task_id, require_open=True)
        _validate_can_act(coordinator, task, person)
        await coordinator.async_complete_task(task_id, person, call.data[ATTR_SOURCE])
        return {"success": True, "task_id": task_id}

    async def _snooze_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        person = call.data[ATTR_PERSON_ENTITY]
        task = _require_task(coordinator, task_id, require_open=True)
        _validate_can_act(coordinator, task, person)
        await coordinator.async_snooze_task(task_id, person)
        return {"success": True, "task_id": task_id}

    async def _reopen_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        task = _require_task(coordinator, task_id)
        if task.status.value != "completed":
            raise ServiceValidationError(
                f"Task {task_id} is not completed and cannot be reopened"
            )
        await coordinator.async_reopen_task(task_id)
        return {"success": True, "task_id": task_id}

    async def _import_seed_tasks(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        today = coordinator.clock.today()
        rules = build_seed_rules(today)
        added = 0
        for rule in rules:
            if rule.id not in coordinator.store.task_rules:
                coordinator.store.task_rules[rule.id] = rule
                added += 1
        if added:
            coordinator.store.async_schedule_save()
            await coordinator.async_refresh()
        return {"success": True, "added": added, "skipped": len(rules) - added}

    async def _start_daily_flow(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_start_daily_flow(call.data.get(ATTR_PERSON_ENTITY))

    async def _send_next_task(call: ServiceCall) -> None:
        coordinator = _coordinator(hass)
        if coordinator is not None:
            await coordinator.async_send_next_task(call.data[ATTR_PERSON_ENTITY])

    async def _sync_todo(call: ServiceCall) -> None:
        todo_sync = _todo_sync(hass)
        if todo_sync is not None:
            await todo_sync.async_sync()

    async def _rebuild_calendar_tasks(call: ServiceCall) -> None:
        calendar_source = _calendar_source(hass)
        if calendar_source is not None:
            await calendar_source.async_sync()

    async def _export_log(call: ServiceCall) -> dict[str, Any] | None:
        log_store = _log_store(hass)
        if log_store is None:
            return None
        fmt = call.data[ATTR_EXPORT_FORMAT]
        timestamp = dt_util.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            hass.config.path(EXPORT_DIRNAME), f"choreflow_log_{timestamp}.{fmt}"
        )
        written = await log_store.async_export(path, fmt)
        return {"path": written}

    async def _get_task(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        task_id = call.data[ATTR_TASK_ID]
        result = coordinator.get_task(task_id)
        if result is None:
            raise ServiceValidationError(f"Unknown ChoreFlow task: {task_id}")
        return result

    async def _get_tasks(call: ServiceCall) -> dict[str, Any]:
        coordinator = _require_coordinator(hass)
        return coordinator.query_tasks(
            status=call.data["status"],
            person_entity=call.data.get(ATTR_PERSON_ENTITY),
            person_scope=call.data["person_scope"],
            room=call.data.get("room"),
            category=call.data.get("category"),
            limit=call.data["limit"],
            offset=call.data["offset"],
        )

    async def _get_history(call: ServiceCall) -> dict[str, Any]:
        log_store = _log_store(hass)
        if log_store is None:
            raise ServiceValidationError("ChoreFlow log store is not loaded")
        rows, total = await log_store.async_query_history(
            event_types=call.data["event_types"],
            person_entity=call.data.get(ATTR_PERSON_ENTITY),
            room=call.data.get("room"),
            category=call.data.get("category"),
            limit=call.data["limit"],
            offset=call.data["offset"],
        )
        return {
            "api_version": CARD_API_VERSION,
            "items": rows,
            "total": total,
            "limit": call.data["limit"],
            "offset": call.data["offset"],
            "has_more": call.data["offset"] + len(rows) < total,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_TASK,
        _create_task,
        schema=_CREATE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_TASK,
        _update_task,
        schema=_UPDATE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_TASK,
        _delete_task,
        schema=_DELETE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        _complete_task,
        schema=_COMPLETE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SNOOZE_TASK,
        _snooze_task,
        schema=_SNOOZE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REOPEN_TASK,
        _reopen_task,
        schema=_DELETE_SCHEMA,  # same shape: just task_id required
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT_SEED_TASKS,
        _import_seed_tasks,
        schema=vol.Schema({}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_START_DAILY_FLOW, _start_daily_flow, schema=_START_FLOW_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_NEXT_TASK, _send_next_task, schema=_SEND_NEXT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SYNC_TODO, _sync_todo, schema=_SYNC_TODO_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REBUILD_CALENDAR_TASKS,
        _rebuild_calendar_tasks,
        schema=_REBUILD_CALENDAR_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_LOG,
        _export_log,
        schema=_EXPORT_LOG_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_TASK,
        _get_task,
        schema=_GET_TASK_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_TASKS,
        _get_tasks,
        schema=_GET_TASKS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_HISTORY,
        _get_history,
        schema=_GET_HISTORY_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove ChoreFlow services."""
    for service in (
        SERVICE_CREATE_TASK,
        SERVICE_UPDATE_TASK,
        SERVICE_DELETE_TASK,
        SERVICE_COMPLETE_TASK,
        SERVICE_SNOOZE_TASK,
        SERVICE_REOPEN_TASK,
        SERVICE_IMPORT_SEED_TASKS,
        SERVICE_START_DAILY_FLOW,
        SERVICE_SEND_NEXT_TASK,
        SERVICE_SYNC_TODO,
        SERVICE_REBUILD_CALENDAR_TASKS,
        SERVICE_EXPORT_LOG,
        SERVICE_GET_TASK,
        SERVICE_GET_TASKS,
        SERVICE_GET_HISTORY,
    ):
        hass.services.async_remove(DOMAIN, service)
