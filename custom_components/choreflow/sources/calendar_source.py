"""Calendar-driven high tasks for ChoreFlow (Pflichtenheft §7, Lastenheft §15).

Reads all-day events from the configured ``calendar.*`` entities, matches them
by summary, and creates ``high`` tasks due ``due_offset_days`` before the event
(default the day before — waste collection). Reconciles on change:

* new matching event → new task (``calendar_task_created``),
* event gone → the still-open task is removed (``calendar_task_removed``),
* changed event → the open task is updated,

while completed tasks stay in the log. An unavailable calendar suspends without
deleting anything and raises a repair issue (§23.4).
"""

from __future__ import annotations

import logging
import re
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from ..const import (
    CONF_CALENDAR_DUE_OFFSET_DAYS,
    CONF_CALENDAR_ENABLED,
    CONF_CALENDAR_ENTITY_ID,
    CONF_CALENDAR_MATCH_SUMMARY_CONTAINS,
    DEFAULT_CALENDAR_CATEGORY,
    DEFAULT_CALENDAR_DUE_OFFSET_DAYS,
    DEFAULT_CALENDAR_PREVIEW_DAYS,
    DEFAULT_CALENDAR_ROOM,
    DOMAIN,
)
from ..models import (
    AssignmentMode,
    CalendarRef,
    ExternalRefs,
    Importance,
    TaskInstance,
    TaskSource,
    TaskStatus,
    UrgencyType,
    VisibilityMode,
)
from ..settings import ChoreFlowSettings

if TYPE_CHECKING:
    from ..coordinator import ChoreFlowCoordinator

_LOGGER = logging.getLogger(__name__)

_ISSUE_CALENDAR_UNAVAILABLE = "calendar_unavailable"


def _sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", value)


def _is_all_day(event: dict[str, Any]) -> bool:
    """All-day events expose a date-only start (no time component)."""
    start = event.get("start", "")
    return isinstance(start, str) and "T" not in start and bool(start)


class CalendarSource:
    """Generates and reconciles calendar-based high tasks."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ChoreFlowCoordinator,
        settings: ChoreFlowSettings,
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self._sources = [
            src
            for src in settings.calendar_sources
            if src.get(CONF_CALENDAR_ENABLED, True) and src.get(CONF_CALENDAR_ENTITY_ID)
        ]

    @property
    def active(self) -> bool:
        return bool(self._sources)

    async def async_sync(self) -> None:
        """Reconcile all configured calendar sources."""
        for source in self._sources:
            await self._sync_source(source)

    # -- per source --------------------------------------------------------
    async def _sync_source(self, source: dict[str, Any]) -> None:
        entity_id: str = source[CONF_CALENDAR_ENTITY_ID]
        keywords = [
            kw.lower()
            for kw in source.get(CONF_CALENDAR_MATCH_SUMMARY_CONTAINS, [])
            if kw
        ]
        offset = source.get(
            CONF_CALENDAR_DUE_OFFSET_DAYS, DEFAULT_CALENDAR_DUE_OFFSET_DAYS
        )
        rule_id = f"cal_{_sanitize(entity_id)}"

        events = await self._fetch_events(entity_id)
        if events is None:
            self._raise_unavailable_issue(entity_id)
            return
        self._clear_unavailable_issue(entity_id)

        desired: dict[str, TaskInstance] = {}
        for event in events:
            if not _is_all_day(event):
                continue
            summary = str(event.get("summary", ""))
            if keywords and not any(kw in summary.lower() for kw in keywords):
                continue
            base_uid = str(event.get("uid") or summary)
            occurrence = str(event.get("recurrence_id") or event["start"])
            event_uid = f"{base_uid}@{occurrence}"
            ref = CalendarRef(
                entity_id=entity_id, event_uid=event_uid, task_rule_id=rule_id
            )
            due = date.fromisoformat(event["start"]) + timedelta(days=offset)
            task_id = f"cal_{_sanitize(ref.dedup_key)}"
            desired[ref.dedup_key] = self._build_instance(task_id, summary, due, ref)

        existing = self._existing_for(entity_id, rule_id)

        # Create or update.
        for key, inst in desired.items():
            current = existing.get(key)
            if current is None:
                await self.coordinator.async_add_calendar_task(inst)
            elif current.status == TaskStatus.OPEN and (
                current.title != inst.title or current.due_date != inst.due_date
            ):
                await self.coordinator.async_update_task(
                    current.id, {"title": inst.title, "due_date": inst.due_date}
                )

        # Remove open tasks whose event disappeared.
        for key, inst in existing.items():
            if key not in desired and inst.status == TaskStatus.OPEN:
                await self.coordinator.async_remove_calendar_task(inst.id)

    # -- helpers -----------------------------------------------------------
    def _existing_for(self, entity_id: str, rule_id: str) -> dict[str, TaskInstance]:
        result: dict[str, TaskInstance] = {}
        for inst in self.coordinator.store.task_instances.values():
            refs = inst.external_refs
            if (
                refs is not None
                and refs.calendar is not None
                and refs.calendar.entity_id == entity_id
                and refs.calendar.task_rule_id == rule_id
            ):
                result[refs.calendar.dedup_key] = inst
        return result

    def _build_instance(
        self, task_id: str, summary: str, due: date, ref: CalendarRef
    ) -> TaskInstance:
        return TaskInstance(
            id=task_id,
            rule_id=ref.task_rule_id,
            title=summary or "Calendar task",
            description=None,
            room=DEFAULT_CALENDAR_ROOM,
            category=DEFAULT_CALENDAR_CATEGORY,
            importance=Importance.HIGH,
            estimated_duration_minutes=None,
            urgency_type=UrgencyType.MANDATORY_DATE,
            due_date=due,
            deadline=due,
            status=TaskStatus.OPEN,
            source=TaskSource.CALENDAR,
            visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
            visibility_persons=[],
            assignment_mode=AssignmentMode.RANDOM,
            assignment_person=None,
            external_refs=ExternalRefs(calendar=ref),
            created_at=self.coordinator.clock.now(),
        )

    async def _fetch_events(self, entity_id: str) -> list[dict[str, Any]] | None:
        """Return events in the preview window, or None when unavailable."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state == "unavailable":
            return None
        start = dt_util.now()
        end = start + timedelta(days=DEFAULT_CALENDAR_PREVIEW_DAYS)
        try:
            response = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": entity_id,
                    "start_date_time": start.isoformat(),
                    "end_date_time": end.isoformat(),
                },
                blocking=True,
                return_response=True,
            )
        except Exception:  # noqa: BLE001 — a calendar failure must not crash setup
            _LOGGER.exception("Failed to read calendar events from %s", entity_id)
            return None
        entity_data = (response or {}).get(entity_id)
        if not isinstance(entity_data, dict):
            return []
        raw_events = entity_data.get("events", [])
        if not isinstance(raw_events, list):
            return []
        return [event for event in raw_events if isinstance(event, dict)]

    def _raise_unavailable_issue(self, entity_id: str) -> None:
        _LOGGER.warning("Calendar %s unavailable; keeping existing tasks", entity_id)
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            f"{_ISSUE_CALENDAR_UNAVAILABLE}_{entity_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=_ISSUE_CALENDAR_UNAVAILABLE,
            translation_placeholders={"entity_id": entity_id},
        )

    def _clear_unavailable_issue(self, entity_id: str) -> None:
        ir.async_delete_issue(
            self.hass, DOMAIN, f"{_ISSUE_CALENDAR_UNAVAILABLE}_{entity_id}"
        )
