"""Runtime coordinator for ChoreFlow (Pflichtenheft §5.2).

Owns the runtime state and orchestrates the presence-aware push chain. The pure
decisions (recurrence, scoring/selection, reservation, schedule windows) live in
``engine/`` and are combined here with HA state, notifications and persistence.
Every automatic decision is logged with a ``decision_reason`` (§24.5).
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from random import Random
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CARD_API_VERSION,
    DEFAULT_IMPORT_CATEGORY,
    DEFAULT_IMPORT_ROOM,
    DOMAIN,
    EVENT_CALENDAR_TASK_CREATED,
    EVENT_CALENDAR_TASK_REMOVED,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EVENT_TASK_CREATED,
    EVENT_TASK_DELETED,
    EVENT_TASK_EXPIRED,
    EVENT_TASK_MISSED_NO_PRESENCE,
    EVENT_TASK_NOTIFIED,
    EVENT_TASK_REOPENED,
    EVENT_TASK_SNOOZED,
    EVENT_TASK_SYNCED_FROM_TODO,
    EVENT_TASK_UPDATED,
    LOGBOOK_EVENT,
    MAX_SENSOR_ATTR_TASKS,
)
from .engine import scheduler
from .engine.clock import Clock, SystemClock
from .engine.recurrence import RecurrenceIndex, due_instances_for
from .engine.reservation import ReservationBook, allows_parallel
from .engine.selector import (
    PersonContext,
    build_urgency_pool,
    pick_first,
    pick_next,
    top_pool_for_person,
)
from .entity import person_slug
from .models import (
    AssignmentMode,
    Importance,
    LogEvent,
    PushChainState,
    RecurrenceType,
    TaskInstance,
    TaskRule,
    TaskSource,
    TaskStatus,
    VisibilityMode,
)
from .notify import async_send_task_push
from .settings import ChoreFlowSettings, PersonSettings
from .store import ChoreFlowStore, LogStore

_LOGGER = logging.getLogger(__name__)

# Counts are pure local computation; refresh periodically so date-derived values
# (overdue, completed-today) stay current without per-sensor polling (§5.6).
_UPDATE_INTERVAL = timedelta(minutes=10)

# Completed instances older than this are pruned at the daily start to keep the
# state store bounded while preserving the recurrence anchor (§4.2).
_COMPLETED_RETENTION_DAYS = 120
_DELETED_RETENTION_DAYS = 120
_CHAIN_STATE_RETENTION_DAYS = 7
# How many days ahead to pre-generate the next occurrence of a recurring rule.
# Covers the longest standard interval (yearly) so a completed task's successor
# always appears in the list immediately.
_LOOKAHEAD_DAYS = 366


@dataclass
class PersonStats:
    open: int = 0
    due: int = 0
    completed_today: int = 0
    remaining_today: int = 0
    has_due: bool = False
    chain_active: bool = False
    chain_status: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChoreFlowData:
    open_tasks: int = 0
    due_tasks: int = 0
    overdue_tasks: int = 0
    completed_today: int = 0
    completed_this_week: int = 0
    active_chains: int = 0
    open_task_list: list[dict[str, Any]] = field(default_factory=list)
    per_person: dict[str, PersonStats] = field(default_factory=dict)


def _visible_to(instance: TaskInstance, person: str) -> bool:
    """Whether a task is visible to a person (§10.3)."""
    if instance.visibility_mode == VisibilityMode.SELECTED_PERSONS:
        return person in instance.visibility_persons
    return True


def task_payload(
    instance: TaskInstance, rule: TaskRule | None = None
) -> dict[str, Any]:
    """Return the versioned card-facing representation of a task."""
    payload: dict[str, Any] = {
        "task_id": instance.id,
        "task_rule_id": instance.rule_id,
        "title": instance.title,
        "description": instance.description,
        "room": instance.room,
        "category": instance.category,
        "importance": instance.importance.value,
        "estimated_duration_minutes": instance.estimated_duration_minutes,
        "due_date": instance.due_date.isoformat() if instance.due_date else None,
        "snooze_until": (
            instance.snooze_until.isoformat() if instance.snooze_until else None
        ),
        "deadline": instance.deadline.isoformat() if instance.deadline else None,
        "status": instance.status.value,
        "source": instance.source.value,
        "visibility_mode": instance.visibility_mode.value,
        "visibility_persons": list(instance.visibility_persons),
        "assignment_mode": instance.assignment_mode.value,
        "assignment_person": instance.assignment_person,
        "created_at": instance.created_at.isoformat(),
        "completed_at": (
            instance.completed_at.isoformat() if instance.completed_at else None
        ),
        "completed_by": instance.completed_by,
        "completion_source": instance.completion_source,
        "recurrence_type": rule.recurrence_type.value if rule else None,
        "recurrence_interval": rule.recurrence_interval if rule else None,
        "recurrence_weekdays": (
            list(rule.recurrence_weekdays)
            if rule and rule.recurrence_weekdays
            else None
        ),
    }
    return payload


def task_preview_payload(instance: TaskInstance) -> dict[str, Any]:
    """Return the bounded sensor payload used for quick dashboard rendering."""
    return {
        "task_id": instance.id,
        "title": instance.title,
        "room": instance.room,
        "category": instance.category,
        "importance": instance.importance.value,
        "estimated_duration_minutes": instance.estimated_duration_minutes,
        "due_date": instance.due_date.isoformat() if instance.due_date else None,
        "snooze_until": (
            instance.snooze_until.isoformat() if instance.snooze_until else None
        ),
    }


def _ordered_open_tasks(
    instances: list[TaskInstance], today: date
) -> list[TaskInstance]:
    """Order all open tasks: urgent/overdue first, future next, snoozed last."""
    snoozed = [i for i in instances if i.snooze_until and i.snooze_until > today]
    snoozed_ids = {i.id for i in snoozed}
    active = [i for i in instances if i.id not in snoozed_ids]
    urgent = build_urgency_pool(active, today)
    urgent_ids = {item.id for item in urgent}
    future = sorted(
        (item for item in active if item.id not in urgent_ids),
        key=lambda item: (item.due_date or date.max, item.id),
    )
    snoozed_sorted = sorted(
        snoozed, key=lambda item: (item.snooze_until or date.max, item.id)
    )
    return [*urgent, *future, *snoozed_sorted]


class ChoreFlowCoordinator(DataUpdateCoordinator[ChoreFlowData]):
    """Runtime state, push-chain orchestration and sensor snapshot."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        store: ChoreFlowStore,
        log_store: LogStore,
        settings: ChoreFlowSettings,
        clock: Clock | None = None,
        rng: Random | None = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({entry.entry_id})",
            update_interval=_UPDATE_INTERVAL,
        )
        self.entry = entry
        self.store = store
        self.log_store = log_store
        self.settings = settings
        self.clock = clock or SystemClock()
        self._rng = rng or Random()
        # Per-person consecutive skip counters for high anti-starvation (§13.4.5).
        self._high_skips: dict[str, dict[str, int]] = {}
        # Serialize chain decisions per person while allowing different people
        # to advance concurrently.
        self._advance_locks: dict[str, asyncio.Lock] = {}
        # Listeners notified after a user completion (e.g. ChoreFlow → to-do).
        self._completion_listeners: list[
            Callable[[TaskInstance, str], Awaitable[None]]
        ] = []
        # Listeners notified after a task is created / reopened / deleted, used to
        # mirror ChoreFlow tasks out to a linked to-do list (§6).
        self._task_created_listeners: list[
            Callable[[TaskInstance], Awaitable[None]]
        ] = []
        self._task_reopened_listeners: list[
            Callable[[TaskInstance], Awaitable[None]]
        ] = []
        self._task_deleted_listeners: list[
            Callable[[TaskInstance], Awaitable[None]]
        ] = []

    def add_completion_listener(
        self, listener: Callable[[TaskInstance, str], Awaitable[None]]
    ) -> None:
        """Register a callback invoked after a user task completion (§6)."""
        self._completion_listeners.append(listener)

    def add_task_created_listener(
        self, listener: Callable[[TaskInstance], Awaitable[None]]
    ) -> None:
        """Register a callback invoked after a task is created (§6)."""
        self._task_created_listeners.append(listener)

    def add_task_reopened_listener(
        self, listener: Callable[[TaskInstance], Awaitable[None]]
    ) -> None:
        """Register a callback invoked after a task is reopened (§6)."""
        self._task_reopened_listeners.append(listener)

    def add_task_deleted_listener(
        self, listener: Callable[[TaskInstance], Awaitable[None]]
    ) -> None:
        """Register a callback invoked after a task is deleted (§6)."""
        self._task_deleted_listeners.append(listener)

    async def _notify_task_created(self, inst: TaskInstance) -> None:
        for listener in self._task_created_listeners:
            await listener(inst)

    async def _notify_task_reopened(self, inst: TaskInstance) -> None:
        for listener in self._task_reopened_listeners:
            await listener(inst)

    async def _notify_task_deleted(self, inst: TaskInstance) -> None:
        for listener in self._task_deleted_listeners:
            await listener(inst)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def _book(self) -> ReservationBook:
        return ReservationBook(self.store.reservations)

    def _is_home(self, person: str) -> bool:
        state = self.hass.states.get(person)
        return state is not None and state.state == "home"

    def _person_for_slug(self, slug: str) -> str | None:
        for person in self.settings.enabled_persons:
            if person_slug(person) == slug:
                return person
        return None

    def _get_chain(self, person: str, day: date) -> PushChainState:
        key = f"{person}|{day.isoformat()}"
        chain = self.store.push_chain_states.get(key)
        if chain is None:
            chain = PushChainState(person_entity=person, date=day)
            self.store.push_chain_states[key] = chain
        return chain

    def _recent_push_counts(self, day: date) -> dict[str, int]:
        counter: Counter[str] = Counter()
        suffix = f"|{day.isoformat()}"
        for key, chain in self.store.push_chain_states.items():
            if key.endswith(suffix):
                counter.update(chain.sent_task_ids)
        return dict(counter)

    def _recalculate_rule_completion_anchor(self, rule_id: str) -> None:
        """Rebuild a rule anchor after a completion is reopened."""
        rule = self.store.task_rules.get(rule_id)
        if rule is None:
            return
        completion_dates = [
            instance.completed_at.date()
            for instance in self.store.task_instances.values()
            if instance.rule_id == rule_id
            and instance.status == TaskStatus.COMPLETED
            and instance.completed_at is not None
        ]
        rule.last_completed_date = max(completion_dates, default=None)

    async def _persist_and_refresh(self) -> None:
        self.store.async_schedule_save()
        # Refresh immediately rather than via the debouncer so no refresh timer
        # lingers after a one-off mutation (e.g. service calls in tests).
        await self.async_refresh()

    async def _async_log_event(
        self,
        event_type: str,
        *,
        task: TaskInstance | None = None,
        person: str | None = None,
        decision_reason: str | None = None,
        completion_source: str | None = None,
        overdue_days: int | None = None,
    ) -> None:
        now = self.clock.now()
        event = LogEvent(
            event_id=f"evt_{now:%Y_%m_%d_%H%M%S}_{uuid4().hex[:6]}",
            event_type=event_type,
            timestamp=now,
            task_id=task.id if task else None,
            task_rule_id=task.rule_id if task else None,
            title=task.title if task else None,
            room=task.room if task else None,
            category=task.category if task else None,
            importance=task.importance.value if task else None,
            person_entity=person,
            source=task.source.value if task else None,
            completion_source=completion_source,
            overdue_days_at_completion=overdue_days,
            decision_reason=decision_reason,
        )
        await self.log_store.async_add_event(event)
        self.hass.bus.async_fire(LOGBOOK_EVENT, event.to_dict())

    # ------------------------------------------------------------------
    # Daily flow & chain advance
    # ------------------------------------------------------------------
    async def _generate_due_instances(self) -> None:
        today = self.clock.today()
        now = self.clock.now()
        rules = list(self.store.task_rules.values())
        index = RecurrenceIndex.from_instances(self.store.task_instances.values())
        new_instances: list[TaskInstance] = []
        state_changed = False

        # Existing stores derive the durable anchor once from retained history.
        for rule in rules:
            observed = index.last_completion_dates.get(rule.id)
            if observed is not None and (
                rule.last_completed_date is None or observed > rule.last_completed_date
            ):
                rule.last_completed_date = observed
                state_changed = True

        remaining_rules = [
            rule
            for rule in rules
            if rule.enabled and rule.id not in index.open_rule_ids
        ]

        for days_ahead in range(_LOOKAHEAD_DAYS + 1):
            if not remaining_rules:
                break
            candidate = today + timedelta(days=days_ahead)
            day_instances = due_instances_for(
                remaining_rules, candidate, [], now, index=index
            )
            new_instances.extend(day_instances)
            if day_instances:
                generated_rule_ids = {
                    instance.rule_id
                    for instance in day_instances
                    if instance.rule_id is not None
                }
                remaining_rules = [
                    rule
                    for rule in remaining_rules
                    if rule.id not in generated_rule_ids
                ]

        for inst in new_instances:
            self.store.task_instances[inst.id] = inst
            if inst.due_date == today:
                # Only log task_created for today's instances; future ones are
                # pre-generated silently and will be visible as upcoming tasks.
                await self._async_log_event(
                    EVENT_TASK_CREATED,
                    task=inst,
                    decision_reason="recurrence due",
                )
            await self._notify_task_created(inst)
        self._prune_stale(today)
        if new_instances or state_changed:
            self.store.async_schedule_save()

    def _prune_stale(self, today: date) -> bool:
        """Bound local state without propagating retention as task deletion."""
        completed_cutoff = today - timedelta(days=_COMPLETED_RETENTION_DAYS)
        deleted_cutoff = today - timedelta(days=_DELETED_RETENTION_DAYS)
        stale_instances = [
            inst_id
            for inst_id, inst in self.store.task_instances.items()
            if (
                inst.status == TaskStatus.COMPLETED
                and inst.completed_at is not None
                and inst.completed_at.date() < completed_cutoff
            )
            or (
                inst.status == TaskStatus.DELETED
                and (inst.deleted_at or inst.completed_at or inst.created_at).date()
                < deleted_cutoff
            )
        ]
        for inst_id in stale_instances:
            self.store.task_instances.pop(inst_id)

        chain_cutoff = today - timedelta(days=_CHAIN_STATE_RETENTION_DAYS)
        stale_chains = [
            key
            for key, chain in self.store.push_chain_states.items()
            if chain.date < chain_cutoff
        ]
        for key in stale_chains:
            self.store.push_chain_states.pop(key)

        expired_reservations = self._book.release_before(today)
        changed = bool(stale_instances or stale_chains or expired_reservations)
        if changed:
            self.store.async_schedule_save()
        return changed

    def _completed_today(self, person: str, today: date) -> bool:
        """True if person completed any task today (any source)."""
        return any(
            inst.completed_by == person
            and inst.completed_at is not None
            and inst.completed_at.date() == today
            for inst in self.store.task_instances.values()
        )

    def _push_enabled(self, person_settings: PersonSettings, day: date) -> bool:
        return scheduler.push_enabled_for_day(
            day,
            weekday_push_enabled=person_settings.weekday_push_enabled,
            weekend_push_enabled=person_settings.weekend_push_enabled,
        )

    async def async_start_daily_flow(self, person: str | None = None) -> None:
        """Start the daily push chain for one or all persons (§12.1)."""
        await self._generate_due_instances()
        today = self.clock.today()
        targets = [person] if person else list(self.settings.enabled_persons)
        for target in targets:
            settings = self.settings.person_settings.get(target)
            if settings is None or not self._push_enabled(settings, today):
                continue
            chain = self._get_chain(target, today)
            if self._is_home(target) or not settings.presence_required:
                await self.async_advance_chain(target)
            else:
                chain.pending_catchup = True
        await self._persist_and_refresh()

    async def async_advance_chain(self, person: str) -> None:
        """Serialize the full chain transition for one person."""
        lock = self._advance_locks.setdefault(person, asyncio.Lock())
        async with lock:
            await self._async_advance_chain_locked(person)
            # Persist even when the locked path exits early: callers such as
            # snooze and presence may have mutated state before advancing.
            await self._persist_and_refresh()

    async def _async_advance_chain_locked(self, person: str) -> None:
        """Pick, reserve and push the next task for a person (§5.2)."""
        settings = self.settings.person_settings.get(person)
        if settings is None:
            return
        now = self.clock.now()
        today = self.clock.today()
        chain = self._get_chain(person, today)

        if not scheduler.is_within_window(now, self.settings.schedule):
            return
        if settings.presence_required and not self._is_home(person):
            chain.active = False
            return
        if chain.tasks_sent_count >= self.settings.max_tasks_per_person_per_day:
            chain.active = False
            chain.ended_reason = "limit"
            return
        if chain.current_task_id is not None:
            return  # waiting for the current task's action
        if not chain.started and not self._push_enabled(settings, today):
            return
        if self.settings.skip_push_after_daily_completion and self._completed_today(
            person, today
        ):
            chain.active = False
            chain.ended_reason = "daily_completion_reached"
            return

        open_instances = [
            i for i in self.store.task_instances.values() if i.status == TaskStatus.OPEN
        ]
        recent = self._recent_push_counts(today)
        pool = build_urgency_pool(open_instances, today, recent)
        book = self._book
        book.release_before(today)
        ctx = PersonContext(
            person_entity=person,
            excluded_task_ids=book.excluded_task_ids_for(person),
            has_capacity=True,
        )
        top = top_pool_for_person(pool, ctx)
        skips = self._high_skips.setdefault(person, {})

        if not chain.started:
            task = pick_first(top, self._rng)
            reason = "first task: soft rotation"
        else:
            task = pick_next(top, chain.last_room, self._rng, skips)
            reason = "follow-up: room bundling / rotation"

        if task is None:
            chain.active = False
            chain.ended_reason = "no_tasks"
            return

        exclusive = not allows_parallel(task, today)
        book.reserve(task.id, person, now, exclusive=exclusive)

        sent = await async_send_task_push(
            self.hass,
            settings.notify_service,
            task,
            person_slug(person),
            today.isoformat(),
        )
        if not sent:
            book.release_for_person(task.id, person)
            chain.active = False
            chain.ended_reason = "no_notify"
            return

        chain.active = True
        chain.started = True
        chain.pending_catchup = False
        chain.current_task_id = task.id
        chain.tasks_sent_count += 1
        chain.sent_task_ids.append(task.id)
        chain.last_room = task.room

        for candidate in top:
            if candidate.importance == Importance.HIGH and candidate.id != task.id:
                skips[candidate.id] = skips.get(candidate.id, 0) + 1
        skips.pop(task.id, None)

        await self._async_log_event(
            EVENT_TASK_NOTIFIED, task=task, person=person, decision_reason=reason
        )

    async def async_send_next_task(self, person: str) -> None:
        """Service entry point: advance the chain for a person."""
        await self.async_advance_chain(person)

    # ------------------------------------------------------------------
    # Task actions
    # ------------------------------------------------------------------
    async def async_complete_task(self, task_id: str, person: str, source: str) -> None:
        """Mark a task completed and push the next one (§19.1)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None or inst.status != TaskStatus.OPEN:
            return  # idempotent against duplicate/lost events
        now = self.clock.now()
        today = self.clock.today()
        inst.status = TaskStatus.COMPLETED
        inst.completed_at = now
        inst.completed_by = person
        inst.completion_source = source
        if inst.rule_id and (rule := self.store.task_rules.get(inst.rule_id)):
            rule.last_completed_date = now.date()

        overdue_days = max(0, (today - inst.due_date).days) if inst.due_date else 0
        self._book.release(task_id)
        chain = self._get_chain(person, today)
        if chain.current_task_id == task_id:
            chain.current_task_id = None

        event_type = (
            EVENT_TASK_COMPLETED_FROM_TODO if source == "todo" else EVENT_TASK_COMPLETED
        )
        await self._async_log_event(
            event_type,
            task=inst,
            person=person,
            completion_source=source,
            overdue_days=overdue_days,
            decision_reason="completed",
        )
        for listener in self._completion_listeners:
            await listener(inst, source)
        await self.async_advance_chain(person)

    async def async_reopen_task(self, task_id: str) -> None:
        """Reopen a completed task, correcting the stats log (§Feature 2)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None or inst.status != TaskStatus.COMPLETED:
            return
        person = inst.completed_by
        inst.status = TaskStatus.OPEN
        inst.completed_at = None
        inst.completed_by = None
        inst.completion_source = None
        if inst.rule_id:
            self._recalculate_rule_completion_anchor(inst.rule_id)
        self._book.release(task_id)
        await self._async_log_event(
            EVENT_TASK_REOPENED,
            task=inst,
            person=person,
            decision_reason="reopened by user",
        )
        await self._notify_task_reopened(inst)
        await self._persist_and_refresh()

    async def async_snooze_task(self, task_id: str, person: str) -> None:
        """Snooze a task until tomorrow (§12.7/§19.2)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return
        today = self.clock.today()
        inst.snooze_until = today + timedelta(days=1)
        self._book.release(task_id)
        chain = self._get_chain(person, today)
        if chain.current_task_id == task_id:
            chain.current_task_id = None

        await self._async_log_event(
            EVENT_TASK_SNOOZED,
            task=inst,
            person=person,
            decision_reason="snoozed by user",
        )

        if inst.importance in (Importance.NORMAL, Importance.LOW):
            chain.active = False
            chain.ended_reason = "snooze"
            await self._persist_and_refresh()
        else:
            # high tasks may be reminded again within the day → continue
            await self.async_advance_chain(person)

    # ------------------------------------------------------------------
    # Task CRUD (dashboard / services)
    # ------------------------------------------------------------------
    async def async_create_task(self, fields: dict[str, Any]) -> str:
        """Create a one-off task instance (§19, Lastenheft §7.3)."""
        task_id = f"task_{uuid4().hex[:8]}"
        inst = TaskInstance(
            id=task_id,
            rule_id=None,
            title=fields["title"],
            description=fields.get("description"),
            room=fields.get("room", DEFAULT_IMPORT_ROOM),
            category=fields.get("category", DEFAULT_IMPORT_CATEGORY),
            importance=Importance(fields.get("importance", Importance.NORMAL.value)),
            estimated_duration_minutes=fields.get("estimated_duration_minutes"),
            urgency_type=None,
            due_date=fields.get("due_date"),
            deadline=None,
            status=TaskStatus.OPEN,
            source=TaskSource.MANUAL,
            visibility_mode=VisibilityMode(
                fields.get("visibility_mode", VisibilityMode.ALL_ENABLED_PERSONS.value)
            ),
            visibility_persons=fields.get("visibility_persons", []),
            assignment_mode=AssignmentMode(
                fields.get("assignment_mode", AssignmentMode.RANDOM.value)
            ),
            assignment_person=fields.get("assignment_person"),
            external_refs=None,
            created_at=self.clock.now(),
        )
        self.store.task_instances[task_id] = inst
        await self._async_log_event(
            EVENT_TASK_CREATED, task=inst, decision_reason="manual create"
        )
        await self._notify_task_created(inst)
        await self._persist_and_refresh()
        return task_id

    def query_tasks(
        self,
        *,
        status: str,
        person_entity: str | None,
        person_scope: str,
        room: str | None,
        category: str | None,
        limit: int,
        offset: int,
    ) -> dict[str, Any]:
        """Return a filtered, paginated task collection for dashboard clients."""
        instances = list(self.store.task_instances.values())
        if status != "all":
            instances = [item for item in instances if item.status.value == status]
        if person_entity is not None:
            if person_scope == "assigned":
                instances = [
                    item
                    for item in instances
                    if item.assignment_person == person_entity
                ]
            else:
                instances = [
                    item for item in instances if _visible_to(item, person_entity)
                ]
        if room is not None:
            instances = [item for item in instances if item.room == room]
        if category is not None:
            instances = [item for item in instances if item.category == category]

        if status == TaskStatus.OPEN.value:
            instances = _ordered_open_tasks(instances, self.clock.today())
        else:
            instances.sort(key=lambda item: (item.created_at, item.id), reverse=True)

        total = len(instances)
        items = instances[offset : offset + limit]
        return {
            "api_version": CARD_API_VERSION,
            "items": [
                task_payload(
                    item,
                    self.store.task_rules.get(item.rule_id) if item.rule_id else None,
                )
                for item in items
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(items) < total,
        }

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Return the full payload for a single task, including rule metadata."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return None
        rule = self.store.task_rules.get(inst.rule_id) if inst.rule_id else None
        return task_payload(inst, rule)

    async def async_update_task(self, task_id: str, changes: dict[str, Any]) -> None:
        """Update mutable fields of a task and its source rule (§19)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return
        today = self.clock.today()

        # --- Instance fields (apply to this occurrence) ---
        for field_name in (
            "title",
            "description",
            "room",
            "category",
            "due_date",
            "estimated_duration_minutes",
        ):
            if field_name in changes:
                setattr(inst, field_name, changes[field_name])
        if "importance" in changes:
            inst.importance = Importance(changes["importance"])
        if "visibility_mode" in changes:
            inst.visibility_mode = VisibilityMode(changes["visibility_mode"])
        if "visibility_persons" in changes:
            inst.visibility_persons = changes["visibility_persons"]
        if "assignment_mode" in changes:
            inst.assignment_mode = AssignmentMode(changes["assignment_mode"])
        if "assignment_person" in changes:
            inst.assignment_person = changes["assignment_person"]

        # --- Rule fields (persist changes to all future occurrences) ---
        rule = self.store.task_rules.get(inst.rule_id) if inst.rule_id else None
        if rule is not None:
            for field_name in (
                "title", "description", "room", "category", "estimated_duration_minutes"
            ):
                if field_name in changes:
                    setattr(rule, field_name, changes[field_name])
            if "importance" in changes:
                rule.importance = Importance(changes["importance"])
            if "visibility_mode" in changes:
                rule.visibility_mode = VisibilityMode(changes["visibility_mode"])
            if "visibility_persons" in changes:
                rule.visibility_persons = changes["visibility_persons"]
            if "assignment_mode" in changes:
                rule.assignment_mode = AssignmentMode(changes["assignment_mode"])
            if "assignment_person" in changes:
                rule.assignment_person = changes["assignment_person"]

            _recurrence_keys = (
                "recurrence_type", "recurrence_interval", "recurrence_weekdays"
            )
            recurrence_changed = any(k in changes for k in _recurrence_keys)
            if "recurrence_type" in changes:
                rule.recurrence_type = RecurrenceType(changes["recurrence_type"])
            if "recurrence_interval" in changes:
                rule.recurrence_interval = changes["recurrence_interval"]
            if "recurrence_weekdays" in changes:
                rule.recurrence_weekdays = changes["recurrence_weekdays"]

            if recurrence_changed:
                # Re-anchor from today so the new interval starts now.
                rule.created_date = today
                rule.last_completed_date = today
                # Drop pre-generated future instances — they used the old schedule.
                stale = [
                    iid for iid, i in self.store.task_instances.items()
                    if i.rule_id == rule.id
                    and i.status == TaskStatus.OPEN
                    and i.due_date is not None
                    and i.due_date > today
                ]
                for iid in stale:
                    removed = self.store.task_instances.pop(iid)
                    await self._notify_task_deleted(removed)

        await self._async_log_event(
            EVENT_TASK_UPDATED, task=inst, decision_reason="manual update"
        )
        await self._persist_and_refresh()

    async def async_delete_task(self, task_id: str) -> None:
        """Delete a task (kept as DELETED; reservations released) (§19)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return
        inst.status = TaskStatus.DELETED
        inst.deleted_at = self.clock.now()
        self._book.release(task_id)
        await self._async_log_event(
            EVENT_TASK_DELETED, task=inst, decision_reason="manual delete"
        )
        await self._notify_task_deleted(inst)
        await self._persist_and_refresh()

    # ------------------------------------------------------------------
    # Sync helpers (to-do / calendar sources)
    # ------------------------------------------------------------------
    async def async_register_imported_task(self, inst: TaskInstance) -> None:
        """Add an externally imported task and log its origin (§6)."""
        self.store.task_instances[inst.id] = inst
        await self._async_log_event(
            EVENT_TASK_SYNCED_FROM_TODO,
            task=inst,
            decision_reason="imported from to-do",
        )
        await self._persist_and_refresh()

    async def async_complete_from_external(self, task_id: str, source: str) -> None:
        """Complete a task from an external source (no person, no chain) (§16.4)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None or inst.status != TaskStatus.OPEN:
            return
        today = self.clock.today()
        inst.status = TaskStatus.COMPLETED
        inst.completed_at = self.clock.now()
        inst.completion_source = source
        if inst.rule_id and (rule := self.store.task_rules.get(inst.rule_id)):
            rule.last_completed_date = inst.completed_at.date()
        overdue_days = max(0, (today - inst.due_date).days) if inst.due_date else 0
        self._book.release(task_id)
        await self._async_log_event(
            EVENT_TASK_COMPLETED_FROM_TODO,
            task=inst,
            completion_source=source,
            overdue_days=overdue_days,
            decision_reason="completed via to-do",
        )
        await self._persist_and_refresh()

    async def async_add_calendar_task(self, inst: TaskInstance) -> None:
        """Add a calendar-generated task and log its creation (§7/§15.4)."""
        self.store.task_instances[inst.id] = inst
        await self._async_log_event(
            EVENT_CALENDAR_TASK_CREATED,
            task=inst,
            decision_reason="created from calendar event",
        )
        await self._notify_task_created(inst)
        await self._persist_and_refresh()

    async def async_remove_calendar_task(self, task_id: str) -> None:
        """Remove an open calendar task whose event disappeared (§15.4)."""
        inst = self.store.task_instances.pop(task_id, None)
        if inst is None:
            return
        self._book.release(task_id)
        await self._async_log_event(
            EVENT_CALENDAR_TASK_REMOVED,
            task=inst,
            decision_reason="calendar event removed",
        )
        await self._notify_task_deleted(inst)
        await self._persist_and_refresh()

    # ------------------------------------------------------------------
    # Triggers (timers / presence / notification actions)
    # ------------------------------------------------------------------
    async def async_handle_start_time(self, *, weekend: bool) -> None:
        """Daily start timer callback for weekday or weekend (§12.1)."""
        if scheduler.is_weekend(self.clock.today()) != weekend:
            return
        await self.async_start_daily_flow()

    async def async_handle_day_end(self) -> None:
        """Close all of today's chains at the day end (§12.1)."""
        today = self.clock.today()
        suffix = f"|{today.isoformat()}"
        book = self._book
        for key, chain in self.store.push_chain_states.items():
            if not key.endswith(suffix):
                continue
            if chain.pending_catchup and not chain.started:
                await self._async_log_event(
                    EVENT_TASK_MISSED_NO_PRESENCE,
                    person=chain.person_entity,
                    decision_reason="absent until day end",
                )
            elif chain.active:
                await self._async_log_event(
                    EVENT_TASK_EXPIRED,
                    person=chain.person_entity,
                    decision_reason="day window ended",
                )
            chain.active = False
            chain.pending_catchup = False
            chain.current_task_id = None
            chain.ended_reason = "window_end"
            book.release_all_for_person(chain.person_entity)
        await self._persist_and_refresh()

    async def async_handle_presence(self, person: str, is_home: bool) -> None:
        """React to a person's presence change (§5.3)."""
        if person not in self.settings.person_settings:
            return
        today = self.clock.today()
        chain = self._get_chain(person, today)
        if is_home:
            await self.async_advance_chain(person)
        else:
            chain.active = False
            await self._persist_and_refresh()

    async def async_handle_notification_action(
        self, kind: str, task_id: str, slug: str
    ) -> None:
        """Route a tapped notification action back into the chain (§5.4)."""
        person = self._person_for_slug(slug)
        if person is None:
            return
        if kind == "done":
            await self.async_complete_task(task_id, person, "push")
        elif kind == "snooze":
            await self.async_snooze_task(task_id, person)

    # ------------------------------------------------------------------
    # Sensor snapshot (read/derive layer)
    # ------------------------------------------------------------------
    async def _async_update_data(self) -> ChoreFlowData:
        await self._generate_due_instances()
        today = self.clock.today()
        week_start = today - timedelta(days=today.weekday())
        today_iso = today.isoformat()

        completed_today = await self.log_store.async_completed_count_in_range(
            today_iso, today_iso
        )
        completed_week = await self.log_store.async_completed_count_in_range(
            week_start.isoformat(), today_iso
        )
        completed_today_by_person = (
            await self.log_store.async_completed_count_by_person_in_range(
                today_iso, today_iso
            )
        )
        return self._compute(
            today, completed_today, completed_week, completed_today_by_person
        )

    def _compute(
        self,
        today: date,
        completed_today: int,
        completed_week: int,
        completed_today_by_person: dict[str, int],
    ) -> ChoreFlowData:
        open_instances = [
            inst
            for inst in self.store.task_instances.values()
            if inst.status == TaskStatus.OPEN
        ]
        due = [i for i in open_instances if i.due_date and i.due_date <= today]
        overdue = [i for i in open_instances if i.due_date and i.due_date < today]

        ordered = _ordered_open_tasks(open_instances, today)
        open_task_list = [
            task_preview_payload(instance)
            for instance in ordered[:MAX_SENSOR_ATTR_TASKS]
        ]

        per_person: dict[str, PersonStats] = {}
        active_chains = 0
        for person in self.settings.enabled_persons:
            visible = [i for i in open_instances if _visible_to(i, person)]
            p_due = [i for i in visible if i.due_date and i.due_date <= today]
            chain = self.store.push_chain_states.get(f"{person}|{today.isoformat()}")
            chain_active = bool(chain and chain.active)
            sent = chain.tasks_sent_count if chain else 0
            current_task = (
                self.store.task_instances.get(chain.current_task_id)
                if chain and chain.current_task_id
                else None
            )
            if chain_active:
                active_chains += 1
            per_person[person] = PersonStats(
                open=len(visible),
                due=len(p_due),
                completed_today=completed_today_by_person.get(person, 0),
                remaining_today=max(
                    0, self.settings.max_tasks_per_person_per_day - sent
                ),
                has_due=len(p_due) > 0,
                chain_active=chain_active,
                chain_status={
                    "api_version": CARD_API_VERSION,
                    "person_entity": person,
                    "date": today.isoformat(),
                    "started": bool(chain and chain.started),
                    "active": chain_active,
                    "pending_catchup": bool(chain and chain.pending_catchup),
                    "current_task_id": chain.current_task_id if chain else None,
                    "current_task_title": (
                        current_task.title if current_task is not None else None
                    ),
                    "tasks_sent_today": sent,
                    "tasks_completed_today": completed_today_by_person.get(person, 0),
                    "daily_limit": self.settings.max_tasks_per_person_per_day,
                    "remaining_today": max(
                        0, self.settings.max_tasks_per_person_per_day - sent
                    ),
                    "ended_reason": chain.ended_reason if chain else None,
                },
            )

        return ChoreFlowData(
            open_tasks=len(open_instances),
            due_tasks=len(due),
            overdue_tasks=len(overdue),
            completed_today=completed_today,
            completed_this_week=completed_week,
            active_chains=active_chains,
            open_task_list=open_task_list,
            per_person=per_person,
        )
