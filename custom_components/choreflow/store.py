"""Persistence layer for ChoreFlow (Pflichtenheft §3).

Two stores, by design:

* :class:`ChoreFlowStore` wraps Home Assistant's ``Store`` helper and holds the
  migratable JSON state (rules, instances, chain states, reservations,
  sync/calendar state) — §3.2.
* :class:`LogStore` (async, HA-aware) writes the durable event history to an own
  SQLite file ``<config>/choreflow.db`` — **not** the HA recorder (§3.1/§3.3).
  Its blocking SQL lives in :class:`LogDatabase`, which is HA-free and runs
  inside ``hass.async_add_executor_job`` (§3.3, no blocking I/O in the loop).
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sqlite3
import threading
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import (
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EVENT_TASK_SNOOZED,
    STORAGE_KEY_TEMPLATE,
    STORAGE_MINOR_VERSION,
    STORAGE_VERSION,
    STORE_SAVE_DEBOUNCE_SECONDS,
)
from .models import (
    LogEvent,
    PushChainState,
    Reservation,
    TaskInstance,
    TaskRule,
)

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")

# Completion is recorded by either a direct completion or a to-do completion.
_COMPLETED_EVENT_TYPES: tuple[str, ...] = (
    EVENT_TASK_COMPLETED,
    EVENT_TASK_COMPLETED_FROM_TODO,
)


# ===========================================================================
# HA Store (JSON state) — §3.2
# ===========================================================================
class _StateStore(Store[dict[str, Any]]):
    """HA Store subclass with a migration hook for future storage versions."""

    async def _async_migrate_func(
        self,
        old_major_version: int,
        old_minor_version: int,
        old_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Migrate persisted data to the current version.

        No migrations exist yet (storage_version=1). This hook is the single
        place future schema changes are handled (§3.2).
        """
        return old_data


class ChoreFlowStore:
    """In-memory ChoreFlow state, persisted as JSON via the HA Store."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store = _StateStore(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY_TEMPLATE.format(entry_id=entry_id),
            minor_version=STORAGE_MINOR_VERSION,
        )
        self.task_rules: dict[str, TaskRule] = {}
        self.task_instances: dict[str, TaskInstance] = {}
        self.push_chain_states: dict[str, PushChainState] = {}
        self.reservations: list[Reservation] = []
        self.sync_state: dict[str, Any] = {}
        self.calendar_state: dict[str, Any] = {}

    async def async_load(self) -> None:
        """Load persisted state into memory (call once at setup)."""
        raw = await self._store.async_load()
        if raw:
            self._deserialize(raw)
            _LOGGER.debug(
                "Loaded ChoreFlow state: %d rules, %d instances",
                len(self.task_rules),
                len(self.task_instances),
            )

    async def async_save(self) -> None:
        """Persist current state immediately."""
        await self._store.async_save(self._serialize())

    @callback
    def async_schedule_save(self) -> None:
        """Persist current state debounced (§3.2 — bundled writes)."""
        self._store.async_delay_save(self._serialize, STORE_SAVE_DEBOUNCE_SECONDS)

    async def async_remove(self) -> None:
        """Delete the persisted store (entry removal)."""
        await self._store.async_remove()

    # -- serialisation ------------------------------------------------------
    def _serialize(self) -> dict[str, Any]:
        return {
            "task_rules": {k: v.to_dict() for k, v in self.task_rules.items()},
            "task_instances": {k: v.to_dict() for k, v in self.task_instances.items()},
            "push_chain_states": {
                k: v.to_dict() for k, v in self.push_chain_states.items()
            },
            "reservations": [r.to_dict() for r in self.reservations],
            "sync_state": self.sync_state,
            "calendar_state": self.calendar_state,
        }

    def _deserialize(self, raw: dict[str, Any]) -> None:
        self.task_rules = {
            k: TaskRule.from_dict(v) for k, v in raw.get("task_rules", {}).items()
        }
        self.task_instances = {
            k: TaskInstance.from_dict(v)
            for k, v in raw.get("task_instances", {}).items()
        }
        self.push_chain_states = {
            k: PushChainState.from_dict(v)
            for k, v in raw.get("push_chain_states", {}).items()
        }
        self.reservations = [
            Reservation.from_dict(v) for v in raw.get("reservations", [])
        ]
        self.sync_state = dict(raw.get("sync_state", {}))
        self.calendar_state = dict(raw.get("calendar_state", {}))


# ===========================================================================
# SQLite log core (HA-free) — §3.3 / §3.4
# ===========================================================================
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS log_events (
    event_id        TEXT PRIMARY KEY,
    event_type      TEXT NOT NULL,
    task_id         TEXT,
    task_rule_id    TEXT,
    title           TEXT,
    room            TEXT,
    category        TEXT,
    importance      TEXT,
    person_entity   TEXT,
    timestamp       TEXT NOT NULL,
    source          TEXT,
    completion_source TEXT,
    overdue_days_at_completion INTEGER,
    decision_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_log_type ON log_events(event_type);
CREATE INDEX IF NOT EXISTS idx_log_person ON log_events(person_entity);
CREATE INDEX IF NOT EXISTS idx_log_room ON log_events(room);
CREATE INDEX IF NOT EXISTS idx_log_ts ON log_events(timestamp);
"""

_INSERT_SQL = """
INSERT OR REPLACE INTO log_events (
    event_id, event_type, task_id, task_rule_id, title, room, category,
    importance, person_entity, timestamp, source, completion_source,
    overdue_days_at_completion, decision_reason
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# Ordered columns of the log_events table (for CSV export).
_LOG_COLUMNS: tuple[str, ...] = (
    "event_id",
    "event_type",
    "task_id",
    "task_rule_id",
    "title",
    "room",
    "category",
    "importance",
    "person_entity",
    "timestamp",
    "source",
    "completion_source",
    "overdue_days_at_completion",
    "decision_reason",
)

# Allowlist of group-by dimensions to keep dynamic column names injection-safe.
_GROUP_COLUMNS: frozenset[str] = frozenset({"person_entity", "room", "category"})

# Placeholder list matching the number of completed event types.
_COMPLETED_PLACEHOLDERS = ", ".join("?" for _ in _COMPLETED_EVENT_TYPES)


class LogDatabase:
    """Synchronous SQLite wrapper for the ChoreFlow event log (HA-free).

    Holds a single connection (``check_same_thread=False``) guarded by a lock,
    so it works both against a file path and an in-memory database in tests.
    All callers in production go through :class:`LogStore`, which runs these
    methods in an executor thread.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()

    # -- lifecycle ----------------------------------------------------------
    def connect(self) -> None:
        """Open the connection and ensure the schema exists."""
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA_SQL)
            self._conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @property
    def _c(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("LogDatabase is not connected")
        return self._conn

    # -- writes -------------------------------------------------------------
    def insert(self, event: LogEvent) -> None:
        row = (
            event.event_id,
            event.event_type,
            event.task_id,
            event.task_rule_id,
            event.title,
            event.room,
            event.category,
            event.importance,
            event.person_entity,
            event.timestamp.isoformat(),
            event.source,
            event.completion_source,
            event.overdue_days_at_completion,
            event.decision_reason,
        )
        with self._lock:
            self._c.execute(_INSERT_SQL, row)
            self._c.commit()

    # -- evaluation queries (§3.4) -----------------------------------------
    def _completed_group_count(self, column: str) -> dict[str, int]:
        if column not in _GROUP_COLUMNS:
            raise ValueError(f"Unsupported group column: {column}")
        sql = (
            f"SELECT {column} AS k, COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            f"GROUP BY {column}"
        )
        with self._lock:
            rows = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchall()
        return {row["k"]: row["c"] for row in rows if row["k"] is not None}

    def completed_count_by_person(self) -> dict[str, int]:
        return self._completed_group_count("person_entity")

    def completed_count_by_room(self) -> dict[str, int]:
        return self._completed_group_count("room")

    def completed_count_by_category(self) -> dict[str, int]:
        return self._completed_group_count("category")

    def completed_count_by_task(self) -> dict[str, int]:
        """Completions grouped by task (rule id, falling back to instance id)."""
        sql = (
            "SELECT COALESCE(task_rule_id, task_id) AS k, COUNT(*) AS c "
            "FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "GROUP BY k"
        )
        with self._lock:
            rows = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchall()
        return {row["k"]: row["c"] for row in rows if row["k"] is not None}

    def snoozed_count(self) -> int:
        sql = "SELECT COUNT(*) AS c FROM log_events WHERE event_type = ?"
        with self._lock:
            row = self._c.execute(sql, (EVENT_TASK_SNOOZED,)).fetchone()
        return int(row["c"])

    def most_snoozed_tasks(self, limit: int = 10) -> list[tuple[str, int]]:
        sql = (
            "SELECT COALESCE(task_rule_id, task_id) AS k, COUNT(*) AS c "
            "FROM log_events WHERE event_type = ? "
            "GROUP BY k ORDER BY c DESC, k ASC LIMIT ?"
        )
        with self._lock:
            rows = self._c.execute(sql, (EVENT_TASK_SNOOZED, limit)).fetchall()
        return [(row["k"], row["c"]) for row in rows if row["k"] is not None]

    def completed_count_by_month(self) -> dict[str, int]:
        """Completions keyed by ``YYYY-MM`` (derived from the ISO timestamp)."""
        sql = (
            "SELECT substr(timestamp, 1, 7) AS k, COUNT(*) AS c "
            "FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "GROUP BY k ORDER BY k"
        )
        with self._lock:
            rows = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchall()
        return {row["k"]: row["c"] for row in rows}

    def completed_count_by_year(self) -> dict[str, int]:
        sql = (
            "SELECT substr(timestamp, 1, 4) AS k, COUNT(*) AS c "
            "FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "GROUP BY k ORDER BY k"
        )
        with self._lock:
            rows = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchall()
        return {row["k"]: row["c"] for row in rows}

    def high_completed_on_time_count(self) -> int:
        """High tasks completed without being overdue (§3.4)."""
        sql = (
            "SELECT COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "AND importance = 'high' "
            "AND (overdue_days_at_completion IS NULL "
            "     OR overdue_days_at_completion <= 0)"
        )
        with self._lock:
            row = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchone()
        return int(row["c"])

    def overdue_at_completion_count(self) -> int:
        """Completions that happened while overdue (§3.4)."""
        sql = (
            "SELECT COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "AND overdue_days_at_completion > 0"
        )
        with self._lock:
            row = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchone()
        return int(row["c"])

    def completion_source_distribution(self) -> dict[str, int]:
        sql = (
            "SELECT completion_source AS k, COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "GROUP BY completion_source"
        )
        with self._lock:
            rows = self._c.execute(sql, _COMPLETED_EVENT_TYPES).fetchall()
        return {row["k"]: row["c"] for row in rows if row["k"] is not None}

    def completed_count_in_range(self, start_date: str, end_date: str) -> int:
        """Completions whose date part falls within ``[start_date, end_date]``.

        Dates are ``YYYY-MM-DD`` and compared on the timestamp's date prefix,
        which is timezone-offset independent.
        """
        sql = (
            "SELECT COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "AND substr(timestamp, 1, 10) BETWEEN ? AND ?"
        )
        with self._lock:
            row = self._c.execute(
                sql, (*_COMPLETED_EVENT_TYPES, start_date, end_date)
            ).fetchone()
        return int(row["c"])

    def completed_count_by_person_in_range(
        self, start_date: str, end_date: str
    ) -> dict[str, int]:
        """Per-person completions within ``[start_date, end_date]`` (date part)."""
        sql = (
            "SELECT person_entity AS k, COUNT(*) AS c FROM log_events "
            f"WHERE event_type IN ({_COMPLETED_PLACEHOLDERS}) "
            "AND substr(timestamp, 1, 10) BETWEEN ? AND ? "
            "GROUP BY person_entity"
        )
        with self._lock:
            rows = self._c.execute(
                sql, (*_COMPLETED_EVENT_TYPES, start_date, end_date)
            ).fetchall()
        return {row["k"]: row["c"] for row in rows if row["k"] is not None}

    def fetch_all(self) -> list[dict[str, Any]]:
        """Return every log event, oldest first."""
        with self._lock:
            rows = self._c.execute(
                "SELECT * FROM log_events ORDER BY timestamp ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def query_history(
        self,
        event_types: Sequence[str],
        person_entity: str | None,
        room: str | None,
        category: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return a filtered history page and the total matching row count."""
        conditions: list[str] = []
        params: list[Any] = []
        if event_types:
            placeholders = ", ".join("?" for _ in event_types)
            conditions.append(f"event_type IN ({placeholders})")
            params.extend(event_types)
        for column, value in (
            ("person_entity", person_entity),
            ("room", room),
            ("category", category),
        ):
            if value is not None:
                conditions.append(f"{column} = ?")
                params.append(value)

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        with self._lock:
            count_row = self._c.execute(
                f"SELECT COUNT(*) AS c FROM log_events{where}", params
            ).fetchone()
            rows = self._c.execute(
                "SELECT * FROM log_events"
                f"{where} ORDER BY timestamp DESC, event_id DESC LIMIT ? OFFSET ?",
                (*params, limit, offset),
            ).fetchall()
        return [dict(row) for row in rows], int(count_row["c"])

    def export_to_file(self, path: str, fmt: str) -> str:
        """Export the whole log to ``path`` as ``json`` or ``csv`` (§8)."""
        rows = self.fetch_all()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if fmt == "csv":
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(_LOG_COLUMNS))
                writer.writeheader()
                writer.writerows(rows)
        else:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(rows, handle, ensure_ascii=False, indent=2)
        return path


# ===========================================================================
# Async HA wrapper around LogDatabase — §3.3
# ===========================================================================
class LogStore:
    """Thin async wrapper that runs all SQLite work in an executor thread."""

    def __init__(self, hass: HomeAssistant, db_path: str) -> None:
        self._hass = hass
        self._db = LogDatabase(db_path)
        self._remove_stop_listener: Callable[[], None] | None = None

    async def _run(self, func: Callable[..., _T], *args: Any) -> _T:
        return await self._hass.async_add_executor_job(func, *args)

    async def async_setup(self) -> None:
        await self._run(self._db.connect)
        self._remove_stop_listener = self._hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP,
            self._async_close_on_stop,
        )

    async def async_close(self) -> None:
        if self._remove_stop_listener is not None:
            remove_stop_listener = self._remove_stop_listener
            self._remove_stop_listener = None
            remove_stop_listener()
        await self._run(self._db.close)

    async def _async_close_on_stop(self, _event: Event[Any]) -> None:
        self._remove_stop_listener = None
        await self.async_close()

    async def async_add_event(self, event: LogEvent) -> None:
        await self._run(self._db.insert, event)

    async def async_completed_count_by_person(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_person)

    async def async_completed_count_by_room(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_room)

    async def async_completed_count_by_category(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_category)

    async def async_completed_count_by_task(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_task)

    async def async_snoozed_count(self) -> int:
        return await self._run(self._db.snoozed_count)

    async def async_most_snoozed_tasks(self, limit: int = 10) -> list[tuple[str, int]]:
        return await self._run(self._db.most_snoozed_tasks, limit)

    async def async_completed_count_by_month(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_month)

    async def async_completed_count_by_year(self) -> dict[str, int]:
        return await self._run(self._db.completed_count_by_year)

    async def async_high_completed_on_time_count(self) -> int:
        return await self._run(self._db.high_completed_on_time_count)

    async def async_overdue_at_completion_count(self) -> int:
        return await self._run(self._db.overdue_at_completion_count)

    async def async_completion_source_distribution(self) -> dict[str, int]:
        return await self._run(self._db.completion_source_distribution)

    async def async_completed_count_in_range(
        self, start_date: str, end_date: str
    ) -> int:
        return await self._run(self._db.completed_count_in_range, start_date, end_date)

    async def async_completed_count_by_person_in_range(
        self, start_date: str, end_date: str
    ) -> dict[str, int]:
        return await self._run(
            self._db.completed_count_by_person_in_range, start_date, end_date
        )

    async def async_export(self, path: str, fmt: str) -> str:
        return await self._run(self._db.export_to_file, path, fmt)

    async def async_query_history(
        self,
        *,
        event_types: Sequence[str],
        person_entity: str | None,
        room: str | None,
        category: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        return await self._run(
            self._db.query_history,
            event_types,
            person_entity,
            room,
            category,
            limit,
            offset,
        )
