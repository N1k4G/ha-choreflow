"""Shared entity helpers for ChoreFlow (Pflichtenheft §5.6)."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DEFAULT_NAME, DEVICE_MANUFACTURER, DEVICE_MODEL, DOMAIN


def build_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Group all ChoreFlow entities under one device per config entry."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title or DEFAULT_NAME,
        manufacturer=DEVICE_MANUFACTURER,
        model=DEVICE_MODEL,
        entry_type=DeviceEntryType.SERVICE,
    )


def person_slug(person_entity: str) -> str:
    """``person.niklas`` → ``niklas`` for stable unique ids."""
    return person_entity.split(".", 1)[-1]
