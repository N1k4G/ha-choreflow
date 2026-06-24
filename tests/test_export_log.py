"""export_log service tests for ChoreFlow (Pflichtenheft §11.2, P6).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

import csv
import glob
import json
import os

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import (
    DOMAIN,
    EXPORT_DIRNAME,
    SERVICE_CREATE_TASK,
    SERVICE_EXPORT_LOG,
)

from .factories import config_entry_data

_PERSON = "person.niklas"


def _prereqs(hass: HomeAssistant) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


async def _exported_files(hass: HomeAssistant, ext: str) -> list[str]:
    pattern = os.path.join(hass.config.path(EXPORT_DIRNAME), f"*.{ext}")
    return await hass.async_add_executor_job(lambda: sorted(glob.glob(pattern)))


async def test_export_log_json(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)
    await hass.services.async_call(
        DOMAIN, SERVICE_CREATE_TASK, {"title": "Wipe sink"}, blocking=True
    )

    await hass.services.async_call(
        DOMAIN, SERVICE_EXPORT_LOG, {"format": "json"}, blocking=True
    )

    files = await _exported_files(hass, "json")
    assert files, "no JSON export written"
    content = await hass.async_add_executor_job(_read, files[-1])
    data = json.loads(content)
    assert any(row["event_type"] == "task_created" for row in data)


async def test_export_log_csv(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    _prereqs(hass)
    await _setup(hass)
    await hass.services.async_call(
        DOMAIN, SERVICE_CREATE_TASK, {"title": "Wipe sink"}, blocking=True
    )

    await hass.services.async_call(
        DOMAIN, SERVICE_EXPORT_LOG, {"format": "csv"}, blocking=True
    )

    files = await _exported_files(hass, "csv")
    assert files, "no CSV export written"
    content = await hass.async_add_executor_job(_read, files[-1])
    rows = list(csv.DictReader(content.splitlines()))
    assert rows
    assert "event_id" in rows[0]
