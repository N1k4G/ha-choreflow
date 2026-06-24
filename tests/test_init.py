"""Entry lifecycle tests for ChoreFlow (Pflichtenheft §11.2, P3a).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    DATA_LOG_STORE,
    DATA_STORE,
    DOMAIN,
)


async def test_setup_and_unload_entry(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "Home"})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    data = hass.data[DOMAIN][entry.entry_id]
    assert DATA_STORE in data
    assert DATA_LOG_STORE in data

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_options_update_triggers_reload(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "Home"})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Updating options fires the update listener which reloads the entry.
    hass.config_entries.async_update_entry(entry, options={"day_end_time": "21:00"})
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
