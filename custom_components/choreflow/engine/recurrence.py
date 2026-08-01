"""Recurrence rules → due task instances (Pflichtenheft §4.2).

Pure function: given the rules, the day to evaluate and the instances that
already exist, return the new :class:`TaskInstance`s that become due on that
day. No duplicates are produced for a rule that already has an instance that
day, regardless of its status.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime

from ..models import RecurrenceType, TaskInstance, TaskRule, TaskSource, TaskStatus


def instance_id_for(rule_id: str, on_date: date) -> str:
    """Stable instance id: ``inst_<YYYY_MM_DD>_<rule_id>`` (§4.2)."""
    return f"inst_{on_date:%Y_%m_%d}_{rule_id}"


@dataclass
class RecurrenceIndex:
    """O(1) recurrence lookups built once for a generation pass."""

    instance_dates: set[tuple[str, date]] = field(default_factory=set)
    open_rule_ids: set[str] = field(default_factory=set)
    last_completion_dates: dict[str, date] = field(default_factory=dict)

    @classmethod
    def from_instances(cls, instances: Iterable[TaskInstance]) -> RecurrenceIndex:
        index = cls()
        for instance in instances:
            index.add(instance)
        return index

    def add(self, instance: TaskInstance) -> None:
        """Add an existing or newly generated instance to the lookup index."""
        rule_id = instance.rule_id
        if rule_id is None:
            return
        if instance.due_date is not None:
            self.instance_dates.add((rule_id, instance.due_date))
        if instance.status == TaskStatus.OPEN:
            self.open_rule_ids.add(rule_id)
        if instance.status == TaskStatus.COMPLETED and instance.completed_at:
            completed_date = instance.completed_at.date()
            previous = self.last_completion_dates.get(rule_id)
            if previous is None or completed_date > previous:
                self.last_completion_dates[rule_id] = completed_date


def _is_due(rule: TaskRule, on_date: date, index: RecurrenceIndex) -> bool:
    if rule.recurrence_type == RecurrenceType.ONCE:
        return False  # one-off rules never recur automatically

    if rule.recurrence_type == RecurrenceType.WEEKDAYS:
        weekdays = rule.recurrence_weekdays or []
        return on_date.weekday() in weekdays

    if rule.recurrence_type == RecurrenceType.EVERY_N_DAYS:
        interval = rule.recurrence_interval
        if not interval or interval < 1:
            return False
        completion_anchor = rule.last_completed_date or index.last_completion_dates.get(
            rule.id
        )
        if completion_anchor is not None:
            return (on_date - completion_anchor).days >= interval
        anchor = rule.created_date or on_date
        delta = (on_date - anchor).days
        # Also catches overdue rules: if at least one full interval has elapsed
        # and no open instance exists (guarded by _has_open_instance), generate
        # the missed instance today rather than waiting for the next exact multiple.
        return delta >= 0 and (delta % interval == 0 or delta >= interval)

    return False


def due_instances_for(
    rules: list[TaskRule],
    on_date: date,
    existing_instances: list[TaskInstance],
    now: datetime,
    *,
    index: RecurrenceIndex | None = None,
) -> list[TaskInstance]:
    """Return new instances that become due on ``on_date``.

    ``now`` provides ``created_at`` for the generated instances (Clock-driven;
    added to the §4.2 signature because :class:`TaskInstance` requires it).
    ``existing_instances`` and a pre-built ``index`` are mutually exclusive.
    """
    if index is not None and existing_instances:
        raise ValueError("existing_instances and index are mutually exclusive")
    context = (
        index
        if index is not None
        else RecurrenceIndex.from_instances(existing_instances)
    )
    result: list[TaskInstance] = []
    for rule in rules:
        if not rule.enabled:
            continue
        if not _is_due(rule, on_date, context):
            continue
        if (rule.id, on_date) in context.instance_dates:
            continue
        if rule.id in context.open_rule_ids:
            continue
        instance = TaskInstance(
            id=instance_id_for(rule.id, on_date),
            rule_id=rule.id,
            title=rule.title,
            description=rule.description,
            room=rule.room,
            category=rule.category,
            importance=rule.importance,
            estimated_duration_minutes=rule.estimated_duration_minutes,
            urgency_type=rule.urgency_type,
            due_date=on_date,
            deadline=rule.deadline,
            status=TaskStatus.OPEN,
            source=TaskSource.RULE,
            visibility_mode=rule.visibility_mode,
            visibility_persons=list(rule.visibility_persons),
            assignment_mode=rule.assignment_mode,
            assignment_person=rule.assignment_person,
            external_refs=None,
            created_at=now,
        )
        result.append(instance)
        context.add(instance)
    return result
