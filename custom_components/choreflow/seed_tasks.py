"""Default task rule pool for ChoreFlow (Feature 6).

Provides ``SEED_RULES`` — a list of ready-to-use :class:`TaskRule` definitions
that cover common household chores. Applied idempotently by the
``choreflow.import_seed_tasks`` service: rules whose id already exists in the
store are skipped so user edits are never overwritten.

The washing machine chore is intentionally absent from the pool: it should be
triggered on-demand from a Home Assistant automation via ``choreflow.create_task``
rather than a fixed recurrence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import (
    AssignmentMode,
    Importance,
    RecurrenceType,
    TaskRule,
    VisibilityMode,
)

# Anchor date used for every_n_days rules so the first due date is today when
# the seed is imported — the recurrence engine uses created_date as fallback.
# We intentionally leave it as None so the coordinator sets it at import time.


@dataclass
class _SeedEntry:
    id: str
    title: str
    room: str
    recurrence_interval: int  # days (every_n_days)
    importance: Importance = Importance.NORMAL
    category: str = "Reinigung"


_ENTRIES: list[_SeedEntry] = [
    _SeedEntry("seed_staub_flur", "Staubputzen", "Flur", 30),
    _SeedEntry("seed_staub_schlafzimmer", "Staubputzen", "Schlafzimmer", 30),
    _SeedEntry("seed_staub_wohnzimmer", "Staubputzen", "Wohnzimmer", 30),
    _SeedEntry("seed_staub_esszimmer", "Staubputzen", "Esszimmer", 30),
    _SeedEntry("seed_staub_arbeitszimmer", "Staubputzen", "Arbeitszimmer", 30),
    _SeedEntry("seed_hildegard", "Hildegard starten", "Wohnbereich", 7),
    _SeedEntry("seed_badezimmer", "Badezimmer putzen", "Badezimmer", 14),
    _SeedEntry("seed_kueche_putzen", "Küche putzen", "Küche", 14),
    _SeedEntry("seed_kuehlschrank", "Kühlschrank reinigen", "Küche", 182),
    _SeedEntry(
        "seed_bett_beziehen",
        "Bett beziehen",
        "Schlafzimmer",
        14,
        category="Haushalt",
    ),
    _SeedEntry(
        "seed_pflanzen",
        "Pflanzen gießen",
        "Wohnzimmer",
        7,
        category="Garten",
    ),
]


def build_seed_rules(today: date) -> list[TaskRule]:
    """Return the seed rules with ``created_date`` set to ``today``."""
    return [
        TaskRule(
            id=e.id,
            title=e.title,
            description=None,
            room=e.room,
            category=e.category,
            importance=e.importance,
            estimated_duration_minutes=None,
            recurrence_type=RecurrenceType.EVERY_N_DAYS,
            recurrence_interval=e.recurrence_interval,
            recurrence_weekdays=None,
            created_date=today,
            urgency_type=None,
            deadline=None,
            visibility_mode=VisibilityMode.ALL_ENABLED_PERSONS,
            visibility_persons=[],
            assignment_mode=AssignmentMode.RANDOM,
            assignment_person=None,
            enabled=True,
        )
        for e in _ENTRIES
    ]
