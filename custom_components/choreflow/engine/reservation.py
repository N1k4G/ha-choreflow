"""Reservations and double-work protection (Pflichtenheft §4.4).

A task pushed to a person is reserved so it is not handed to anybody else.
The one exception is a time-critical ``high`` task on its last relevant day:
it may be reserved in parallel by several present persons (§4.4, Lastenheft
§14). :class:`ReservationBook` mutates the list it is given in place so the
coordinator can persist it directly.
"""

from __future__ import annotations

from datetime import date, datetime

from ..models import Importance, Reservation, TaskInstance


def relevant_day(instance: TaskInstance) -> date | None:
    """The day a task must be done by — due date, falling back to deadline."""
    return instance.due_date or instance.deadline


def is_last_relevant_day(instance: TaskInstance, on_date: date) -> bool:
    """True when ``on_date`` is the task's due/deadline day (§4.4)."""
    day = relevant_day(instance)
    return day is not None and day == on_date


def allows_parallel(instance: TaskInstance, on_date: date) -> bool:
    """A time-critical ``high`` task on its last day may go to several people."""
    return instance.importance == Importance.HIGH and is_last_relevant_day(
        instance, on_date
    )


class ReservationBook:
    """Thin view over the list of active reservations."""

    def __init__(self, reservations: list[Reservation] | None = None) -> None:
        self.items: list[Reservation] = reservations if reservations is not None else []

    def _find(self, task_id: str, person: str) -> Reservation | None:
        return next(
            (
                r
                for r in self.items
                if r.task_id == task_id and r.person_entity == person
            ),
            None,
        )

    def reserve(
        self,
        task_id: str,
        person: str,
        now: datetime,
        *,
        exclusive: bool = True,
    ) -> Reservation:
        """Reserve a task for a person (idempotent per person)."""
        existing = self._find(task_id, person)
        if existing is not None:
            existing.exclusive = exclusive
            return existing
        reservation = Reservation(
            task_id=task_id,
            person_entity=person,
            reserved_at=now,
            exclusive=exclusive,
        )
        self.items.append(reservation)
        return reservation

    def release(self, task_id: str) -> None:
        """Release all reservations for a task (snooze/complete/day-end)."""
        self.items[:] = [r for r in self.items if r.task_id != task_id]

    def release_for_person(self, task_id: str, person: str) -> None:
        """Release only the given person's reservation of a task."""
        self.items[:] = [
            r
            for r in self.items
            if not (r.task_id == task_id and r.person_entity == person)
        ]

    def release_all_for_person(self, person: str) -> int:
        """Release every reservation held by a person and return the count."""
        previous_count = len(self.items)
        self.items[:] = [r for r in self.items if r.person_entity != person]
        return previous_count - len(self.items)

    def release_before(self, on_date: date) -> int:
        """Expire reservations from earlier days and return the count."""
        previous_count = len(self.items)
        self.items[:] = [r for r in self.items if r.reserved_at.date() >= on_date]
        return previous_count - len(self.items)

    def is_reserved_for_other(self, task_id: str, person: str) -> bool:
        """True if another person holds an exclusive reservation of the task."""
        return any(
            r.task_id == task_id and r.person_entity != person and r.exclusive
            for r in self.items
        )

    def excluded_task_ids_for(self, person: str) -> set[str]:
        """Task ids the person cannot take (others' exclusive reservations)."""
        return {
            r.task_id for r in self.items if r.person_entity != person and r.exclusive
        }

    def reserved_persons(self, task_id: str) -> set[str]:
        """All persons currently holding a reservation of a task."""
        return {r.person_entity for r in self.items if r.task_id == task_id}
