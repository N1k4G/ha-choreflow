"""Runtime coordinator for ChoreFlow (Pflichtenheft §5.2).

Owns the runtime state and orchestrates the presence-aware push chain. The pure
decisions (recurrence, scoring/selection, reservation, schedule windows) live in
``engine/`` and are combined here with HA state, notifications and persistence.
Every automatic decision is logged with a ``decision_reason`` (§24.5).
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from random import Random
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DEFAULT_IMPORT_CATEGORY,
    DEFAULT_IMPORT_ROOM,
    DOMAIN,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EVENT_TASK_CREATED,
    EVENT_TASK_DELETED,
    EVENT_TASK_EXPIRED,
    EVENT_TASK_MISSED_NO_PRESENCE,
    EVENT_TASK_NOTIFIED,
    EVENT_TASK_SNOOZED,
    EVENT_TASK_UPDATED,
    LOGBOOK_EVENT,
    MAX_SENSOR_ATTR_TASKS,
)
from .engine import scheduler
from .engine.clock import Clock, SystemClock
from .engine.recurrence import due_instances_for
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
    TaskInstance,
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


@dataclass
class PersonStats:
    open: int = 0
    due: int = 0
    completed_today: int = 0
    remaining_today: int = 0
    has_due: bool = False
    chain_active: bool = False


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
        existing = list(self.store.task_instances.values())
        rules = list(self.store.task_rules.values())
        for inst in due_instances_for(rules, today, existing, now):
            self.store.task_instances[inst.id] = inst
            await self._async_log_event(
                EVENT_TASK_CREATED,
                task=inst,
                decision_reason="recurrence due",
            )
        self._prune_completed(today)

    def _prune_completed(self, today: date) -> None:
        cutoff = today - timedelta(days=_COMPLETED_RETENTION_DAYS)
        stale = [
            inst_id
            for inst_id, inst in self.store.task_instances.items()
            if inst.status == TaskStatus.COMPLETED
            and inst.completed_at is not None
            and inst.completed_at.date() < cutoff
        ]
        for inst_id in stale:
            del self.store.task_instances[inst_id]

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

        open_instances = [
            i for i in self.store.task_instances.values() if i.status == TaskStatus.OPEN
        ]
        recent = self._recent_push_counts(today)
        pool = build_urgency_pool(open_instances, today, recent)
        book = self._book
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
        await self._persist_and_refresh()

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
        await self.async_advance_chain(person)
        await self._persist_and_refresh()

    async def async_snooze_task(self, task_id: str, person: str) -> None:
        """Snooze a task without changing its due date (§12.7/§19.2)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return
        today = self.clock.today()
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
        await self._persist_and_refresh()
        return task_id

    async def async_update_task(self, task_id: str, changes: dict[str, Any]) -> None:
        """Update mutable fields of an existing task (§19)."""
        inst = self.store.task_instances.get(task_id)
        if inst is None:
            return
        for field_name in ("title", "description", "room", "category", "due_date"):
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
        self._book.release(task_id)
        await self._async_log_event(
            EVENT_TASK_DELETED, task=inst, decision_reason="manual delete"
        )
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
            chain.ended_reason = "window_end"
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

        ordered = build_urgency_pool(open_instances, today)
        open_task_list = [
            {
                "title": i.title,
                "room": i.room,
                "category": i.category,
                "importance": i.importance.value,
                "due_date": i.due_date.isoformat() if i.due_date else None,
            }
            for i in ordered[:MAX_SENSOR_ATTR_TASKS]
        ]

        per_person: dict[str, PersonStats] = {}
        active_chains = 0
        for person in self.settings.enabled_persons:
            visible = [i for i in open_instances if _visible_to(i, person)]
            p_due = [i for i in visible if i.due_date and i.due_date <= today]
            chain = self.store.push_chain_states.get(f"{person}|{today.isoformat()}")
            chain_active = bool(chain and chain.active)
            sent = chain.tasks_sent_count if chain else 0
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
