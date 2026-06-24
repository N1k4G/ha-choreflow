"""Sensors for ChoreFlow (Pflichtenheft §5.6, Lastenheft §18).

Global counts and per-person counts, all read from the coordinator snapshot —
no entity-level polling.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_SETTINGS, DOMAIN
from .coordinator import ChoreFlowCoordinator, ChoreFlowData, PersonStats
from .entity import build_device_info, person_slug
from .settings import ChoreFlowSettings

_UNIT_TASKS = "tasks"


@dataclass(frozen=True, kw_only=True)
class GlobalSensorDescription(SensorEntityDescription):
    value_fn: Callable[[ChoreFlowData], int]
    attrs_fn: Callable[[ChoreFlowData], dict[str, Any]] | None = None


@dataclass(frozen=True, kw_only=True)
class PersonSensorDescription(SensorEntityDescription):
    value_fn: Callable[[PersonStats], int]


GLOBAL_SENSORS: tuple[GlobalSensorDescription, ...] = (
    GlobalSensorDescription(
        key="open_tasks",
        translation_key="open_tasks",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.open_tasks,
        attrs_fn=lambda data: {"open_tasks": data.open_task_list},
    ),
    GlobalSensorDescription(
        key="due_tasks",
        translation_key="due_tasks",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.due_tasks,
    ),
    GlobalSensorDescription(
        key="overdue_tasks",
        translation_key="overdue_tasks",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.overdue_tasks,
    ),
    GlobalSensorDescription(
        key="completed_today",
        translation_key="completed_today",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.completed_today,
    ),
    GlobalSensorDescription(
        key="completed_this_week",
        translation_key="completed_this_week",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.completed_this_week,
    ),
    GlobalSensorDescription(
        key="active_chains",
        translation_key="active_chains",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.active_chains,
    ),
)

PERSON_SENSORS: tuple[PersonSensorDescription, ...] = (
    PersonSensorDescription(
        key="open_tasks",
        translation_key="person_open_tasks",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda stats: stats.open,
    ),
    PersonSensorDescription(
        key="due_tasks",
        translation_key="person_due_tasks",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda stats: stats.due,
    ),
    PersonSensorDescription(
        key="completed_today",
        translation_key="person_completed_today",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda stats: stats.completed_today,
    ),
    PersonSensorDescription(
        key="tasks_remaining_today",
        translation_key="person_tasks_remaining_today",
        native_unit_of_measurement=_UNIT_TASKS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda stats: stats.remaining_today,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ChoreFlow sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ChoreFlowCoordinator = data[DATA_COORDINATOR]
    settings: ChoreFlowSettings = data[DATA_SETTINGS]

    entities: list[SensorEntity] = [
        GlobalSensor(coordinator, entry, desc) for desc in GLOBAL_SENSORS
    ]
    for person in settings.enabled_persons:
        friendly = _friendly_name(hass, person)
        entities.extend(
            PersonSensor(coordinator, entry, person, friendly, desc)
            for desc in PERSON_SENSORS
        )
    async_add_entities(entities)


def _friendly_name(hass: HomeAssistant, person: str) -> str:
    state = hass.states.get(person)
    if state and state.name:
        return state.name
    return person_slug(person).replace("_", " ").title()


class GlobalSensor(CoordinatorEntity[ChoreFlowCoordinator], SensorEntity):
    """A global ChoreFlow count sensor."""

    _attr_has_entity_name = True
    entity_description: GlobalSensorDescription

    def __init__(
        self,
        coordinator: ChoreFlowCoordinator,
        entry: ConfigEntry,
        description: GlobalSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        if data is None or self.entity_description.attrs_fn is None:
            return {}
        return self.entity_description.attrs_fn(data)


class PersonSensor(CoordinatorEntity[ChoreFlowCoordinator], SensorEntity):
    """A per-person ChoreFlow count sensor."""

    _attr_has_entity_name = True
    entity_description: PersonSensorDescription

    def __init__(
        self,
        coordinator: ChoreFlowCoordinator,
        entry: ConfigEntry,
        person: str,
        friendly_name: str,
        description: PersonSensorDescription,
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
    def native_value(self) -> int | None:
        data = self.coordinator.data
        if data is None:
            return None
        stats = data.per_person.get(self._person)
        if stats is None:
            return None
        return self.entity_description.value_fn(stats)
