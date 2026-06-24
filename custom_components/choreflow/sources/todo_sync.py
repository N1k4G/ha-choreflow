"""To-do list synchronisation for ChoreFlow (Pflichtenheft §6, Lastenheft §16).

ChoreFlow is the source of truth; a mapped ``todo.*`` entity is an import source
and completion mirror. This module:

* imports new open to-do items as one-off tasks (dedup via the item uid),
* completes the matching ChoreFlow task when its to-do item is checked off,
* checks off the to-do item when a synced ChoreFlow task is completed,

and degrades gracefully when the to-do entity is unavailable: it suspends,
raises a repair issue and resumes on the next sync (§23.3).
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from ..const import (
    COMPLETION_SOURCE_TODO,
    CONF_IMPORT_ASSIGNMENT_MODE,
    CONF_IMPORT_CATEGORY,
    CONF_IMPORT_IMPORTANCE,
    CONF_IMPORT_ROOM,
    CONF_TODO_ENABLED,
    CONF_TODO_ENTITY_ID,
    CONF_TODO_IMPORT_DEFAULTS,
    CONF_TODO_IMPORT_NEW_ITEMS,
    CONF_TODO_SYNC_FROM_TODO,
    CONF_TODO_SYNC_TO_TODO,
    DEFAULT_IMPORT_ASSIGNMENT_MODE,
    DEFAULT_IMPORT_CATEGORY,
    DEFAULT_IMPORT_IMPORTANCE,
    DEFAULT_IMPORT_ROOM,
    DOMAIN,
)
from ..models import (
    AssignmentMode,
    ExternalRefs,
    Importance,
    TaskInstance,
    TaskSource,
    TaskStatus,
    TodoRef,
    VisibilityMode,
)
from ..settings import ChoreFlowSettings

if TYPE_CHECKING:
    from ..coordinator import ChoreFlowCoordinator

_LOGGER = logging.getLogger(__name__)

_ISSUE_TODO_UNAVAILABLE = "todo_unavailable"
_STATUS_COMPLETED = "completed"


def _sanitize(uid: str) -> str:
    """Make a to-do uid safe for use inside a task/action id."""
    return re.sub(r"[^A-Za-z0-9]", "-", uid)


class TodoSync:
    """Bidirectional sync between ChoreFlow and one ``todo.*`` entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ChoreFlowCoordinator,
        settings: ChoreFlowSettings,
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        cfg = settings.todo
        self.enabled: bool = cfg.get(CONF_TODO_ENABLED, False)
        self.entity_id: str | None = cfg.get(CONF_TODO_ENTITY_ID)
        self.import_new: bool = cfg.get(CONF_TODO_IMPORT_NEW_ITEMS, True)
        self.sync_from_todo: bool = cfg.get(CONF_TODO_SYNC_FROM_TODO, True)
        self.sync_to_todo: bool = cfg.get(CONF_TODO_SYNC_TO_TODO, True)
        defaults: dict[str, Any] = cfg.get(CONF_TODO_IMPORT_DEFAULTS, {})
        self._room = defaults.get(CONF_IMPORT_ROOM, DEFAULT_IMPORT_ROOM)
        self._category = defaults.get(CONF_IMPORT_CATEGORY, DEFAULT_IMPORT_CATEGORY)
        self._importance = Importance(
            defaults.get(CONF_IMPORT_IMPORTANCE, DEFAULT_IMPORT_IMPORTANCE)
        )
        self._assignment = AssignmentMode(
            defaults.get(CONF_IMPORT_ASSIGNMENT_MODE, DEFAULT_IMPORT_ASSIGNMENT_MODE)
        )

    @property
    def active(self) -> bool:
        return self.enabled and bool(self.entity_id)

    # -- listener for ChoreFlow → to-do completion (§16.5) -----------------
    async def async_on_completion(self, inst: TaskInstance, source: str) -> None:
        """Mirror a ChoreFlow completion to the linked to-do item."""
        if not self.active or not self.sync_to_todo or source == COMPLETION_SOURCE_TODO:
            return
        refs = inst.external_refs
        if refs is None or refs.todo is None or refs.todo.entity_id != self.entity_id:
            return
        await self._complete_todo_item(refs.todo.item_uid)

    # -- full reconcile (§16.3/§16.4) --------------------------------------
    async def async_sync(self) -> None:
        """Import new items and pull to-do completions into ChoreFlow."""
        if not self.active:
            return
        assert self.entity_id is not None

        items = await self._fetch_items()
        if items is None:
            self._raise_unavailable_issue()
            return
        self._clear_unavailable_issue()

        by_uid = {item["uid"]: item for item in items if item.get("uid")}
        mapped = self._mapped_instances()

        if self.sync_from_todo:
            for uid, inst in mapped.items():
                if inst.status != TaskStatus.OPEN:
                    continue
                item = by_uid.get(uid)
                if item is None or item.get("status") == _STATUS_COMPLETED:
                    await self.coordinator.async_complete_from_external(
                        inst.id, COMPLETION_SOURCE_TODO
                    )

        if self.import_new:
            for uid, item in by_uid.items():
                if item.get("status") == _STATUS_COMPLETED:
                    continue
                task_id = f"task_todo_{_sanitize(uid)}"
                if task_id in self.coordinator.store.task_instances:
                    continue
                await self.coordinator.async_register_imported_task(
                    self._build_instance(task_id, uid, item)
                )

    # -- helpers -----------------------------------------------------------
    def _mapped_instances(self) -> dict[str, TaskInstance]:
        result: dict[str, TaskInstance] = {}
        for inst in self.coordinator.store.task_instances.values():
            refs = inst.external_refs
            if (
                refs is not None
                and refs.todo is not None
                and refs.todo.entity_id == self.entity_id
            ):
                result[refs.todo.item_uid] = inst
        return result

    def _build_instance(
        self, task_id: str, uid: str, item: dict[str, Any]
    ) -> TaskInstance:
        assert self.entity_id is not None
        return TaskInstance(
            id=task_id,
            rule_id=None,
            title=item.get("summary", "To-do"),
            description=item.get("description"),
            room=self._room,
            category=self._category,
            importance=self._importance,
            estimated_duration_minutes=None,
            urgency_type=None,
            due_date=None,
            deadline=None,
            status=TaskStatus.OPEN,
            source=TaskSource.TODO_SYNC,
            visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
            visibility_persons=[],
            assignment_mode=self._assignment,
            assignment_person=None,
            external_refs=ExternalRefs(
                todo=TodoRef(entity_id=self.entity_id, item_uid=uid)
            ),
            created_at=self.coordinator.clock.now(),
        )

    async def _fetch_items(self) -> list[dict[str, Any]] | None:
        """Return the to-do items, or None when the entity is unavailable."""
        assert self.entity_id is not None
        state = self.hass.states.get(self.entity_id)
        if state is None or state.state == "unavailable":
            return None
        try:
            response = await self.hass.services.async_call(
                "todo",
                "get_items",
                {"entity_id": self.entity_id},
                blocking=True,
                return_response=True,
            )
        except Exception:  # noqa: BLE001 — never let a sync failure crash setup
            _LOGGER.exception("Failed to read to-do items from %s", self.entity_id)
            return None
        entity_data = (response or {}).get(self.entity_id)
        if not isinstance(entity_data, dict):
            return []
        raw_items = entity_data.get("items", [])
        if not isinstance(raw_items, list):
            return []
        return [item for item in raw_items if isinstance(item, dict)]

    async def _complete_todo_item(self, uid: str) -> None:
        assert self.entity_id is not None
        try:
            await self.hass.services.async_call(
                "todo",
                "update_item",
                {"entity_id": self.entity_id, "item": uid, "status": "completed"},
                blocking=True,
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to complete to-do item %s", uid)

    def _raise_unavailable_issue(self) -> None:
        _LOGGER.warning("To-do entity %s unavailable; sync suspended", self.entity_id)
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            f"{_ISSUE_TODO_UNAVAILABLE}_{self.entity_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=_ISSUE_TODO_UNAVAILABLE,
            translation_placeholders={"entity_id": self.entity_id or ""},
        )

    def _clear_unavailable_issue(self) -> None:
        ir.async_delete_issue(
            self.hass, DOMAIN, f"{_ISSUE_TODO_UNAVAILABLE}_{self.entity_id}"
        )
