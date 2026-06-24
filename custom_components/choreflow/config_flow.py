"""Config flow and options flow for ChoreFlow (Pflichtenheft §5.5).

Multi-step setup: instance name → enabled persons → per-person push settings →
schedule → to-do sync → calendar sync. The options flow walks the same steps,
pre-filled from the current configuration, and writes to the entry options so a
change triggers a reload (§5.5/Lastenheft §21.2). Inputs are validated (person
entities and notify services must exist).
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    CONF_CALENDAR_DUE_OFFSET_DAYS,
    CONF_CALENDAR_ENABLED,
    CONF_CALENDAR_ENTITY_ID,
    CONF_CALENDAR_MATCH_SUMMARY_CONTAINS,
    CONF_CALENDAR_SOURCES,
    CONF_DAY_END_TIME,
    CONF_ENABLED_PERSONS,
    CONF_IMPORT_ASSIGNMENT_MODE,
    CONF_IMPORT_CATEGORY,
    CONF_IMPORT_IMPORTANCE,
    CONF_IMPORT_ROOM,
    CONF_MAX_TASKS_PER_PERSON_PER_DAY,
    CONF_NAME,
    CONF_NOTIFY_SERVICE,
    CONF_PERSON_SETTINGS,
    CONF_PRESENCE_REQUIRED,
    CONF_TODO_ENABLED,
    CONF_TODO_ENTITY_ID,
    CONF_TODO_IMPORT_DEFAULTS,
    CONF_TODO_IMPORT_NEW_ITEMS,
    CONF_TODO_SYNC,
    CONF_TODO_SYNC_FROM_TODO,
    CONF_TODO_SYNC_TO_TODO,
    CONF_WEEKDAY_PUSH_ENABLED,
    CONF_WEEKDAY_START_TIME,
    CONF_WEEKEND_PUSH_ENABLED,
    CONF_WEEKEND_START_TIME,
    DEFAULT_CALENDAR_DUE_OFFSET_DAYS,
    DEFAULT_DAY_END_TIME,
    DEFAULT_IMPORT_ASSIGNMENT_MODE,
    DEFAULT_IMPORT_CATEGORY,
    DEFAULT_IMPORT_IMPORTANCE,
    DEFAULT_IMPORT_ROOM,
    DEFAULT_MAX_TASKS_PER_PERSON_PER_DAY,
    DEFAULT_NAME,
    DEFAULT_PRESENCE_REQUIRED,
    DEFAULT_WEEKDAY_PUSH_ENABLED,
    DEFAULT_WEEKDAY_START_TIME,
    DEFAULT_WEEKEND_PUSH_ENABLED,
    DEFAULT_WEEKEND_START_TIME,
    DOMAIN,
)

_IMPORTANCE_OPTIONS = ["high", "normal", "low"]
_ASSIGNMENT_OPTIONS = ["random", "assigned"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _notify_services(hass: HomeAssistant) -> list[str]:
    """Return the available ``notify.*`` service ids, sorted."""
    services = hass.services.async_services().get("notify", {})
    return sorted(f"notify.{name}" for name in services)


def _normalise_time(value: str) -> str:
    """Normalise a selector time (``HH:MM:SS``) to ``HH:MM``."""
    return value[:5]


def _persons_schema(default: list[str] | None) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_ENABLED_PERSONS, default=default or []
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="person", multiple=True)
            )
        }
    )


def _person_settings_schema(
    hass: HomeAssistant, defaults: dict[str, Any]
) -> vol.Schema:
    notify_options = _notify_services(hass)
    return vol.Schema(
        {
            vol.Required(
                CONF_NOTIFY_SERVICE,
                default=defaults.get(CONF_NOTIFY_SERVICE, vol.UNDEFINED),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=notify_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            ),
            vol.Required(
                CONF_PRESENCE_REQUIRED,
                default=defaults.get(CONF_PRESENCE_REQUIRED, DEFAULT_PRESENCE_REQUIRED),
            ): bool,
            vol.Required(
                CONF_WEEKDAY_PUSH_ENABLED,
                default=defaults.get(
                    CONF_WEEKDAY_PUSH_ENABLED, DEFAULT_WEEKDAY_PUSH_ENABLED
                ),
            ): bool,
            vol.Required(
                CONF_WEEKEND_PUSH_ENABLED,
                default=defaults.get(
                    CONF_WEEKEND_PUSH_ENABLED, DEFAULT_WEEKEND_PUSH_ENABLED
                ),
            ): bool,
        }
    )


def _schedule_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_WEEKDAY_START_TIME,
                default=defaults.get(
                    CONF_WEEKDAY_START_TIME, DEFAULT_WEEKDAY_START_TIME
                ),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_WEEKEND_START_TIME,
                default=defaults.get(
                    CONF_WEEKEND_START_TIME, DEFAULT_WEEKEND_START_TIME
                ),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_DAY_END_TIME,
                default=defaults.get(CONF_DAY_END_TIME, DEFAULT_DAY_END_TIME),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_MAX_TASKS_PER_PERSON_PER_DAY,
                default=defaults.get(
                    CONF_MAX_TASKS_PER_PERSON_PER_DAY,
                    DEFAULT_MAX_TASKS_PER_PERSON_PER_DAY,
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
        }
    )


def _todo_schema(defaults: dict[str, Any]) -> vol.Schema:
    import_defaults = defaults.get(CONF_TODO_IMPORT_DEFAULTS, {})
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_TODO_ENABLED, default=defaults.get(CONF_TODO_ENABLED, False)
        ): bool,
        vol.Optional(
            CONF_TODO_ENTITY_ID,
            description={"suggested_value": defaults.get(CONF_TODO_ENTITY_ID)},
        ): selector.EntitySelector(selector.EntitySelectorConfig(domain="todo")),
        vol.Required(
            CONF_TODO_IMPORT_NEW_ITEMS,
            default=defaults.get(CONF_TODO_IMPORT_NEW_ITEMS, True),
        ): bool,
        vol.Required(
            CONF_TODO_SYNC_FROM_TODO,
            default=defaults.get(CONF_TODO_SYNC_FROM_TODO, True),
        ): bool,
        vol.Required(
            CONF_TODO_SYNC_TO_TODO,
            default=defaults.get(CONF_TODO_SYNC_TO_TODO, True),
        ): bool,
        vol.Required(
            CONF_IMPORT_ROOM,
            default=import_defaults.get(CONF_IMPORT_ROOM, DEFAULT_IMPORT_ROOM),
        ): str,
        vol.Required(
            CONF_IMPORT_CATEGORY,
            default=import_defaults.get(CONF_IMPORT_CATEGORY, DEFAULT_IMPORT_CATEGORY),
        ): str,
        vol.Required(
            CONF_IMPORT_IMPORTANCE,
            default=import_defaults.get(
                CONF_IMPORT_IMPORTANCE, DEFAULT_IMPORT_IMPORTANCE
            ),
        ): vol.In(_IMPORTANCE_OPTIONS),
        vol.Required(
            CONF_IMPORT_ASSIGNMENT_MODE,
            default=import_defaults.get(
                CONF_IMPORT_ASSIGNMENT_MODE, DEFAULT_IMPORT_ASSIGNMENT_MODE
            ),
        ): vol.In(_ASSIGNMENT_OPTIONS),
    }
    return vol.Schema(schema)


def _calendar_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_CALENDAR_ENABLED,
                default=defaults.get(CONF_CALENDAR_ENABLED, False),
            ): bool,
            vol.Optional(
                CONF_CALENDAR_ENTITY_ID,
                description={"suggested_value": defaults.get(CONF_CALENDAR_ENTITY_ID)},
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="calendar")
            ),
            vol.Optional(
                CONF_CALENDAR_MATCH_SUMMARY_CONTAINS,
                default=defaults.get(CONF_CALENDAR_MATCH_SUMMARY_CONTAINS, ""),
            ): str,
            vol.Required(
                CONF_CALENDAR_DUE_OFFSET_DAYS,
                default=defaults.get(
                    CONF_CALENDAR_DUE_OFFSET_DAYS, DEFAULT_CALENDAR_DUE_OFFSET_DAYS
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=-14, max=14)),
        }
    )


def _build_todo_config(user_input: dict[str, Any]) -> dict[str, Any]:
    """Assemble the nested ``todo_sync`` config from a flat to-do form."""
    return {
        CONF_TODO_ENABLED: user_input[CONF_TODO_ENABLED],
        CONF_TODO_ENTITY_ID: user_input.get(CONF_TODO_ENTITY_ID),
        CONF_TODO_IMPORT_NEW_ITEMS: user_input[CONF_TODO_IMPORT_NEW_ITEMS],
        CONF_TODO_SYNC_FROM_TODO: user_input[CONF_TODO_SYNC_FROM_TODO],
        CONF_TODO_SYNC_TO_TODO: user_input[CONF_TODO_SYNC_TO_TODO],
        CONF_TODO_IMPORT_DEFAULTS: {
            CONF_IMPORT_ROOM: user_input[CONF_IMPORT_ROOM],
            CONF_IMPORT_CATEGORY: user_input[CONF_IMPORT_CATEGORY],
            CONF_IMPORT_IMPORTANCE: user_input[CONF_IMPORT_IMPORTANCE],
            CONF_IMPORT_ASSIGNMENT_MODE: user_input[CONF_IMPORT_ASSIGNMENT_MODE],
        },
    }


def _build_calendar_config(user_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Assemble the ``calendar_sources`` list from a flat calendar form."""
    if not user_input[CONF_CALENDAR_ENABLED] or not user_input.get(
        CONF_CALENDAR_ENTITY_ID
    ):
        return []
    raw = user_input.get(CONF_CALENDAR_MATCH_SUMMARY_CONTAINS, "") or ""
    summary_contains = [part.strip() for part in raw.split(",") if part.strip()]
    return [
        {
            CONF_CALENDAR_ENTITY_ID: user_input[CONF_CALENDAR_ENTITY_ID],
            CONF_CALENDAR_ENABLED: True,
            CONF_CALENDAR_MATCH_SUMMARY_CONTAINS: summary_contains,
            CONF_CALENDAR_DUE_OFFSET_DAYS: user_input[CONF_CALENDAR_DUE_OFFSET_DAYS],
        }
    ]


# ---------------------------------------------------------------------------
# Config flow
# ---------------------------------------------------------------------------
class ChoreFlowConfigFlow(ConfigFlow, domain=DOMAIN):
    """Initial multi-step setup of ChoreFlow."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._person_settings: dict[str, dict[str, Any]] = {}
        self._person_queue: list[str] = []
        self._current_person: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_NAME] = user_input[CONF_NAME]
            return await self.async_step_persons()
        schema = vol.Schema({vol.Required(CONF_NAME, default=DEFAULT_NAME): str})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_persons(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            persons = user_input[CONF_ENABLED_PERSONS]
            if not persons:
                errors["base"] = "no_persons"
            else:
                self._data[CONF_ENABLED_PERSONS] = persons
                self._person_queue = list(persons)
                return await self.async_step_person_config()
        return self.async_show_form(
            step_id="persons",
            data_schema=_persons_schema(None),
            errors=errors,
        )

    async def async_step_person_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None and self._current_person is not None:
            notify_service = user_input[CONF_NOTIFY_SERVICE]
            if notify_service not in _notify_services(self.hass):
                errors["base"] = "notify_not_found"
            else:
                self._person_settings[self._current_person] = user_input
                self._current_person = None

        if not errors:
            if self._person_queue:
                self._current_person = self._person_queue.pop(0)
            else:
                self._data[CONF_PERSON_SETTINGS] = self._person_settings
                return await self.async_step_schedule()

        person = self._current_person
        return self.async_show_form(
            step_id="person_config",
            data_schema=_person_settings_schema(
                self.hass, self._person_settings.get(person or "", {})
            ),
            errors=errors,
            description_placeholders={"person": person or ""},
        )

    async def async_step_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_WEEKDAY_START_TIME] = _normalise_time(
                user_input[CONF_WEEKDAY_START_TIME]
            )
            self._data[CONF_WEEKEND_START_TIME] = _normalise_time(
                user_input[CONF_WEEKEND_START_TIME]
            )
            self._data[CONF_DAY_END_TIME] = _normalise_time(
                user_input[CONF_DAY_END_TIME]
            )
            self._data[CONF_MAX_TASKS_PER_PERSON_PER_DAY] = user_input[
                CONF_MAX_TASKS_PER_PERSON_PER_DAY
            ]
            return await self.async_step_todo()
        return self.async_show_form(
            step_id="schedule", data_schema=_schedule_schema({})
        )

    async def async_step_todo(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_TODO_SYNC] = _build_todo_config(user_input)
            return await self.async_step_calendar()
        return self.async_show_form(step_id="todo", data_schema=_todo_schema({}))

    async def async_step_calendar(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_CALENDAR_SOURCES] = _build_calendar_config(user_input)
            return self.async_create_entry(
                title=self._data.get(CONF_NAME, DEFAULT_NAME), data=self._data
            )
        return self.async_show_form(
            step_id="calendar", data_schema=_calendar_schema({})
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> ChoreFlowOptionsFlow:
        return ChoreFlowOptionsFlow()


# ---------------------------------------------------------------------------
# Options flow
# ---------------------------------------------------------------------------
class ChoreFlowOptionsFlow(OptionsFlow):
    """Change any setting after setup; the entry reloads on save (§5.5)."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._person_settings: dict[str, dict[str, Any]] = {}
        self._person_queue: list[str] = []
        self._current_person: str | None = None

    @property
    def _current(self) -> dict[str, Any]:
        """Merged current config: options override the original data."""
        return {**self.config_entry.data, **self.config_entry.options}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self.async_step_persons(user_input)

    async def async_step_persons(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            persons = user_input[CONF_ENABLED_PERSONS]
            if not persons:
                errors["base"] = "no_persons"
            else:
                self._data[CONF_ENABLED_PERSONS] = persons
                self._person_queue = list(persons)
                return await self.async_step_person_config()
        return self.async_show_form(
            step_id="persons",
            data_schema=_persons_schema(self._current.get(CONF_ENABLED_PERSONS)),
            errors=errors,
        )

    async def async_step_person_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        existing = self._current.get(CONF_PERSON_SETTINGS, {})
        if user_input is not None and self._current_person is not None:
            if user_input[CONF_NOTIFY_SERVICE] not in _notify_services(self.hass):
                errors["base"] = "notify_not_found"
            else:
                self._person_settings[self._current_person] = user_input
                self._current_person = None

        if not errors:
            if self._person_queue:
                self._current_person = self._person_queue.pop(0)
            else:
                self._data[CONF_PERSON_SETTINGS] = self._person_settings
                return await self.async_step_schedule()

        person = self._current_person or ""
        return self.async_show_form(
            step_id="person_config",
            data_schema=_person_settings_schema(
                self.hass,
                self._person_settings.get(person) or existing.get(person, {}),
            ),
            errors=errors,
            description_placeholders={"person": person},
        )

    async def async_step_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_WEEKDAY_START_TIME] = _normalise_time(
                user_input[CONF_WEEKDAY_START_TIME]
            )
            self._data[CONF_WEEKEND_START_TIME] = _normalise_time(
                user_input[CONF_WEEKEND_START_TIME]
            )
            self._data[CONF_DAY_END_TIME] = _normalise_time(
                user_input[CONF_DAY_END_TIME]
            )
            self._data[CONF_MAX_TASKS_PER_PERSON_PER_DAY] = user_input[
                CONF_MAX_TASKS_PER_PERSON_PER_DAY
            ]
            return await self.async_step_todo()
        return self.async_show_form(
            step_id="schedule", data_schema=_schedule_schema(self._current)
        )

    async def async_step_todo(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_TODO_SYNC] = _build_todo_config(user_input)
            return await self.async_step_calendar()
        todo_defaults = dict(self._current.get(CONF_TODO_SYNC, {}))
        return self.async_show_form(
            step_id="todo", data_schema=_todo_schema(todo_defaults)
        )

    async def async_step_calendar(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_CALENDAR_SOURCES] = _build_calendar_config(user_input)
            return self.async_create_entry(title="", data=self._data)
        sources = self._current.get(CONF_CALENDAR_SOURCES) or [{}]
        first = sources[0]
        defaults = {
            CONF_CALENDAR_ENABLED: first.get(CONF_CALENDAR_ENABLED, False),
            CONF_CALENDAR_ENTITY_ID: first.get(CONF_CALENDAR_ENTITY_ID),
            CONF_CALENDAR_MATCH_SUMMARY_CONTAINS: ", ".join(
                first.get(CONF_CALENDAR_MATCH_SUMMARY_CONTAINS, [])
            ),
            CONF_CALENDAR_DUE_OFFSET_DAYS: first.get(
                CONF_CALENDAR_DUE_OFFSET_DAYS, DEFAULT_CALENDAR_DUE_OFFSET_DAYS
            ),
        }
        return self.async_show_form(
            step_id="calendar", data_schema=_calendar_schema(defaults)
        )
