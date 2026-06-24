"""Recurrence rules → due task instances (Pflichtenheft §4.2).

Pure function: given the rules, the day to evaluate and the instances that
already exist, return the new :class:`TaskInstance`s that become due on that
day. No duplicates are produced for a rule that already has an instance that
day, regardless of its status.
"""

from __future__ import annotations

from datetime import date, datetime

from ..models import RecurrenceType, TaskInstance, TaskRule, TaskSource, TaskStatus


def instance_id_for(rule_id: str, on_date: date) -> str:
    """Stable instance id: ``inst_<YYYY_MM_DD>_<rule_id>`` (§4.2)."""
    return f"inst_{on_date:%Y_%m_%d}_{rule_id}"


def _last_completion_date(rule_id: str, existing: list[TaskInstance]) -> date | None:
    """Most recent completion date of a rule, used as the recurrence anchor."""
    dates = [
        inst.completed_at.date()
        for inst in existing
        if inst.rule_id == rule_id
        and inst.status == TaskStatus.COMPLETED
        and inst.completed_at is not None
    ]
    return max(dates) if dates else None


def _has_instance_on(rule_id: str, on_date: date, existing: list[TaskInstance]) -> bool:
    """True if any instance of the rule already exists for ``on_date``."""
    return any(
        inst.rule_id == rule_id and inst.due_date == on_date for inst in existing
    )


def _has_open_instance(rule_id: str, existing: list[TaskInstance]) -> bool:
    """True if the rule already has an open (not yet completed) instance.

    Prevents pile-up for long-ignored every_n_days rules: at most one open
    instance per rule is generated, so the dashboard doesn't fill with stacked
    copies of the same recurring chore.
    """
    return any(
        inst.rule_id == rule_id and inst.status == TaskStatus.OPEN
        for inst in existing
    )


def _is_due(rule: TaskRule, on_date: date, existing: list[TaskInstance]) -> bool:
    if rule.recurrence_type == RecurrenceType.ONCE:
        return False  # one-off rules never recur automatically

    if rule.recurrence_type == RecurrenceType.WEEKDAYS:
        weekdays = rule.recurrence_weekdays or []
        return on_date.weekday() in weekdays

    if rule.recurrence_type == RecurrenceType.EVERY_N_DAYS:
        interval = rule.recurrence_interval
        if not interval or interval < 1:
            return False
        anchor = (
            _last_completion_date(rule.id, existing) or rule.created_date or on_date
        )
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
) -> list[TaskInstance]:
    """Return new instances that become due on ``on_date``.

    ``now`` provides ``created_at`` for the generated instances (Clock-driven;
    added to the §4.2 signature because :class:`TaskInstance` requires it).
    """
    result: list[TaskInstance] = []
    for rule in rules:
        if not rule.enabled:
            continue
        if not _is_due(rule, on_date, existing_instances):
            continue
        if _has_instance_on(rule.id, on_date, existing_instances):
            continue
        if _has_open_instance(rule.id, existing_instances):
            continue
        result.append(
            TaskInstance(
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
        )
    return result
