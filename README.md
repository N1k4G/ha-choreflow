# ChoreFlow — Home Assistant Integration

[![Tests](https://github.com/N1k4G/ha-choreflow/actions/workflows/test.yaml/badge.svg)](https://github.com/N1k4G/ha-choreflow/actions/workflows/test.yaml)
[![Hassfest](https://github.com/N1k4G/ha-choreflow/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/N1k4G/ha-choreflow/actions/workflows/hassfest.yaml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

Presence-aware household **chore manager** for Home Assistant. ChoreFlow keeps
recurring and one-off chores small and actionable, prioritises what is due, and
nudges the people who are **home** with a one-task-at-a-time push chain — then
logs everything for long-term insight.

> **Target platform:** Home Assistant 2026.6+ · config-flow-only · fully local.

---

## Features

- Recurring task rules (`every_n_days`, specific `weekdays`) and one-off tasks.
- Importance `high` / `normal` / `low`, rooms, categories, visibility and
  assignment (fixed person or random).
- **Presence-aware push chain**: starts at 17:30 (weekdays) / 10:00 (weekends),
  catches up on return until the 20:00 day end, max five tasks per person/day.
  One task per push with **Done / Snooze / Open dashboard** actions handled by
  ChoreFlow itself (no user automation needed).
- Smart selection: urgency pool → per-person top-5 → soft rotation, room
  bundling for follow-ups, and `high` tasks protected from starvation.
- Reservations prevent double work; time-critical `high` tasks may go to several
  people in parallel on the last day.
- **To-do sync** (MVP 0.2): import items from a `todo.*` list, and push
  ChoreFlow tasks back to it — mirroring creation, completion, reopen and
  deletion both ways.
- **Calendar tasks** (MVP 0.2): all-day events (e.g. waste collection) become
  `high` tasks due the day before, with change/delete reconciliation.
- Global and per-person sensors + binary sensors.
- Durable SQLite event log (independent of the recorder) with JSON/CSV export.
- Diagnostics, repair issues, German & English UI.

---

## Installation

### HACS (custom repository)

1. HACS → **⋮** → **Custom repositories**.
2. Add `https://github.com/N1k4G/ha-choreflow`, category **Integration**.
3. Install **ChoreFlow** and restart Home Assistant.

### Manual

Copy `custom_components/choreflow` into your Home Assistant
`config/custom_components/` directory and restart.

---

## Setup

**Settings → Devices & Services → Add Integration → ChoreFlow.** The flow walks
through:

1. **Name** of the instance.
2. **Persons** that take part (`person.*`).
3. Per person: **notify service** (`notify.mobile_app_*`), presence-required,
   weekday/weekend push toggles.
4. **Schedule**: weekday/weekend start time, day end, max tasks per day.
5. **To-do sync** (optional): list entity, import + push/completion flags,
   import defaults. With "Push tasks and completion to to-do" enabled, open
   ChoreFlow tasks (due today, overdue, or with no due date) are created as
   items on the list and kept in sync.
6. **Calendar sync** (optional): calendar entity, summary match terms, due
   offset (default −1 = day before).

All values are editable later via the integration's **Configure** (options).

You manage task rules and one-off tasks through the services below (a Lovelace
card can be added later — the backend already exposes everything it needs).

---

## Entities

**Global:** `sensor.choreflow_open_tasks`, `…_due_tasks`, `…_overdue_tasks`,
`…_completed_today`, `…_completed_this_week`, `…_active_chains`
(the open-tasks sensor lists upcoming tasks in its attributes).
The preview contains stable task IDs, is capped at 30 items, and exposes
`total`/`truncated`. Use `choreflow.get_tasks` for complete, filtered and
paginated lists.

**Per enabled person:** `…_<person>_open_tasks`, `…_due_tasks`,
`…_completed_today`, `…_tasks_remaining_today`,
`binary_sensor.…_<person>_has_due_tasks`, `…_<person>_chain_active`.

---

## Services

| Service | Purpose |
|---------|---------|
| `choreflow.create_task` | Create a one-off task. |
| `choreflow.update_task` | Update fields of a task. |
| `choreflow.delete_task` | Delete a task. |
| `choreflow.complete_task` | Mark a task completed (and push the next). |
| `choreflow.snooze_task` | Postpone the reminder (keeps the due date). |
| `choreflow.start_daily_flow` | Start the daily push chain (one/all persons). |
| `choreflow.send_next_task` | Advance a person's chain. |
| `choreflow.sync_todo` | Run a to-do synchronisation now. |
| `choreflow.rebuild_calendar_tasks` | Reconcile calendar-based tasks now. |
| `choreflow.export_log` | Export the event log to `choreflow_exports/` (JSON/CSV). |
| `choreflow.get_task` | Return full detail for a single task (used by the edit dialog). |
| `choreflow.get_tasks` | Return filtered, paginated task data for dashboards. |
| `choreflow.get_history` | Return filtered, paginated log history. |

See **Developer Tools → Actions** for the full field schemas (also localised
de/en).

---

## Dashboard card

ChoreFlow bundles a Lovelace custom card (`custom:choreflow-card`) that is
**auto-registered** on setup — no manual resource needed. Add it to a dashboard
and point it at your entities:

```yaml
type: custom:choreflow-card
title: Haushalt
entities:
  open_tasks: sensor.choreflow_open_tasks
```

The card is a standalone Lit/TypeScript project in [card/](card/) and talks to
the integration only through the documented service/sensor contract, so it can
later be published as its own HACS frontend repository without backend changes.

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). The engine is pure and HA-free; tests
are split into pure unit tests and HA integration tests
(see [tests/README.md](tests/README.md)).

```bash
pip install -r requirements_test.txt
pytest --cov=custom_components/choreflow
```

The card lives in [card/](card/) (independent npm project). After changing it,
rebuild and refresh the bundled artifact:

```bash
cd card
npm install
npm run lint   # tsc --noEmit
npm run build  # → dist/choreflow-card.js
cp dist/choreflow-card.js ../custom_components/choreflow/www/choreflow-card.js
```

---

## License

[MIT](LICENSE) © 2026 N1k4G

The bundled dashboard card includes third-party software. See
[Third-party notices](THIRD_PARTY_NOTICES.md) for copyright and license details.
