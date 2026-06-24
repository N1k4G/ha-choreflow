# Claude Design Prompt: ChoreFlow Card

## Aufgabe

Entwirf eine hochwertige Home-Assistant-Lovelace-Custom-Card fuer **ChoreFlow**.
Liefere ein interaktives High-Fidelity-Mockup und danach eine produktionsnahe
Lit-/TypeScript-Implementierung. Die Card ist ein ruhiges, kompaktes
Arbeitswerkzeug fuer kleine Haushaltsaufgaben: erwachsen, schnell scanbar und
ohne Punkte, Ranglisten, Badges, Konfetti oder spielerische Sprache.

## Backend-Vertrag

ChoreFlow hat eine einzelne Config Entry. Entity-IDs koennen umbenannt werden
und muessen deshalb ueber die Card-Config konfigurierbar sein.

Typische globale Sensoren:

- `sensor.choreflow_open_tasks`
- `sensor.choreflow_due_tasks`
- `sensor.choreflow_overdue_tasks`
- `sensor.choreflow_completed_today`
- `sensor.choreflow_completed_this_week`
- `sensor.choreflow_active_chains`

Typische Sensoren je Person:

- `sensor.choreflow_<slug>_open_tasks`
- `sensor.choreflow_<slug>_due_tasks`
- `sensor.choreflow_<slug>_completed_today`
- `sensor.choreflow_<slug>_tasks_remaining_today`
- `binary_sensor.choreflow_<slug>_has_due_tasks`
- `binary_sensor.choreflow_<slug>_chain_active`

Der `chain_active`-Binary-Sensor liefert als Attribute `api_version`,
`person_entity`, `date`, `started`, `active`, `pending_catchup`,
`current_task_id`, `current_task_title`, `tasks_sent_today`,
`tasks_completed_today`, `daily_limit`, `remaining_today` und
`ended_reason`.

Nur der globale Open-Tasks-Sensor besitzt das Attribut `open_tasks`. Es ist
nach Dringlichkeit sortiert, auf 30 Eintraege begrenzt und sieht aktuell exakt
so aus:

```ts
type CurrentOpenTask = {
  task_id: string;
  title: string;
  room: string;
  category: string;
  importance: "high" | "normal" | "low";
  estimated_duration_minutes: number | null;
  due_date: string | null; // YYYY-MM-DD
};
```

Der Sensor liefert ausserdem `api_version`, `total` und `truncated`.

Raeume und Kategorien sind freie Texte, keine festen Enums. Leite Filterwerte
aus den vorhandenen Aufgaben ab und erlaube im Erstellen-Dialog eigene Werte.

Vollstaendige Aufgaben werden ueber den response-returning Service
`choreflow.get_tasks` geladen. Kapsle den Payload-Zugriff in einem Adapter:

```ts
type ChoreFlowTask = CurrentOpenTask & {
  task_rule_id: string | null;
  description?: string | null;
  deadline: string | null;
  status: "open" | "completed" | "deleted";
  visibility_mode: "all_enabled_persons" | "selected_persons";
  assignment_person?: string | null;
  assignment_mode: "random" | "assigned";
  visibility_persons: string[];
  source: "rule" | "dashboard" | "todo_sync" | "calendar" | "manual";
  created_at: string;
  completed_at: string | null;
  completed_by: string | null;
  completion_source: string | null;
};
```

Beide Query-Services liefern:

```ts
type Page<T> = {
  api_version: 1;
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
};
```

`choreflow.get_history` liefert echte Logeintraege und ist die Datenquelle
fuer den History-Tab. Keine Demo-Historie in der ausgelieferten Runtime. Ohne
`event_types` werden ausschliesslich Erledigungen geliefert (`task_completed`
und `task_completed_from_todo`). Jeder Eintrag hat folgende Form:

```ts
type ChoreFlowEventType =
  | "task_created"
  | "task_updated"
  | "task_deleted"
  | "task_notified"
  | "task_completed"
  | "task_snoozed"
  | "task_missed_no_presence"
  | "task_expired"
  | "task_synced_from_todo"
  | "task_completed_from_todo"
  | "calendar_task_created"
  | "calendar_task_removed";

type HistoryEvent = {
  event_id: string;
  event_type: ChoreFlowEventType;
  task_id: string | null;
  task_rule_id: string | null;
  title: string | null;
  room: string | null;
  category: string | null;
  importance: "high" | "normal" | "low" | null;
  person_entity: string | null;
  timestamp: string; // ISO 8601 mit Zeitzone, absteigend sortiert
  source: string | null;
  completion_source: string | null;
  overdue_days_at_completion: number | null;
  decision_reason: string | null;
};
```

## Services

Nutze ausschliesslich Home Assistants Service-API. Mutationen werden ueber
`hass.callService("choreflow", service, data)` ausgeloest. Fuer
`get_tasks` und `get_history` muss der aktuelle HA-Mechanismus fuer
Service-Responses mit `return_response` verwendet werden. Keine `fetch()`-
oder eigenen HTTP-Aufrufe.

```ts
complete_task: {
  task_id: string;
  person_entity: string;
  source: "dashboard";
}
snooze_task: { task_id: string; person_entity: string }
delete_task: { task_id: string }
start_daily_flow: { person_entity?: string }
send_next_task: { person_entity: string }

create_task: {
  title: string;
  description?: string;
  room?: string;
  category?: string;
  importance?: "high" | "normal" | "low";
  estimated_duration_minutes?: number;
  due_date?: string;
  visibility_mode?: "all_enabled_persons" | "selected_persons";
  visibility_persons?: string[];
  assignment_mode?: "random" | "assigned";
  assignment_person?: string;
}

update_task: {
  task_id: string;
  title?: string;
  description?: string;
  room?: string;
  category?: string;
  importance?: "high" | "normal" | "low";
  estimated_duration_minutes?: number;
  due_date?: string;
  visibility_mode?: "all_enabled_persons" | "selected_persons";
  visibility_persons?: string[];
  assignment_mode?: "random" | "assigned";
  assignment_person?: string;
}

get_tasks: {
  status?: "open" | "completed" | "deleted" | "all";
  person_entity?: string;
  person_scope?: "visible" | "assigned";
  room?: string;
  category?: string;
  limit?: number;  // 1-100
  offset?: number;
}

get_history: {
  event_types?: string[];
  person_entity?: string;
  room?: string;
  category?: string;
  limit?: number;  // 1-100
  offset?: number;
}
```

Mutierende Services (`create_task`, `update_task`, `delete_task`,
`complete_task`, `snooze_task`) liefern bei `return_response` ein
`{ success: true, task_id: string }`; nutze die `task_id` aus `create_task`
fuer optimistische UI. Sie koennen einen `ServiceValidationError` werfen
(unbekannte oder nicht offene Aufgabe, fehlende Sichtbarkeit/Zuweisung, nicht
aktivierte Person). Fange diesen ab und zeige ihn als ruhiges,
nicht-blockierendes Feedback an der betroffenen Aufgabe.

Snooze aendert das Faelligkeitsdatum nicht und kann bei normalen/niedrigen
Aufgaben die heutige Kette beenden. Beschrifte es als `Spaeter erinnern`.

## Card-Config

```yaml
type: custom:choreflow-card
title: Haushalt
entities:
  open_tasks: sensor.choreflow_open_tasks
  due_tasks: sensor.choreflow_due_tasks
  overdue_tasks: sensor.choreflow_overdue_tasks
  completed_today: sensor.choreflow_completed_today
  completed_this_week: sensor.choreflow_completed_this_week
  active_chains: sensor.choreflow_active_chains
persons:
  - entity: person.niklas
    open_tasks: sensor.choreflow_niklas_open_tasks
    due_tasks: sensor.choreflow_niklas_due_tasks
    completed_today: sensor.choreflow_niklas_completed_today
    remaining_today: sensor.choreflow_niklas_tasks_remaining_today
    has_due_tasks: binary_sensor.choreflow_niklas_has_due_tasks
    chain_active: binary_sensor.choreflow_niklas_chain_active
show_create: true
show_history: true
default_person: person.niklas
default_room: null
```

Implementiere `getConfigElement()`, `getStubConfig()`, `setConfig()`,
reaktiven `hass`-Zugriff und Config-Validierung. Fehlende optionale Sensoren
blenden nur den betroffenen Bereich aus. Ein fehlender Open-Tasks-Sensor ergibt
einen verstaendlichen Card-Fehlerzustand.

## UX

Baue die echte Arbeitsansicht, keine Landingpage:

1. Kompakter Kopf: Offen, Faellig, Ueberfaellig, Heute erledigt.
2. Kettenstatus je Person: aktiv/inaktiv, heute erledigt und verbleibende
   Push-Slots als getrennte Fakten.
3. Nach Dringlichkeit sortierte Aufgabenliste, optional nach Raum gruppiert.
4. Filter fuer Person, Raum und Kategorie ueber `get_tasks`.
5. Pro Aufgabe: Titel, Raum, Kategorie, Wichtigkeit, Faelligkeit und optional
   geschaetzte Dauer.
6. Mit `task_id`: Icon-Aktionen fuer Erledigen und Spaeter mit Tooltips,
   Pending-State, Fehlerfeedback und Doppelklickschutz.
7. Erstellen-Dialog; Sichtbarkeit/Zuweisung in einem erweiterten Bereich.
8. Ruhiger Leerzustand: `Fuer diesen Filter ist nichts offen.`
9. Paginierte Historie ueber `get_history`.

Keine Emojis als UI-Icons. Nutze Home-Assistant-`ha-icon`/MDI-Icons,
Icon-Buttons und Tooltips. Microinteractions kurz und ruhig; beachte
`prefers-reduced-motion`.

## Gestaltung

- Ruhig, klar, wohnlich, aber als kompaktes operatives Werkzeug.
- Keine verschachtelten Cards oder Marketing-Komposition.
- Maximal 8 px Radius; stabile Zeilenhoehen und Aktionsflaechen.
- Dringlichkeit ueber Akzentkante, Icon und Text, nicht nur Farbe.
- `high` und `overdue` muessen unterscheidbar sein.
- Optimiert fuer 360-480 px Breite, zugleich sauber in breiten Spalten.
- Light/Dark automatisch ueber das aktive HA-Theme.

Farben ausschliesslich ueber HA-Theme-Variablen:
`--primary-text-color`, `--secondary-text-color`,
`--card-background-color`, `--primary-background-color`, `--primary-color`,
`--divider-color`, `--error-color`, `--warning-color`,
`--success-color` (Fallback `--primary-color`) und
`--disabled-text-color`. Keine Hex-/RGB-Farben.

## Technik und Output

- LitElement + TypeScript, gebuendelt als `choreflow-card.js`.
- Daten reaktiv aus `hass.states`; kein Polling.
- Keine `fetch()`-Aufrufe, kein SQLite-/Dateizugriff.
- Kein `localStorage` oder `sessionStorage`.
- Registrierung als `custom:choreflow-card` inklusive `window.customCards`.
- Barrierearme Labels, Tastaturbedienung, Dialog-Fokus und gute Touch-Ziele.
- Separates HACS-Frontend-Repo `ha-choreflow-card` mit `package.json`,
  Build-Konfiguration und README.

Liefere:

1. Interaktives Mockup mit realistischen Beispieldaten, schmal/breit, Light/Dark.
2. Kurze Designbegruendung und Design-Tokens ohne feste Farben.
3. Vollstaendige Lit-/TypeScript-Quellen und Build-Konfiguration.
4. README mit Installation, YAML, Datenvertrag und Read-only-Fallback.
5. Abschliessend eine knappe Liste noch benoetigter Backend-Erweiterungen.
