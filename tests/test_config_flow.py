"""Config + options flow tests for ChoreFlow (Pflichtenheft §11.2, P3a).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN

_PERSON = "person.niklas"
_NOTIFY = "notify.mobile_app_niklas"

_FULL_DATA: dict[str, Any] = {
    "name": "Home",
    "enabled_persons": [_PERSON],
    "person_settings": {
        _PERSON: {
            "notify_service": _NOTIFY,
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        }
    },
    "weekday_start_time": "17:30",
    "weekend_start_time": "10:00",
    "day_end_time": "20:00",
    "max_tasks_per_person_per_day": 5,
    "todo_sync": {"enabled": False},
    "calendar_sources": [],
}


def _register_prereqs(hass: HomeAssistant) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)


async def _drive_to_create(hass: HomeAssistant, flow_id: str) -> dict[str, Any]:
    """Walk persons → person_config → schedule → todo → calendar → create."""
    result = await hass.config_entries.flow.async_configure(
        flow_id, {"enabled_persons": [_PERSON]}
    )
    assert result["step_id"] == "person_config"
    result = await hass.config_entries.flow.async_configure(
        flow_id,
        {
            "notify_service": _NOTIFY,
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["step_id"] == "schedule"
    result = await hass.config_entries.flow.async_configure(
        flow_id,
        {
            "weekday_start_time": "17:30:00",
            "weekend_start_time": "10:00:00",
            "day_end_time": "20:00:00",
            "max_tasks_per_person_per_day": 5,
        },
    )
    assert result["step_id"] == "todo"
    result = await hass.config_entries.flow.async_configure(
        flow_id,
        {
            "enabled": False,
            "import_new_items": True,
            "sync_completion_from_todo": True,
            "sync_completion_to_todo": True,
            "room": "Allgemein",
            "category": "Allgemein",
            "importance": "normal",
            "assignment_mode": "random",
        },
    )
    assert result["step_id"] == "calendar"
    return await hass.config_entries.flow.async_configure(
        flow_id,
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )


async def test_full_config_flow(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Home"}
    )
    assert result["step_id"] == "persons"

    result = await _drive_to_create(hass, result["flow_id"])
    assert result["type"] == FlowResultType.CREATE_ENTRY
    data = result["data"]
    assert data["name"] == "Home"
    assert data["enabled_persons"] == [_PERSON]
    assert data["person_settings"][_PERSON]["notify_service"] == _NOTIFY
    assert data["weekday_start_time"] == "17:30"  # normalised from HH:MM:SS
    assert data["max_tasks_per_person_per_day"] == 5
    assert data["todo_sync"]["enabled"] is False
    assert data["calendar_sources"] == []


async def test_persons_step_requires_a_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Home"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"enabled_persons": []}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "no_persons"}


async def test_person_config_rejects_unknown_notify(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Home"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"enabled_persons": [_PERSON]}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "notify_service": "notify.does_not_exist",
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "notify_not_found"}


async def test_single_instance_only(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    MockConfigEntry(domain=DOMAIN, data={}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow_updates_schedule(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    entry = MockConfigEntry(domain=DOMAIN, data=_FULL_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "persons"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"enabled_persons": [_PERSON]}
    )
    assert result["step_id"] == "person_config"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "notify_service": _NOTIFY,
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": False,
        },
    )
    assert result["step_id"] == "schedule"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "weekday_start_time": "18:00:00",
            "weekend_start_time": "09:00:00",
            "day_end_time": "21:00:00",
            "max_tasks_per_person_per_day": 3,
        },
    )
    assert result["step_id"] == "todo"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "enabled": False,
            "import_new_items": True,
            "sync_completion_from_todo": True,
            "sync_completion_to_todo": True,
            "room": "Allgemein",
            "category": "Allgemein",
            "importance": "normal",
            "assignment_mode": "random",
        },
    )
    assert result["step_id"] == "calendar"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options["weekday_start_time"] == "18:00"
    assert entry.options["max_tasks_per_person_per_day"] == 3
    assert entry.options["person_settings"][_PERSON]["weekend_push_enabled"] is False

    # Saving options triggers a reload; let it finish so the reloaded
    # coordinator's refresh-interval timer is cancelled cleanly at teardown
    # (otherwise it lingers past the test).
    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
