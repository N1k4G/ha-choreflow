"""The ChoreFlow integration.

Config-flow-only household chore manager (Pflichtenheft §5.1). This module owns
the config-entry lifecycle. The heavy wiring — Store/LogStore, coordinator,
platforms, services, presence/notification/calendar/todo listeners and the
schedule timers — is added in later work packages (P1–P3); the calls below are
marked with TODO and intentionally left out so the entry already loads cleanly.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ChoreFlow from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data[entry.entry_id] = {}

    # TODO(P1): load HA Store + initialise SQLite LogStore.
    # TODO(P3): create coordinator, forward PLATFORMS, register services and
    #           the presence / notification-action / time listeners.

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.debug("ChoreFlow entry %s set up (P0 skeleton)", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # TODO(P3): unload platforms, cancel timers, detach listeners, close the DB.
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change (Pflichtenheft §5.1)."""
    await hass.config_entries.async_reload(entry.entry_id)
