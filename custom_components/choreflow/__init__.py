"""The ChoreFlow integration.

Config-flow-only household chore manager (Pflichtenheft §5.1). Owns the
config-entry lifecycle: state + log stores, the coordinator, platforms, repair
issues, services, and the runtime triggers — presence changes, the daily start
and day-end timers, and the notification-action back channel (§5.3/§5.4).
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
    async_track_time_change,
)

from .const import (
    DATA_COORDINATOR,
    DATA_LOG_STORE,
    DATA_SETTINGS,
    DATA_STORE,
    DB_FILENAME,
    DOMAIN,
    EVENT_MOBILE_APP_NOTIFICATION_ACTION,
)
from .coordinator import ChoreFlowCoordinator
from .notify import parse_action_id
from .repairs import async_check_issues
from .services import async_register_services, async_unregister_services
from .settings import ChoreFlowSettings
from .store import ChoreFlowStore, LogStore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ChoreFlow from a config entry."""
    store = ChoreFlowStore(hass, entry.entry_id)
    await store.async_load()

    log_store = LogStore(hass, hass.config.path(DB_FILENAME))
    await log_store.async_setup()

    settings = ChoreFlowSettings.from_entry(entry)
    coordinator = ChoreFlowCoordinator(hass, entry, store, log_store, settings)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_STORE: store,
        DATA_LOG_STORE: log_store,
        DATA_SETTINGS: settings,
        DATA_COORDINATOR: coordinator,
    }

    async_check_issues(hass, entry, settings)
    async_register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_runtime_triggers(hass, entry, coordinator, settings)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.debug("ChoreFlow entry %s set up", entry.entry_id)
    return True


@callback
def _register_runtime_triggers(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: ChoreFlowCoordinator,
    settings: ChoreFlowSettings,
) -> None:
    """Wire presence, schedule timers and the notification back channel."""
    schedule = settings.schedule

    async def _weekday_start(_now: object) -> None:
        await coordinator.async_handle_start_time(weekend=False)

    async def _weekend_start(_now: object) -> None:
        await coordinator.async_handle_start_time(weekend=True)

    async def _day_end(_now: object) -> None:
        await coordinator.async_handle_day_end()

    entry.async_on_unload(
        async_track_time_change(
            hass,
            _weekday_start,
            hour=schedule.weekday_start.hour,
            minute=schedule.weekday_start.minute,
            second=0,
        )
    )
    entry.async_on_unload(
        async_track_time_change(
            hass,
            _weekend_start,
            hour=schedule.weekend_start.hour,
            minute=schedule.weekend_start.minute,
            second=0,
        )
    )
    entry.async_on_unload(
        async_track_time_change(
            hass,
            _day_end,
            hour=schedule.day_end.hour,
            minute=schedule.day_end.minute,
            second=0,
        )
    )

    @callback
    def _on_presence(event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is None:
            return
        old_state = event.data["old_state"]
        new_home = new_state.state == "home"
        old_home = old_state.state == "home" if old_state else None
        if new_home == old_home:
            return
        person = event.data["entity_id"]
        hass.async_create_task(coordinator.async_handle_presence(person, new_home))

    if settings.enabled_persons:
        entry.async_on_unload(
            async_track_state_change_event(hass, settings.enabled_persons, _on_presence)
        )

    @callback
    def _on_notification_action(event: Event) -> None:
        action = event.data.get("action")
        if not action:
            return
        parsed = parse_action_id(action)
        if parsed is None:
            return
        hass.async_create_task(
            coordinator.async_handle_notification_action(
                parsed.kind, parsed.task_id, parsed.person_slug
            )
        )

    entry.async_on_unload(
        hass.bus.async_listen(
            EVENT_MOBILE_APP_NOTIFICATION_ACTION, _on_notification_action
        )
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and release its resources."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data is not None:
            await data[DATA_LOG_STORE].async_close()
        if not hass.data[DOMAIN]:
            async_unregister_services(hass)

    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change (Pflichtenheft §5.1)."""
    await hass.config_entries.async_reload(entry.entry_id)
