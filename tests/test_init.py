"""Entry lifecycle tests for ChoreFlow (Pflichtenheft §11.2, P3a).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    DATA_LOG_STORE,
    DATA_STORE,
    DB_FILENAME,
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


async def test_remove_entry_deletes_state_but_keeps_history(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "Home"})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    store = hass.data[DOMAIN][entry.entry_id][DATA_STORE]
    await store.async_save()
    database_path = Path(hass.config.path(DB_FILENAME))
    assert database_path.exists()

    removed_keys: list[str] = []

    async def capture_remove(state_store: Any) -> None:
        removed_keys.append(state_store.key)

    with patch(
        "custom_components.choreflow.store._StateStore.async_remove",
        new=capture_remove,
    ):
        assert await hass.config_entries.async_remove(entry.entry_id)
        await hass.async_block_till_done()

    assert removed_keys == [f"choreflow.{entry.entry_id}"]
    assert database_path.exists()
