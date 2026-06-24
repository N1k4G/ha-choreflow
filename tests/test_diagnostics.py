"""Diagnostics tests for ChoreFlow (Pflichtenheft §11.2, P3b).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN
from custom_components.choreflow.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .factories import config_entry_data

_PERSON = "person.niklas"


async def test_diagnostics_redacts_notify_and_reports_counts(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)

    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, entry)

    notify = result["entry"]["data"]["person_settings"][_PERSON]["notify_service"]
    assert notify == "**REDACTED**"
    assert result["coordinator"]["open_tasks"] == 0
    assert result["store"]["open_instances"] == 0
    assert "task_rules" in result["store"]
