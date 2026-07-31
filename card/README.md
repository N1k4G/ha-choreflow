# ChoreFlow Card (`ha-choreflow-card`)

A calm, compact Lovelace custom card for the **ChoreFlow** Home Assistant
integration. It is built as an operational tool for small household chores —
fast to scan, adult in tone, and free of points, leaderboards, badges,
confetti or playful language.

- Header KPIs: Offen · Fällig · Überfällig · Heute erledigt
- Per-person chain status (active/inactive, completed today, remaining push slots)
- Urgency-sorted task list, optionally grouped by room
- Person / room / category filters
- Per-task actions (Erledigen, Später erinnern) with pending, error and double-click handling
- Create dialog with an expandable visibility & assignment section
- Paginated history backed by `choreflow.get_history`
- Light/Dark automatically via the active HA theme — **no hard-coded colors**

---

## Installation

The card is **bundled with the ChoreFlow integration** and auto-registered on
setup — no manual resource step needed. Install ChoreFlow via HACS or manually
(see the [integration README](../README.md)).

### Manual resource (standalone use)

If you want to load the card independently of the integration:

1. `npm install && npm run build`
2. Copy `dist/choreflow-card.js` to `config/www/choreflow-card.js`.
3. Settings → Dashboards → ⋮ → *Resources* → add
   `/local/choreflow-card.js` as a **JavaScript module**.

---

## Configuration

Entity ids are renameable, so every sensor is configurable. A visual editor
(`getConfigElement`) is provided; the YAML below is equivalent.

```yaml
type: custom:choreflow-card
title: Haushalt
entities:
  open_tasks: sensor.choreflow_open_tasks        # REQUIRED
  due_tasks: sensor.choreflow_due_tasks
  overdue_tasks: sensor.choreflow_overdue_tasks
  completed_today: sensor.choreflow_completed_today
  completed_this_week: sensor.choreflow_completed_this_week
  active_chains: sensor.choreflow_active_chains
persons:
  - entity: person.alice
    open_tasks: sensor.choreflow_alice_open_tasks
    due_tasks: sensor.choreflow_alice_due_tasks
    completed_today: sensor.choreflow_alice_completed_today
    remaining_today: sensor.choreflow_alice_tasks_remaining_today
    has_due_tasks: binary_sensor.choreflow_alice_has_due_tasks
    chain_active: binary_sensor.choreflow_alice_chain_active
show_create: true
show_history: true
default_person: person.alice
default_room: null
```

| Option | Type | Default | Notes |
|---|---|---|---|
| `entities.open_tasks` | string | — | **Required.** The only sensor with the `open_tasks` attribute. |
| `entities.*` | string | optional | A missing sensor only hides the affected fact. |
| `persons[]` | list | `[]` | Per-person chain & KPI sensors. |
| `show_create` | bool | `true` | Hides the create button & dialog when `false`. |
| `show_history` | bool | `true` | Hides the history tab when `false`. |
| `default_person` | string | first person | `person_entity` used for completions. |
| `default_room` | string\|null | `null` | Pre-selects the room filter. |

### Missing-sensor / read-only fallback

- **Required sensor missing** — if `entities.open_tasks` cannot be resolved the
  card renders a single, calm error state naming the missing entity instead of
  crashing the dashboard.
- **Optional sensor missing** — only the affected number is hidden (`—`); the
  rest of the card keeps working.
- **No `task_id`** — tasks coming from the attribute feed without a `task_id`
  render without action buttons (read-only row), so the card never offers an
  action it cannot perform.

---

## Data contract

The card reads reactively from `hass.states` (no polling, no `fetch`,
no `localStorage`):

- **Counts** come from the global/per-person sensors.
- **The task list** comes from `sensor.choreflow_open_tasks` →
  `attributes.open_tasks` (urgency-sorted, max 30, `truncated` flag respected).
- **Chain facts** come from each `binary_sensor.*_chain_active`'s attributes
  (`active`, `tasks_completed_today`, `remaining_today`, `daily_limit`).

Mutations and queries go exclusively through the Home Assistant service API:

| Action | Service | Notes |
|---|---|---|
| Erledigen | `choreflow.complete_task` | `{ task_id, person_entity, source: "dashboard" }` |
| Später erinnern | `choreflow.snooze_task` | does **not** change the due date; may end today's chain |
| Tag starten | `choreflow.start_daily_flow` | per person |
| Nächste Aufgabe | `choreflow.send_next_task` | per person |
| Erstellen | `choreflow.create_task` | optimistic UI from returned `task_id` |
| Verlauf | `choreflow.get_history` | `return_response`; completions only without `event_types` |
| Volle Liste | `choreflow.get_tasks` | `return_response`; paged `Page<T>` envelope |

`ServiceValidationError`s (unknown/closed task, missing visibility/assignment,
disabled person) are caught and surfaced as quiet, non-blocking inline feedback
on the affected task — never as a modal.

---

## Design rationale

**It is a tool, not a landing page.** The densest information (the four KPIs and
the task rows) is reachable without scrolling on a 360–480 px column, and the
same layout stays clean in wide dashboard columns. There is no nested-card or
marketing composition.

**Urgency is encoded three ways, never colour alone:** a left accent edge, a
leading icon, and a text label. `high` (warning edge + priority chevron +
„Wichtig") and `overdue` (error edge + alert glyph + „Überfällig · N Tage") stay
distinguishable for colour-blind users and in both themes.

**Microinteractions are short and quiet** — a 0.8 s spinner during a pending
mutation, an optimistic settled state, and an auto-dismissing error line.
Everything respects `prefers-reduced-motion`.

### Design tokens (no fixed colours)

All colour comes from HA theme variables, so the card inherits the user's theme
and switches light/dark automatically:

| Token | Variable | Use |
|---|---|---|
| Text primary | `--primary-text-color` | titles, numbers |
| Text secondary | `--secondary-text-color` | labels, meta |
| Surface | `--card-background-color` | the card |
| Sunken | `--primary-background-color` | strips, inputs, segmented bg |
| Accent | `--primary-color` | today/primary actions |
| Divider | `--divider-color` | rules, borders |
| Danger | `--error-color` | overdue edge/text, errors |
| Attention | `--warning-color` | `high` edge/text, snoozed |
| Success | `--success-color` (→ `--primary-color`) | active chain, complete |
| Disabled | `--disabled-text-color` | inactive chain dot |

Non-colour tokens: radius `≤ 8 px` (6 px controls, 4 px chips), row min height
~48 px, action targets 32–34 px, type 10.5–22 px on a Roboto/HA stack.

---

## Development

```bash
npm install
npm run watch   # rebuild on change → dist/choreflow-card.js
npm run lint    # tsc --noEmit
npm run build   # minified production bundle
```

See [`BACKEND.md`](./BACKEND.md) for the small list of backend additions that
would let the card drop its current workarounds.

## License

MIT. The production bundle also contains third-party software covered by the
[repository's third-party notices](../THIRD_PARTY_NOTICES.md).
