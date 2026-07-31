"""Repair-issue tests for ChoreFlow (Pflichtenheft §11.2, P3b).

Requires Home Assistant; runs in CI (Linux), not on native Windows.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.choreflow.const import DOMAIN

from .factories import config_entry_data

_PERSON = "person.niklas"
_NOTIFY = "notify.mobile_app_niklas"


async def test_issues_created_when_person_and_notify_missing(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    # Neither the person entity nor the notify service exist.
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    assert (
        registry.async_get_issue(DOMAIN, f"{entry.entry_id}_missing_person_{_PERSON}")
        is not None
    )
    assert (
        registry.async_get_issue(
            DOMAIN, f"{entry.entry_id}_missing_notify_service_{_PERSON}"
        )
        is not None
    )


async def test_no_issues_when_person_and_notify_present(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    hass.states.async_set(_PERSON, "home")
    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)

    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    assert (
        registry.async_get_issue(DOMAIN, f"{entry.entry_id}_missing_person_{_PERSON}")
        is None
    )
    assert (
        registry.async_get_issue(
            DOMAIN, f"{entry.entry_id}_missing_notify_service_{_PERSON}"
        )
        is None
    )


async def test_notify_issue_tracks_service_lifecycle_without_reload(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    hass.states.async_set(_PERSON, "home")
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    issue_id = f"{entry.entry_id}_missing_notify_service_{_PERSON}"
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    hass.services.async_register("notify", "mobile_app_niklas", lambda call: None)
    await hass.async_block_till_done()
    assert registry.async_get_issue(DOMAIN, issue_id) is None

    hass.services.async_remove("notify", "mobile_app_niklas")
    await hass.async_block_till_done()
    assert registry.async_get_issue(DOMAIN, issue_id) is not None


async def test_entry_removal_clears_owned_repair_issues(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=config_entry_data())
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    person_issue_id = f"{entry.entry_id}_missing_person_{_PERSON}"
    notify_issue_id = f"{entry.entry_id}_missing_notify_service_{_PERSON}"
    assert registry.async_get_issue(DOMAIN, person_issue_id) is not None
    assert registry.async_get_issue(DOMAIN, notify_issue_id) is not None

    assert await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert registry.async_get_issue(DOMAIN, person_issue_id) is None
    assert registry.async_get_issue(DOMAIN, notify_issue_id) is None
