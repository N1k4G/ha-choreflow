"""The ChoreFlow integration.

Config-flow-only household chore manager (Pflichtenheft §5.1). Owns the
config-entry lifecycle: state + log stores, the coordinator, platforms, repair
issues, services, and the runtime triggers — presence changes, the daily start
and day-end timers, and the notification-action back channel (§5.3/§5.4).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_DOMAIN,
    EVENT_SERVICE_REGISTERED,
    EVENT_SERVICE_REMOVED,
    Platform,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import start as ha_start
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_call_later,
    async_track_state_change_event,
    async_track_time_change,
)

from .const import (
    CALENDAR_RECONCILE_HOUR,
    CALENDAR_RECONCILE_MINUTE,
    DATA_CALENDAR_SOURCE,
    DATA_COORDINATOR,
    DATA_LOG_STORE,
    DATA_SETTINGS,
    DATA_STORE,
    DATA_TODO_SYNC,
    DB_FILENAME,
    DOMAIN,
    EVENT_MOBILE_APP_NOTIFICATION_ACTION,
)
from .coordinator import ChoreFlowCoordinator
from .frontend import async_register_card
from .notify import parse_action_id
from .repairs import async_check_issues, async_clear_issues
from .services import async_register_services, async_unregister_services
from .settings import ChoreFlowSettings
from .sources.calendar_source import CalendarSource
from .sources.todo_sync import TodoSync
from .store import ChoreFlowStore, LogStore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]
_TODO_SYNC_DEBOUNCE_SECONDS = 3.0


class _TodoSyncDebouncer:
    """Collapse state-change bursts and self-triggered writes into one sync."""

    def __init__(
        self,
        hass: HomeAssistant,
        function: Callable[[], Awaitable[None]],
    ) -> None:
        self._hass = hass
        self._function = function
        self._cancel: Callable[[], None] | None = None

    @callback
    def async_schedule(self) -> None:
        """Restart the trailing debounce timer."""
        if self._cancel is not None:
            self._cancel()
        self._cancel = async_call_later(
            self._hass,
            _TODO_SYNC_DEBOUNCE_SECONDS,
            self._async_run,
        )

    async def _async_run(self, _now: object) -> None:
        self._cancel = None
        await self._function()

    @callback
    def async_cancel(self) -> None:
        """Cancel a pending trailing sync during unload."""
        if self._cancel is not None:
            self._cancel()
            self._cancel = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ChoreFlow from a config entry."""
    store = ChoreFlowStore(hass, entry.entry_id)
    await store.async_load()

    log_store = LogStore(hass, hass.config.path(DB_FILENAME))
    await log_store.async_setup()

    settings = ChoreFlowSettings.from_entry(entry)
    coordinator = ChoreFlowCoordinator(hass, entry, store, log_store, settings)
    await coordinator.async_config_entry_first_refresh()

    todo_sync = TodoSync(hass, coordinator, settings)
    calendar_source = CalendarSource(hass, coordinator, settings)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_STORE: store,
        DATA_LOG_STORE: log_store,
        DATA_SETTINGS: settings,
        DATA_COORDINATOR: coordinator,
        DATA_TODO_SYNC: todo_sync,
        DATA_CALENDAR_SOURCE: calendar_source,
    }

    @callback
    def _check_issues_at_start(_hass: HomeAssistant) -> None:
        async_check_issues(hass, entry, settings)

    cancel = ha_start.async_at_started(hass, _check_issues_at_start)
    if cancel is not None:
        entry.async_on_unload(cancel)
    _register_issue_tracking(hass, entry, settings)

    async_register_services(hass)
    await async_register_card(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_runtime_triggers(hass, entry, coordinator, settings)
    _register_todo_sync(hass, entry, coordinator, todo_sync)
    _register_calendar_source(hass, entry, calendar_source)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.debug("ChoreFlow entry %s set up", entry.entry_id)
    return True


@callback
def _register_issue_tracking(
    hass: HomeAssistant,
    entry: ConfigEntry,
    settings: ChoreFlowSettings,
) -> None:
    """Re-evaluate notify repair issues as services come and go."""

    @callback
    def _on_service_change(event: Event) -> None:
        if event.data.get(ATTR_DOMAIN) == "notify":
            async_check_issues(hass, entry, settings)

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_SERVICE_REGISTERED, _on_service_change)
    )
    entry.async_on_unload(
        hass.bus.async_listen(EVENT_SERVICE_REMOVED, _on_service_change)
    )


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


@callback
def _register_todo_sync(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: ChoreFlowCoordinator,
    todo_sync: TodoSync,
) -> None:
    """Wire to-do completion mirroring, change tracking and an initial sync."""
    if not todo_sync.active or todo_sync.entity_id is None:
        return

    coordinator.add_completion_listener(todo_sync.async_on_completion)
    coordinator.add_task_created_listener(todo_sync.async_on_task_created)
    coordinator.add_task_reopened_listener(todo_sync.async_on_task_reopened)
    coordinator.add_task_deleted_listener(todo_sync.async_on_task_deleted)
    debouncer = _TodoSyncDebouncer(hass, todo_sync.async_sync)
    entry.async_on_unload(debouncer.async_cancel)

    @callback
    def _on_todo_change(event: Event[EventStateChangedData]) -> None:
        debouncer.async_schedule()

    entry.async_on_unload(
        async_track_state_change_event(hass, [todo_sync.entity_id], _on_todo_change)
    )

    async def _reconcile(_now: object) -> None:
        await todo_sync.async_sync()

    entry.async_on_unload(
        async_track_time_change(
            hass,
            _reconcile,
            hour=CALENDAR_RECONCILE_HOUR,
            minute=CALENDAR_RECONCILE_MINUTE,
            second=0,
        )
    )

    def _start_todo_sync(_hass: HomeAssistant) -> None:
        entry.async_create_background_task(
            hass,
            todo_sync.async_sync(),
            name="choreflow_initial_todo_sync",
            eager_start=False,
        )

    cancel = ha_start.async_at_started(hass, _start_todo_sync)
    if cancel is not None:
        entry.async_on_unload(cancel)


@callback
def _register_calendar_source(
    hass: HomeAssistant,
    entry: ConfigEntry,
    calendar_source: CalendarSource,
) -> None:
    """Wire a daily calendar reconcile and an initial sync (§7)."""
    if not calendar_source.active:
        return

    async def _reconcile(_now: object) -> None:
        await calendar_source.async_sync()

    entry.async_on_unload(
        async_track_time_change(
            hass,
            _reconcile,
            hour=CALENDAR_RECONCILE_HOUR,
            minute=CALENDAR_RECONCILE_MINUTE,
            second=0,
        )
    )

    def _start_calendar_sync(_hass: HomeAssistant) -> None:
        entry.async_create_background_task(
            hass, calendar_source.async_sync(), name="choreflow_initial_calendar_sync"
        )

    cancel = ha_start.async_at_started(hass, _start_calendar_sync)
    if cancel is not None:
        entry.async_on_unload(cancel)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and release its resources."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        try:
            if data is not None:
                try:
                    await data[DATA_STORE].async_save()
                finally:
                    await data[DATA_LOG_STORE].async_close()
        finally:
            if not hass.data[DOMAIN]:
                async_unregister_services(hass)

    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove entry-scoped operational state.

    The SQLite event log and user-created exports are retained deliberately so
    uninstalling the integration does not destroy long-term household history.
    """
    store = ChoreFlowStore(hass, entry.entry_id)
    await store.async_remove()
    async_clear_issues(hass, entry)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change (Pflichtenheft §5.1)."""
    await hass.config_entries.async_reload(entry.entry_id)
