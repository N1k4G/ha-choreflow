"""Logbook integration for ChoreFlow (Pflichtenheft §8).

Describes the ``choreflow_event`` bus events (fired alongside the SQLite log in
P3c) so ChoreFlow actions appear in the Home Assistant logbook.
"""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.core import Event, HomeAssistant, callback

from .const import DOMAIN, LOGBOOK_EVENT


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[[str, str, Callable[[Event], dict[str, str]]], None],
) -> None:
    """Register the ChoreFlow logbook event describer."""

    @callback
    def describe(event: Event) -> dict[str, str]:
        data = event.data
        event_type = str(data.get("event_type", "event"))
        title = str(data.get("title", "")).strip()
        message = f"{event_type}: {title}" if title else event_type
        described: dict[str, str] = {
            "name": "ChoreFlow",
            "message": message,
        }
        person = data.get("person_entity")
        if person:
            described["entity_id"] = str(person)
        return described

    async_describe_event(DOMAIN, LOGBOOK_EVENT, describe)
