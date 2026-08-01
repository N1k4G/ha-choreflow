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
    return await _drive_schedule_to_create(hass, flow_id)


async def _drive_schedule_to_create(
    hass: HomeAssistant, flow_id: str
) -> dict[str, Any]:
    """Walk schedule → todo → calendar → create."""
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


def _todo_input(
    assignment_mode: str, assignment_person: str | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": True,
        "entity_id": "todo.household",
        "import_new_items": True,
        "sync_completion_from_todo": True,
        "sync_completion_to_todo": True,
        "room": "General",
        "category": "General",
        "importance": "normal",
        "assignment_mode": assignment_mode,
    }
    if assignment_person is not None:
        result["assignment_person"] = assignment_person
    return result


async def _drive_initial_to_todo(hass: HomeAssistant) -> dict[str, Any]:
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
            "notify_service": _NOTIFY,
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    return await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "weekday_start_time": "17:30:00",
            "weekend_start_time": "10:00:00",
            "day_end_time": "20:00:00",
            "max_tasks_per_person_per_day": 5,
        },
    )


async def _drive_options_to_todo(
    hass: HomeAssistant, entry: MockConfigEntry
) -> dict[str, Any]:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"enabled_persons": [_PERSON]}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "notify_service": _NOTIFY,
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    return await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "weekday_start_time": "17:30:00",
            "weekend_start_time": "10:00:00",
            "day_end_time": "20:00:00",
            "max_tasks_per_person_per_day": 5,
        },
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


async def test_initial_flow_validates_and_persists_assigned_import_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    result = await _drive_initial_to_todo(hass)
    assert result["step_id"] == "todo"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _todo_input("assigned")
    )
    assert result["step_id"] == "todo"
    assert result["errors"] == {
        "assignment_person": "import_assignment_person_required"
    }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _todo_input("assigned", "person.partner")
    )
    assert result["step_id"] == "todo"
    assert result["errors"] == {
        "assignment_person": "import_assignment_person_not_enabled"
    }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], _todo_input("assigned", _PERSON)
    )
    assert result["step_id"] == "calendar"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    defaults = result["data"]["todo_sync"]["import_defaults"]
    assert defaults["assignment_mode"] == "assigned"
    assert defaults["assignment_person"] == _PERSON

    # Creating the entry starts an initial to-do sync as a background task.
    # Drain it explicitly before teardown so the test does not leak the task.
    await hass.async_block_till_done(wait_background_tasks=True)
    assert await hass.config_entries.async_unload(result["result"].entry_id)
    await hass.async_block_till_done()


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


async def test_person_config_accepts_unregistered_notify_and_rejects_malformed(
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
            "notify_service": "mobile_app_missing_prefix",
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "notify_not_found"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "notify_service": "notify.mobile_app_not_yet_registered",
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["step_id"] == "schedule"
    result = await _drive_schedule_to_create(hass, result["flow_id"])
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert (
        result["data"]["person_settings"][_PERSON]["notify_service"]
        == "notify.mobile_app_not_yet_registered"
    )


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


async def test_options_flow_validates_and_persists_assigned_import_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    entry = MockConfigEntry(domain=DOMAIN, data=_FULL_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    result = await _drive_options_to_todo(hass, entry)
    assert result["step_id"] == "todo"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _todo_input("assigned")
    )
    assert result["errors"] == {
        "assignment_person": "import_assignment_person_required"
    }
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _todo_input("assigned", "person.partner")
    )
    assert result["errors"] == {
        "assignment_person": "import_assignment_person_not_enabled"
    }

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _todo_input("assigned", _PERSON)
    )
    assert result["step_id"] == "calendar"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    defaults = entry.options["todo_sync"]["import_defaults"]
    assert defaults["assignment_mode"] == "assigned"
    assert defaults["assignment_person"] == _PERSON

    await hass.async_block_till_done(wait_background_tasks=True)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_options_flow_random_clears_stale_assignment_person(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    entry = MockConfigEntry(domain=DOMAIN, data=_FULL_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done(wait_background_tasks=True)
    result = await _drive_options_to_todo(hass, entry)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _todo_input("random", _PERSON)
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    defaults = entry.options["todo_sync"]["import_defaults"]
    assert defaults["assignment_mode"] == "random"
    assert defaults["assignment_person"] is None

    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_options_flow_accepts_unregistered_notify_and_rejects_malformed(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _register_prereqs(hass)
    entry = MockConfigEntry(domain=DOMAIN, data=_FULL_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"enabled_persons": [_PERSON]}
    )
    assert result["step_id"] == "person_config"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "notify_service": "persistent_notification.create",
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "notify_not_found"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "notify_service": "notify.mobile_app_not_yet_registered",
            "presence_required": True,
            "weekday_push_enabled": True,
            "weekend_push_enabled": True,
        },
    )
    assert result["step_id"] == "schedule"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "weekday_start_time": "17:30:00",
            "weekend_start_time": "10:00:00",
            "day_end_time": "20:00:00",
            "max_tasks_per_person_per_day": 5,
        },
    )
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
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"enabled": False, "summary_contains": "", "due_offset_days": -1},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert (
        entry.options["person_settings"][_PERSON]["notify_service"]
        == "notify.mobile_app_not_yet_registered"
    )

    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
