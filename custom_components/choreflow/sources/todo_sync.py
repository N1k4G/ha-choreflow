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

import asyncio
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
        # Serialises exports so a state-change-triggered re-sync cannot race the
        # add-then-link window in ``_export_task`` and create duplicate items.
        self._export_lock = asyncio.Lock()

    @property
    def active(self) -> bool:
        return self.enabled and bool(self.entity_id)

    # -- listener for ChoreFlow → to-do completion (§16.5) -----------------
    async def async_on_completion(self, inst: TaskInstance, source: str) -> None:
        """Mirror a ChoreFlow completion to the linked to-do item."""
        if not self.active or not self.sync_to_todo or source == COMPLETION_SOURCE_TODO:
            return
        uid = self._linked_uid(inst)
        if uid is not None:
            await self._complete_todo_item(uid)

    # -- listeners for ChoreFlow → to-do creation/reopen/delete (§16.5) -----
    async def async_on_task_created(self, inst: TaskInstance) -> None:
        """Push a newly created ChoreFlow task to the linked to-do list."""
        if not self.active or not self.sync_to_todo:
            return
        if self._should_export(inst):
            await self._export_task(inst)

    async def async_on_task_reopened(self, inst: TaskInstance) -> None:
        """Re-open the linked to-do item when its ChoreFlow task is reopened."""
        if not self.active or not self.sync_to_todo:
            return
        uid = self._linked_uid(inst)
        if uid is not None:
            await self._reopen_todo_item(uid)

    async def async_on_task_deleted(self, inst: TaskInstance) -> None:
        """Remove the linked to-do item when its ChoreFlow task is deleted."""
        if not self.active or not self.sync_to_todo:
            return
        uid = self._linked_uid(inst)
        if uid is not None:
            await self._delete_todo_item(uid)

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
                # Skip items already linked to an existing task — including ones
                # we exported ourselves — so we never re-import them as dupes.
                if uid in mapped:
                    continue
                task_id = f"task_todo_{_sanitize(uid)}"
                if task_id in self.coordinator.store.task_instances:
                    continue
                await self.coordinator.async_register_imported_task(
                    self._build_instance(task_id, uid, item)
                )

        if self.sync_to_todo:
            for inst in list(self.coordinator.store.task_instances.values()):
                if self._should_export(inst):
                    await self._export_task(inst)

    # -- helpers -----------------------------------------------------------
    def _linked_uid(self, inst: TaskInstance) -> str | None:
        """Return the to-do uid this task is linked to on our entity, if any."""
        refs = inst.external_refs
        if refs is None or refs.todo is None or refs.todo.entity_id != self.entity_id:
            return None
        return refs.todo.item_uid

    def _should_export(self, inst: TaskInstance) -> bool:
        """True when an open ChoreFlow task should be pushed to the to-do list."""
        if inst.status != TaskStatus.OPEN:
            return False
        if self._linked_uid(inst) is not None:
            return False  # already mirrored to this entity
        today = self.coordinator.clock.today()
        return inst.due_date is None or inst.due_date <= today

    async def _export_task(self, inst: TaskInstance) -> None:
        """Create a to-do item for a ChoreFlow task and link it back."""
        assert self.entity_id is not None
        # The lock serialises the add-then-link window; the re-check inside it
        # guards against a concurrent export that already linked this task while
        # we waited (e.g. a state-change-triggered re-sync).
        async with self._export_lock:
            if not self._should_export(inst):
                return
            before = await self._fetch_items()
            if before is None:
                return  # entity unavailable; the next reconcile retries
            before_uids = {item["uid"] for item in before if item.get("uid")}
            if not await self._add_todo_item(inst.title, inst.description):
                return
            after = await self._fetch_items()
            if after is None:
                return
            new_items = [
                item
                for item in after
                if item.get("uid") and item["uid"] not in before_uids
            ]
            if len(new_items) == 1:
                uid = new_items[0]["uid"]
            else:
                # Ambiguous (concurrent add or duplicate summary): match by summary.
                matches = [i for i in new_items if i.get("summary") == inst.title]
                if len(matches) != 1:
                    _LOGGER.warning(
                        "Could not resolve uid for exported task %s; will retry",
                        inst.id,
                    )
                    return
                uid = matches[0]["uid"]
            # Merge, never replace: a calendar task keeps its calendar ref so the
            # calendar source still recognises it and won't recreate a duplicate.
            refs = inst.external_refs or ExternalRefs()
            refs.todo = TodoRef(entity_id=self.entity_id, item_uid=uid)
            inst.external_refs = refs
            self.coordinator.store.async_schedule_save()

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

    async def _add_todo_item(self, summary: str, description: str | None) -> bool:
        """Create a to-do item; return True on success."""
        assert self.entity_id is not None
        data: dict[str, Any] = {"entity_id": self.entity_id, "item": summary}
        if description:
            data["description"] = description
        try:
            await self.hass.services.async_call("todo", "add_item", data, blocking=True)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to add to-do item %s", summary)
            return False
        return True

    async def _complete_todo_item(self, uid: str) -> None:
        await self._update_todo_status(uid, "completed")

    async def _reopen_todo_item(self, uid: str) -> None:
        await self._update_todo_status(uid, "needs_action")

    async def _update_todo_status(self, uid: str, status: str) -> None:
        assert self.entity_id is not None
        try:
            await self.hass.services.async_call(
                "todo",
                "update_item",
                {"entity_id": self.entity_id, "item": uid, "status": status},
                blocking=True,
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to set to-do item %s to %s", uid, status)

    async def _delete_todo_item(self, uid: str) -> None:
        assert self.entity_id is not None
        try:
            await self.hass.services.async_call(
                "todo",
                "remove_item",
                {"entity_id": self.entity_id, "item": uid},
                blocking=True,
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to remove to-do item %s", uid)

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
