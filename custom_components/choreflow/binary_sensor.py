"""Binary sensors for ChoreFlow (Pflichtenheft §5.6, Lastenheft §18.2)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_SETTINGS, DOMAIN
from .coordinator import ChoreFlowCoordinator, PersonStats
from .entity import build_device_info, person_slug
from .settings import ChoreFlowSettings


@dataclass(frozen=True, kw_only=True)
class PersonBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[PersonStats], bool]


PERSON_BINARY_SENSORS: tuple[PersonBinaryDescription, ...] = (
    PersonBinaryDescription(
        key="has_due_tasks",
        translation_key="person_has_due_tasks",
        value_fn=lambda stats: stats.has_due,
    ),
    PersonBinaryDescription(
        key="chain_active",
        translation_key="person_chain_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda stats: stats.chain_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ChoreFlow binary sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ChoreFlowCoordinator = data[DATA_COORDINATOR]
    settings: ChoreFlowSettings = data[DATA_SETTINGS]

    entities: list[BinarySensorEntity] = []
    for person in settings.enabled_persons:
        friendly = _friendly_name(hass, person)
        entities.extend(
            PersonBinarySensor(coordinator, entry, person, friendly, desc)
            for desc in PERSON_BINARY_SENSORS
        )
    async_add_entities(entities)


def _friendly_name(hass: HomeAssistant, person: str) -> str:
    state = hass.states.get(person)
    if state and state.name:
        return state.name
    return person_slug(person).replace("_", " ").title()


class PersonBinarySensor(CoordinatorEntity[ChoreFlowCoordinator], BinarySensorEntity):
    """A per-person ChoreFlow status binary sensor."""

    _attr_has_entity_name = True
    entity_description: PersonBinaryDescription

    def __init__(
        self,
        coordinator: ChoreFlowCoordinator,
        entry: ConfigEntry,
        person: str,
        friendly_name: str,
        description: PersonBinaryDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._person = person
        self._attr_translation_placeholders = {"person": friendly_name}
        self._attr_unique_id = (
            f"{entry.entry_id}_{person_slug(person)}_{description.key}"
        )
        self._attr_device_info = build_device_info(entry)

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if data is None:
            return None
        stats = data.per_person.get(self._person)
        if stats is None:
            return None
        return self.entity_description.value_fn(stats)
