# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Accept syntactically valid notify service ids before their integrations have
  registered the services.
- Remove entry-scoped `.storage` data on uninstall while retaining the durable
  event log and user exports.
- Replace household-specific starter tasks with a smaller generic seed pool.
- Restore required license notices for dependencies bundled into the card.

## [1.1.1] - 2026-06-30

HACS-compatible, config-flow-only integration targeting Home Assistant 2026.6,
CI via hassfest, HACS validation, ruff, mypy (`--strict`) and pytest.

### Added — To-do export
- "Push tasks and completion to to-do" (the former "Sync completion to to-do"
  option) now also exports ChoreFlow tasks to the linked to-do list: open tasks
  that are due today, overdue, or have no due date are created as to-do items
  and linked back. Creating, completing, reopening and deleting/pruning such a
  task is mirrored to its to-do item. A daily reconcile back-fills tasks that
  become due later and repairs drift.

### Added — MVP 0.1
- Multi-step config flow and options flow (persons, per-person notify targets,
  schedule, to-do and calendar setup); German & English UI.
- Data model and two-tier persistence: HA `Store` JSON state + own SQLite event
  log (independent of the recorder) with evaluation queries.
- Pure, HA-free engine: recurrence, urgency scoring/selection (top-5, room
  bundling, `high` anti-starvation), reservations, schedule windows.
- Presence-aware push chain: start times, catch-up, day end, daily limit; one
  task per push with self-handled Done/Snooze/Open-dashboard actions.
- Global and per-person sensors + binary sensors; logbook, diagnostics, repairs.
- Services: `create_task`, `update_task`, `delete_task`, `complete_task`,
  `snooze_task`, `start_daily_flow`, `send_next_task`.

### Added — MVP 0.2
- To-do synchronisation: import items, bidirectional completion sync, dedup,
  graceful handling of an unavailable list (`sync_todo` service).
- Calendar tasks: all-day events → `high` tasks due the day before, with
  change/delete reconciliation and dedup (`rebuild_calendar_tasks` service).
- `export_log` service (JSON/CSV).

### Added - Dashboard API
- Versioned, compact open-task sensor payload with stable task IDs and
  truncation metadata.
- Paginated `get_tasks` and `get_history` response services for dashboard
  filters and history.
- Detailed per-person daily chain attributes.
- Estimated duration propagated from task rules to task instances and CRUD.
- Dashboard actions validate visibility, assignment and enabled persons.

### Added - Lovelace card
- Bundled `choreflow-card` Lovelace custom card (Lit/TypeScript, source in
  `card/`), auto-registered as a frontend resource — no manual setup. The card
  is decoupled from the backend (uses only the documented service/sensor
  contract) and can later be split into its own HACS frontend repository.
