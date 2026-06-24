"""Task selection: urgency pool, per-person top-5, rotation (Pflichtenheft §4.3).

Pure scoring and selection. The caller (coordinator) supplies the runtime
context — which tasks are reserved for others, whether the person still has
day-limit capacity, how often a task was recently pushed, and the per-task
"skipped" counters that drive ``high`` anti-starvation. Randomness is injected
as a :class:`random.Random` so "soft rotation" stays deterministic in tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from random import Random

from ..const import (
    HIGH_FORCE_AFTER_SKIPPED,
    IMPORTANCE_WEIGHTS,
    TOP_POOL_SIZE,
    W_DUE_TODAY,
    W_IMPORTANCE,
    W_OVERDUE,
    W_RECENT_PUSH,
)
from ..models import (
    AssignmentMode,
    Importance,
    TaskInstance,
    TaskStatus,
    VisibilityMode,
)


@dataclass
class PersonContext:
    """Per-person runtime inputs for selection."""

    person_entity: str
    # Task ids exclusively reserved by *other* persons (from reservation.py).
    excluded_task_ids: set[str] = field(default_factory=set)
    # False once the person reached the daily task limit (§12.4).
    has_capacity: bool = True


def score(
    instance: TaskInstance,
    on_date: date,
    recent_push_counts: dict[str, int],
) -> float:
    """Urgency score for one instance (§4.3 formula)."""
    importance_weight = IMPORTANCE_WEIGHTS[instance.importance]
    overdue_days = 0
    is_due_today = 0
    if instance.due_date is not None:
        delta = (on_date - instance.due_date).days
        overdue_days = max(0, delta)
        is_due_today = 1 if delta == 0 else 0
    recent = recent_push_counts.get(instance.id, 0)
    return (
        W_IMPORTANCE * importance_weight
        + W_OVERDUE * overdue_days
        + W_DUE_TODAY * is_due_today
        - W_RECENT_PUSH * recent
    )


def build_urgency_pool(
    instances: list[TaskInstance],
    on_date: date,
    recent_push_counts: dict[str, int] | None = None,
) -> list[TaskInstance]:
    """All open, due/overdue instances, sorted by descending urgency (§13.1).

    Instances without a due date (e.g. imported to-do items) are treated as
    eligible. Ties break on id for deterministic ordering.
    """
    recent = recent_push_counts or {}
    pool = [
        inst
        for inst in instances
        if inst.status == TaskStatus.OPEN
        and (inst.due_date is None or inst.due_date <= on_date)
    ]
    pool.sort(key=lambda inst: (-score(inst, on_date, recent), inst.id))
    return pool


def is_suitable(instance: TaskInstance, ctx: PersonContext) -> bool:
    """Whether a task may be offered to the person (§13.2)."""
    if (
        instance.visibility_mode == VisibilityMode.SELECTED_PERSONS
        and ctx.person_entity not in instance.visibility_persons
    ):
        return False
    if (
        instance.assignment_mode == AssignmentMode.ASSIGNED
        and instance.assignment_person != ctx.person_entity
    ):
        return False
    return instance.id not in ctx.excluded_task_ids


def top_pool_for_person(
    pool: list[TaskInstance],
    ctx: PersonContext,
    size: int = TOP_POOL_SIZE,
) -> list[TaskInstance]:
    """The ``size`` most urgent suitable tasks for the person (§13.2)."""
    if not ctx.has_capacity:
        return []
    suitable = [inst for inst in pool if is_suitable(inst, ctx)]
    return suitable[:size]


def pick_first(top_pool: list[TaskInstance], rng: Random) -> TaskInstance | None:
    """First task of a chain: soft rotation, ``high`` preferred (§13.3).

    Weighted random choice by importance weight — ``high`` dominates but does
    not strictly monopolise, giving gentle rotation. Deterministic for a seeded
    ``rng``.
    """
    if not top_pool:
        return None
    weights = [IMPORTANCE_WEIGHTS[inst.importance] for inst in top_pool]
    return rng.choices(top_pool, weights=weights, k=1)[0]


def pick_next(
    top_pool: list[TaskInstance],
    last_room: str | None,
    rng: Random,
    high_skip_counts: dict[str, int] | None = None,
) -> TaskInstance | None:
    """Follow-up task selection (§13.4).

    Order: (1) force a ``high`` task that has been skipped too often so room
    bundling cannot starve it (§13.4.5); (2) otherwise bundle by ``last_room``
    — most urgent task in that room; (3) otherwise soft rotation.
    """
    if not top_pool:
        return None
    skips = high_skip_counts or {}

    forced = [
        inst
        for inst in top_pool
        if inst.importance == Importance.HIGH
        and skips.get(inst.id, 0) >= HIGH_FORCE_AFTER_SKIPPED
    ]
    if forced:
        return forced[0]  # top_pool is score-sorted → most urgent forced high

    if last_room:
        same_room = [inst for inst in top_pool if inst.room == last_room]
        if same_room:
            return same_room[0]

    return pick_first(top_pool, rng)
