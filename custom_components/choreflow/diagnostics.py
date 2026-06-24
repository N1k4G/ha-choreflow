"""Diagnostics for ChoreFlow (Pflichtenheft §5.8, Lastenheft §24.3).

Output is safe to attach to a GitHub issue: notify services are redacted and no
task content is exported — only counts and status.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_NOTIFY_SERVICE, DATA_COORDINATOR, DATA_STORE, DOMAIN
from .coordinator import ChoreFlowCoordinator
from .store import ChoreFlowStore

_REDACT = {CONF_NOTIFY_SERVICE}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return redacted diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ChoreFlowCoordinator = data[DATA_COORDINATOR]
    store: ChoreFlowStore = data[DATA_STORE]

    snapshot = coordinator.data

    return {
        "entry": {
            "data": async_redact_data(dict(entry.data), _REDACT),
            "options": async_redact_data(dict(entry.options), _REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "open_tasks": snapshot.open_tasks if snapshot else None,
            "due_tasks": snapshot.due_tasks if snapshot else None,
            "overdue_tasks": snapshot.overdue_tasks if snapshot else None,
            "completed_today": snapshot.completed_today if snapshot else None,
            "active_chains": snapshot.active_chains if snapshot else None,
        },
        "store": {
            "task_rules": len(store.task_rules),
            "open_instances": len(store.task_instances),
            "push_chain_states": len(store.push_chain_states),
            "reservations": len(store.reservations),
            "todo_sync_state_keys": sorted(store.sync_state.keys()),
            "calendar_state_keys": sorted(store.calendar_state.keys()),
        },
    }
