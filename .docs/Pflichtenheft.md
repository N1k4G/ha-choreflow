# Pflichtenheft: ChoreFlow Home Assistant Integration

> **Dokumenttyp:** Pflichtenheft (technische Umsetzungsspezifikation)
> **Basis:** Lastenheft ChoreFlow v0.1
> **Zielversion:** ChoreFlow 0.1 / 0.2 (MVP)
> **Home-Assistant-Zielversion:** 2026.6 (Core 2026.6.x)
> **Implementierung durch:** Claude Sonnet
> **Status:** Entwurf zur Umsetzung
> **Dokumentversion:** 1.0

---

## 0. Hinweise für die Implementierung (Claude Sonnet)

Dieses Dokument ist die verbindliche Umsetzungsgrundlage. Es übersetzt die *Was*-Anforderungen des Lastenhefts in *Wie*-Spezifikationen. Wo das Lastenheft offen ließ, sind hier verbindliche Festlegungen getroffen. Abweichungen nur nach Rücksprache.

**Grundregeln für die Umsetzung:**

1. **Config-Flow-only.** Keine YAML-Konfiguration der Integration. Alle Einstellungen über Config Flow und Options Flow. YAML-Beispiele aus dem Lastenheft sind ausschließlich Datenmodell-Illustrationen, kein Konfigurationsformat.
2. **Aufgabenregeln werden im internen Store gepflegt**, erzeugt/bearbeitet über Services und (später) Dashboard. Es gibt **keine** von der Integration eingelesene Tasks-YAML-Datei.
3. **Keine blockierende I/O im Event Loop.** Alle Datei-/DB-Zugriffe asynchron oder über `hass.async_add_executor_job`.
4. **HA 2026.6 als Zielplattform.** Die Legacy-Template-Syntax wurde in 2026.6 entfernt — in Doku, Beispielen und Card ausschließlich aktuelle Syntax verwenden.
5. **Zeit ist injizierbar.** Keine direkten `datetime.now()`-Aufrufe in der Kernlogik. Stattdessen eine `Clock`-Abstraktion (siehe §6.7), damit Zeitfenster testbar bleiben.
6. **Determinismus & Nachvollziehbarkeit.** Jede automatische Entscheidung (Auswahl, Nicht-Auswahl, kein Push) wird begründet protokolliert.

**Empfohlene Bearbeitungsreihenfolge:** §6 (Architektur) → §7 (Datenmodell) → §8 (Persistenz) → §9 (Kernlogik) → §10 (HA-Integration) → §11 (Sync/Kalender) → §12 (Sensoren/Services) → §13 (Tests).

---

## 1. Architekturüberblick

### 1.1 Komponentenschnitt

```text
custom_components/choreflow/
├─ __init__.py            # Setup, Entry-Lifecycle, Platform-Forwarding
├─ manifest.json
├─ const.py               # Domain, Keys, Defaults, Event-Typen
├─ config_flow.py         # Config Flow + Options Flow
├─ coordinator.py         # DataUpdateCoordinator: hält Laufzeitzustand, triggert Updates
├─ models.py              # Dataclasses: TaskRule, TaskInstance, PushChainState, ...
├─ store.py               # Persistenz-Layer (HA Store für State + SQLite für Log)
├─ engine/
│  ├─ scheduler.py        # Tagesfenster, Startzeiten, Nachholen, Tagesende
│  ├─ selector.py         # Dringlichkeitspool, Top-5, Raum-Bündelung, Rotation
│  ├─ reservation.py      # Reservierungen, Doppelbearbeitungs-Schutz
│  ├─ recurrence.py       # Wiederholungsregeln → fällige Instanzen
│  └─ clock.py            # Zeit-Abstraktion (injizierbar)
├─ sources/
│  ├─ todo_sync.py        # todo.* Import + bidirektionaler Erledigt-Sync
│  └─ calendar_source.py  # Kalender → high-Aufgaben, Dedup, Änderungserkennung
├─ notify.py              # Push-Versand + Notification-Action-Event-Listener
├─ logbook.py             # Event-Logging in SQLite, Auswertungs-Queries
├─ sensor.py
├─ binary_sensor.py
├─ services.py            # Service-Registrierung + Handler
├─ services.yaml
├─ diagnostics.py
├─ repairs.py
└─ translations/
   ├─ en.json
   └─ de.json
```

### 1.2 Verantwortlichkeiten (Trennung)

| Modul | Verantwortung | HA-Abhängig? |
|-------|---------------|--------------|
| `engine/*` | Reine Logik: Auswahl, Recurrence, Reservierung, Zeitfenster | Nein (testbar ohne HA) |
| `models.py` | Datenstrukturen | Nein |
| `store.py` | Persistenz | Teilweise (HA Store) |
| `coordinator.py` | Orchestrierung, Laufzeitzustand, Update-Push | Ja |
| `sources/*`, `notify.py`, `sensor.py`, `services.py` | HA-Anbindung | Ja |

Die `engine`-Module dürfen **keine** `homeassistant`-Imports enthalten (außer Typing). Das ist die Grundlage der Unit-Testbarkeit.

---

## 2. Datenmodell (verbindlich)

Alle Modelle als `@dataclass` in `models.py`. Enums für feste Wertebereiche.

### 2.1 Enums

```python
class Importance(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class UrgencyType(StrEnum):
    MANDATORY_DATE = "mandatory_date"
    DEADLINE = "deadline"

class TaskStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"
    DELETED = "deleted"

class TaskSource(StrEnum):
    RULE = "rule"
    DASHBOARD = "dashboard"
    TODO_SYNC = "todo_sync"
    CALENDAR = "calendar"
    MANUAL = "manual"

class AssignmentMode(StrEnum):
    ASSIGNED = "assigned"
    RANDOM = "random"

class VisibilityMode(StrEnum):
    ALL_ENABLED_PERSONS = "all_enabled_persons"
    SELECTED_PERSONS = "selected_persons"

class RecurrenceType(StrEnum):
    EVERY_N_DAYS = "every_n_days"
    WEEKDAYS = "weekdays"          # bestimmte Wochentage
    ONCE = "once"                  # einmalig (keine Wiederholung)
```

### 2.2 TaskRule

```python
@dataclass
class TaskRule:
    id: str                              # stabil, slug-artig
    title: str
    description: str | None
    room: str
    category: str
    importance: Importance
    estimated_duration_minutes: int | None
    recurrence_type: RecurrenceType
    recurrence_interval: int | None      # bei every_n_days
    recurrence_weekdays: list[int] | None  # 0=Mo..6=So, bei weekdays
    urgency_type: UrgencyType | None
    deadline: date | None
    visibility_mode: VisibilityMode
    visibility_persons: list[str]        # person.* entity_ids
    assignment_mode: AssignmentMode
    assignment_person: str | None
    enabled: bool = True
```

### 2.3 TaskInstance

```python
@dataclass
class TaskInstance:
    id: str                              # z.B. inst_2026_06_18_clean_bathroom_sink
    rule_id: str | None                  # None bei einmaligen Aufgaben
    title: str
    description: str | None
    room: str
    category: str
    importance: Importance
    urgency_type: UrgencyType | None
    due_date: date | None
    deadline: date | None
    status: TaskStatus
    source: TaskSource
    visibility_mode: VisibilityMode
    visibility_persons: list[str]
    assignment_mode: AssignmentMode
    assignment_person: str | None
    external_refs: ExternalRefs | None
    created_at: datetime
    completed_at: datetime | None
    completed_by: str | None             # person.* entity_id
    completion_source: str | None        # push | dashboard | todo
```

### 2.4 ExternalRefs

```python
@dataclass
class TodoRef:
    entity_id: str
    item_uid: str

@dataclass
class CalendarRef:
    entity_id: str
    event_uid: str
    task_rule_id: str                    # Teil des Dedup-Keys

@dataclass
class ExternalRefs:
    todo: TodoRef | None = None
    calendar: CalendarRef | None = None
```

### 2.5 PushChainState (Laufzeit, pro Person und Tag)

```python
@dataclass
class PushChainState:
    person_entity: str
    date: date
    active: bool
    started: bool                        # initialer Start erfolgt?
    pending_catchup: bool                # wartet auf Heimkehr
    tasks_sent_count: int                # gegen Tageslimit
    current_task_id: str | None          # aktuell gepusht, wartet auf Aktion
    last_room: str | None                # für Raum-Bündelung der Folgeaufgabe
    sent_task_ids: list[str]             # Reservierungs-/Verlaufsbasis
    ended_reason: str | None             # snooze | left_home | no_tasks | limit | window_end
```

### 2.6 Reservation (Laufzeit)

```python
@dataclass
class Reservation:
    task_id: str
    person_entity: str
    reserved_at: datetime
    # high-Aufgaben am letzten relevanten Tag: parallele Reservierung erlaubt
    exclusive: bool = True
```

---

## 3. Persistenz

### 3.1 Zweigeteilte Persistenz

| Datenart | Speicher | Begründung |
|----------|----------|------------|
| TaskRules, TaskInstances (offen), PushChainState, Reservations, Sync-Status, Storage-Version | HA `Store` (Helper `homeassistant.helpers.storage.Store`), JSON | Standard für HA-Integrationen, migrationsfähig |
| Log-Events (Historie) | Eigene SQLite-DB `<config>/choreflow.db` | Jahresauswertbarkeit, performante Aggregation, unabhängig vom Recorder-Purge |

**Wichtig:** Das Log nutzt **nicht** den HA-Recorder. Eine eigene SQLite-Datei stellt sicher, dass Auswertungen über Jahre erhalten bleiben.

### 3.2 HA Store

- Ein Store pro Config Entry, Key `choreflow.<entry_id>`.
- Felder: `storage_version`, `task_rules`, `task_instances`, `push_chain_states`, `reservations`, `sync_state`, `calendar_state`.
- `storage_version: 1` zum Start. Migrationsfunktion `_migrate_func` vorbereiten, auch wenn noch leer.
- Schreibzugriffe gebündelt (debounced) über den Coordinator, nicht pro Einzeländerung.

### 3.3 SQLite-Log-Schema

```sql
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
    timestamp       TEXT NOT NULL,       -- ISO 8601 mit TZ
    source          TEXT,
    completion_source TEXT,
    overdue_days_at_completion INTEGER,
    decision_reason TEXT                 -- Nachvollziehbarkeit (§ NFA)
);
CREATE INDEX IF NOT EXISTS idx_log_type ON log_events(event_type);
CREATE INDEX IF NOT EXISTS idx_log_person ON log_events(person_entity);
CREATE INDEX IF NOT EXISTS idx_log_room ON log_events(room);
CREATE INDEX IF NOT EXISTS idx_log_ts ON log_events(timestamp);
```

- Alle SQLite-Zugriffe über `async_add_executor_job` (sqlite3 blockiert).
- Eine dünne `LogStore`-Klasse kapselt Schreib- und Auswertungs-Queries.

### 3.4 Auswertungs-Queries (Mindestumfang)

`LogStore` muss Methoden bereitstellen für: erledigte Aufgaben je Person / Raum / Kategorie / Task, aufgeschobene Aufgaben, häufig aufgeschobene Aufgaben (Top-N), Erledigungen je Monat/Jahr, rechtzeitig erledigte `high`-Aufgaben, überfällige bei Erledigung, Verteilung nach `completion_source`. Diese Methoden liefern Python-Strukturen, die Sensor-Attribute und der spätere Export nutzen.

---

## 4. Kernlogik (engine/)

### 4.1 Clock (`engine/clock.py`)

```python
class Clock(Protocol):
    def now(self) -> datetime: ...
    def today(self) -> date: ...

class SystemClock:  # Produktion: nutzt dt_util.now() (HA-aware)
    ...

class FixedClock:   # Tests: feste/steuerbare Zeit
    ...
```

Alle Engine-Module erhalten `Clock` per Konstruktor/Parameter. Zeitzone = HA-Zeitzone.

### 4.2 Recurrence (`engine/recurrence.py`)

- Reine Funktion: `due_instances_for(rules, on_date, existing_instances) -> list[TaskInstance]`.
- `every_n_days`: fällig, wenn `(on_date - anchor).days % interval == 0`; Anker = letzte Erledigung oder Regel-Erstelldatum.
- `weekdays`: fällig, wenn `on_date.weekday() in recurrence_weekdays`.
- `once`: nie automatisch erneut.
- Erzeugt keine Duplikate: prüft gegen vorhandene offene Instanz derselben Regel am selben Tag.
- Instanz-ID-Schema: `inst_<YYYY_MM_DD>_<rule_id>`.

### 4.3 Selector (`engine/selector.py`)

Implementiert §13 des Lastenhefts.

**Dringlichkeitspool** (`build_urgency_pool`): alle offenen, fälligen und überfälligen Instanzen. Score-Funktion berücksichtigt:

```text
score = w_importance * importance_weight
      + w_overdue    * overdue_days
      + w_due_today  * is_due_today
      - w_recent_push * times_recently_notified
```

Gewichte als Konstanten in `const.py`, dokumentiert und an einer Stelle änderbar. `high` muss strukturell vor `normal`/`low` liegen (z. B. dominanter Importance-Term), darf aber durch Raum-Bündelung **nicht dauerhaft verdrängt** werden (Lastenheft §13.4.5): Wenn eine `high`-Aufgabe für die Person im Pool ist und seit N Folgeaufgaben nicht gewählt wurde, wird sie erzwungen.

**Top-5-Pool** (`top_pool_for_person`): pro Person die fünf dringendsten *passenden* Aufgaben. Passend = sichtbar für Person ∧ (zufällig zuweisbar ∨ ihr zugewiesen) ∧ nicht durch andere exklusiv reserviert ∧ Person unter Tageslimit.

**Erste Aufgabe** (`pick_first`): sanfte Rotation aus Top-5 (z. B. gewichtete Zufallswahl, `high` bevorzugt). „Sanfte Rotation" = deterministischer, seed-barer Zufall für Testbarkeit (Seed injizierbar).

**Folgeaufgabe** (`pick_next`): nach §13.4 — Top-5 neu berechnen → wenn Aufgabe im `last_room` existiert, dringendste daraus → sonst sanfte Rotation → `high`-Erzwingung beachten.

### 4.4 Reservation (`engine/reservation.py`)

- `reserve(task_id, person)`: legt exklusive Reservierung an; verhindert Vergabe an andere.
- Ausnahme: zeitkritische `high`-Aufgabe am letzten relevanten Tag → `exclusive=False`, parallele Reservierung mehrerer anwesender Personen erlaubt.
- `release(task_id)`: bei Snooze/Erledigung/Tagesende.
- „letzter relevanter Tag" = `due_date` (bzw. `deadline`) == heute.

### 4.5 Scheduler (`engine/scheduler.py`)

Implementiert §12.

- `start_time_for(date)`: Mo–Fr 17:30, Sa/So 10:00 (aus Optionen, Defaults als Fallback).
- `is_within_window(now)`: zwischen Startzeit und 20:00.
- `should_start_chain(person, now, presence)`: initialer Start, falls Startzeit erreicht ∧ Person `home` ∧ Tag-Push für Person aktiviert (weekday/weekend-Flag) ∧ noch nicht gestartet.
- `should_catchup(person, now, presence)`: Person war zur Startzeit abwesend, kommt vor/bis 20:00 zurück → Kette nachholen.
- Nach 20:00: kein Start, keine Fortsetzung. Offene `pending_catchup` → Event `task_missed_no_presence` bzw. `task_expired`.

---

## 5. Home-Assistant-Anbindung

### 5.1 Entry-Lifecycle (`__init__.py`)

- `async_setup_entry`: Store laden, LogStore initialisieren, Coordinator erzeugen, Platforms (`sensor`, `binary_sensor`) forwarden, Services registrieren, Event-Listener (Notification-Actions, Presence, Calendar, Todo) anmelden, Zeit-Trigger (`async_track_time_change` / `async_track_point_in_time`) für Startzeiten und Tagesende registrieren.
- `async_unload_entry`: alle Listener/Timer sauber abmelden, DB-Verbindung schließen.
- `async_reload_entry` bei Options-Änderung.

### 5.2 Coordinator (`coordinator.py`)

- Hält Laufzeitzustand (Instanzen, ChainStates, Reservierungen).
- Reagiert auf: Zeit-Trigger, Presence-State-Changes (`async_track_state_change_event` auf `enabled_persons`), Notification-Action-Events, Todo-/Kalender-Änderungen, Service-Aufrufe.
- Stößt nach jeder relevanten Änderung Store-Persistenz (debounced) und Sensor-Update an.
- Zentrale Methode `async_advance_chain(person)`: prüft Fenster/Präsenz/Limit, wählt nächste Aufgabe (Selector), reserviert, sendet Push, aktualisiert ChainState.

### 5.3 Presence

- Maßgeblich ausschließlich `person.*`-State `== "home"` (Lastenheft §4.3). Keine anderen Zonen im MVP.
- State-Change-Listener: bei Heimkehr Nachhol-Logik prüfen; bei Verlassen laufende Kette pausieren (`active=False`, kein weiterer Push).

### 5.4 Notification-Actions (`notify.py`) — verbindlich: eigener Listener

ChoreFlow fängt die Rückkanal-Events **selbst** ab (keine Nutzer-Automation nötig).

- Push-Versand über den pro Person konfigurierten `notify_service` (`notify.mobile_app_*`).
- Jede Nachricht enthält `data.actions` mit eindeutigen Action-IDs, die Task- und Personen-Kontext kodieren, z. B.:
  - `CHOREFLOW_DONE__<task_id>__<person_slug>`
  - `CHOREFLOW_SNOOZE__<task_id>__<person_slug>`
  - `CHOREFLOW_OPEN_DASHBOARD`
- Event-Listener auf `mobile_app_notification_action`. Handler parst die Action-ID, ruft intern `complete_task` bzw. `snooze_task` und stößt `async_advance_chain` an.
- `tag` pro Aufgabe setzen, damit Folgemeldungen die vorherige ersetzen können.
- Robust gegen verlorene/doppelte Events: idempotente Verarbeitung anhand `task_id`-Status.

**Beispiel-Notify-Payload (konzeptuell):**

```python
service_data = {
    "title": "🧽 Bad: Waschbecken wischen",
    "message": "Heute fällig · ca. 5 Min",
    "data": {
        "tag": f"choreflow_{task_id}",
        "actions": [
            {"action": done_id, "title": "Erledigt"},
            {"action": snooze_id, "title": "Später erinnern"},
            {"action": "CHOREFLOW_OPEN_DASHBOARD", "title": "Dashboard öffnen",
             "uri": "/lovelace/choreflow"},
        ],
    },
}
```

### 5.5 Config Flow & Options Flow (`config_flow.py`)

**Config Flow (Ersteinrichtung), mehrstufig:**

1. Instanzname.
2. Personenauswahl (Multi-Select über vorhandene `person.*`).
3. Pro aktivierter Person: `notify_service` (Auswahl aus `notify.*`), `presence_required` (Default true), `weekday_push_enabled`, `weekend_push_enabled`.
4. Startzeiten (Default 17:30 / 10:00), Tagesende (Default 20:00), Tageslimit (Default 5).
5. Todo-Sync: aktiv ja/nein, Entität, Import-/Sync-Flags, Import-Defaults.
6. Kalender-Sync: aktiv ja/nein, Kalender-Entität(en), Match-Regeln, `due_offset_days`.

**Options Flow:** alle obigen Werte nachträglich änderbar (Lastenheft §21.2). Änderung triggert `async_reload_entry`.

Eingaben validieren (Entität existiert, Notify-Service existiert). Mehrsprachige `strings.json` + `translations/{en,de}.json`.

### 5.6 Sensoren (`sensor.py`, `binary_sensor.py`)

**Global:** `open_tasks`, `due_tasks`, `overdue_tasks`, `completed_today`, `completed_this_week`, `active_chains`.

**Pro aktivierter Person:** `<person>_open_tasks`, `<person>_due_tasks`, `<person>_completed_today`, `<person>_tasks_remaining_today`, `binary_sensor.<person>_has_due_tasks`, `binary_sensor.<person>_chain_active`.

- `unique_id` stabil je Entität; korrekte Device-Gruppierung (eine ChoreFlow-Device pro Entry, Personen ggf. als Sub-Devices).
- Attribute: `open_tasks` als Liste mit `title, room, category, importance, due_date` (Lastenheft §18.3). Listengröße begrenzen (z. B. max. 30) zur Vermeidung großer State-Attribute.
- Werte aus Coordinator, kein eigenständiges Polling.

### 5.7 Services (`services.py` + `services.yaml`)

Mindestumfang (Lastenheft §19): `create_task`, `update_task`, `delete_task`, `complete_task`, `snooze_task`, `start_daily_flow`, `send_next_task`, `rebuild_calendar_tasks`, `sync_todo`, `export_log`.

- Vollständige `services.yaml` mit Feldbeschreibungen, Selektoren und Übersetzungen.
- `complete_task(task_id, person_entity, source)`, `snooze_task(task_id, person_entity)`, `start_daily_flow(person_entity?)`, `sync_todo(entity_id?)` gemäß Lastenheft §19.1–19.4.
- Alle Services schreiben passende Log-Events und stoßen Sensor-Updates an.

### 5.8 Diagnostics & Repairs

- `diagnostics.py`: Entry-Konfiguration (Notify-Services anonymisiert), Zähler offener/fälliger Aufgaben, aktive Ketten, Sync-Status. **Keine** sensiblen Klartextdaten (Lastenheft §24.3).
- `repairs.py`: Issues bei fehlender Person, fehlendem Notify-Service, nicht verfügbarer Todo-/Kalender-Entität (Lastenheft §23).

---

## 6. To-do-Synchronisation (`sources/todo_sync.py`)

Implementiert §16. MVP 0.2.

- Zugriff auf die gemappte `todo.*`-Entität über die Todo-Plattform-API (Items lesen via Service/State, abhaken via `todo.update_item`).
- **Import:** neue offene Todo-Items → einmalige `TaskInstance` (`source=todo_sync`) mit Import-Defaults (`room`, `category`, `importance`, `assignment.mode` aus Optionen). Dedup über `TodoRef(entity_id, item_uid)`.
- **Sync To-do → ChoreFlow:** Todo-Item abgehakt → zugehörige Instanz `completed`, Event `task_completed_from_todo`.
- **Sync ChoreFlow → To-do:** synchronisierte Instanz erledigt → Todo-Item via `todo.update_item` auf `completed`.
- Erkennung von Änderungen über State-Change-Listener auf die Todo-Entität + periodischer Abgleich beim Sync-Service.
- Robust bei nicht verfügbarer Entität: Sync aussetzen, Fehler loggen, später fortsetzen (Lastenheft §23.3) — Integration läuft weiter.

---

## 7. Kalender (`sources/calendar_source.py`)

Implementiert §15. MVP 0.2.

- Liest ganztägige Ereignisse der konfigurierten `calendar.*`-Entität(en) (via `calendar.get_events`-Service über einen Vorschauzeitraum, z. B. 14 Tage).
- Match per `summary_contains`-Regeln (case-insensitive).
- Erzeugt `high`-Instanz mit `due_date = event_date + due_offset_days` (Default -1 → Vortag).
- **Dedup-Key:** `calendar_entity_id + calendar_event_uid + task_rule_id` (Lastenheft §23.5).
- **Änderungs-/Löschlogik (§15.4):** Event gelöscht → zugehörige *offene* Instanz entfernen (Event `calendar_task_removed`). Neues Event → neue Instanz (`calendar_task_created`). Geändertes Event → Instanz aktualisieren. Bereits erledigte Aufgaben bleiben im Log erhalten.
- Kalender nicht verfügbar: bestehende Aufgaben **nicht** vorschnell löschen, Fehler loggen, bei Verfügbarkeit neu syncen (Lastenheft §23.4).
- Periodischer Abgleich (z. B. 1×/Tag früh) + Service `rebuild_calendar_tasks`.

---

## 8. Logging (`logbook.py`)

- Schreibt alle Eventtypen aus Lastenheft §17.1 in `log_events`.
- Jedes Event mit `decision_reason` befüllen, wo eine automatische Entscheidung zugrunde liegt (Auswahl/Nicht-Auswahl/kein Push) — erfüllt §24.5 (Nachvollziehbarkeit).
- `event_id`-Schema: `evt_<YYYY_MM_DD>_<HHMMSS>_<kurzhash>` (kollisionssicher).
- `overdue_days_at_completion` bei Erledigung berechnen.
- `export_log`-Service: SQLite → JSON oder CSV in `<config>/choreflow_exports/`. Export ist nachrangig, muss aber funktionieren.

---

## 9. Fehlerfälle (verbindlich, Lastenheft §23)

| Fall | Verhalten |
|------|-----------|
| Person existiert nicht mehr | Keine Pushes; Warnung; Repair-Issue |
| Notify-Service fehlt | Kein Push; Fehler loggen; Repair-Issue |
| Todo-Entität nicht verfügbar | Lokal weiterlaufen; Sync aussetzen; Fehler loggen; späterer Sync möglich |
| Kalender nicht verfügbar | Aufgaben nicht vorschnell löschen; Fehler loggen; bei Verfügbarkeit neu syncen |
| Doppelte Aufgaben | Über externe Referenzen vermeiden (Todo/Kalender-Dedup-Keys) |

Übergreifend: Fehler in Sync/Push dürfen die Integration nie vollständig lahmlegen (§24.4). Defensive `try/except` um externe Aufrufe, mit Logging.

---

## 10. Nichtfunktionale Anforderungen (Umsetzung)

- **HA-Best-Practices:** Config/Options Flow, `services.yaml`, Übersetzungen (de/en), Diagnostics, Repairs, saubere Entity-Struktur, keine blockierende I/O, lokale Datenhaltung, migrationsfähiger Store (§24.1).
- **HACS:** Repo-Struktur gemäß Lastenheft §24.2, `hacs.json`, `manifest.json` (mit `config_flow: true`, `iot_class: calculated`/`local_push` passend, `version`, `documentation`, `issue_tracker`), `pyproject.toml`.
- **Datenschutz:** rein lokal, keine Cloud durch ChoreFlow, Diagnostics ohne sensible Klartextdaten (§24.3).
- **Stabilität & Nachvollziehbarkeit:** §24.4 / §24.5 wie oben.

---

## 11. Teststrategie (`tests/`)

Zweistufig. Verbindlich für MVP.

### 11.1 Reine Unit-Tests (ohne HA)

Decken die `engine`-Module ab — das fehleranfällige Herz:

- **recurrence:** `every_n_days`, `weekdays`, `once`; keine Duplikate; Ankerberechnung nach Erledigung.
- **selector:** Pool-Bildung; Scoring-Reihenfolge; `high`-Bevorzugung; Top-5-Begrenzung; Raum-Bündelung der Folgeaufgabe; `high`-Erzwingung gegen Verdrängung; deterministische Rotation (gesetzter Seed).
- **reservation:** Exklusivität; parallele Reservierung nur bei zeitkritischer `high` am letzten Tag; Release-Pfade.
- **scheduler:** Startzeiten Werktag/Wochenende; Fenster bis 20:00; Nachholen bei Heimkehr; kein Start/keine Fortsetzung nach 20:00 — alles über `FixedClock`.

### 11.2 HA-Integrationstests (`pytest-homeassistant-custom-component`)

- Config Flow & Options Flow: vollständiger Happy Path + Validierungsfehler.
- Setup/Unload des Entry; saubere Listener-/Timer-Abmeldung.
- Service-Registrierung und -Aufrufe (`complete_task`, `snooze_task`, `start_daily_flow`, `sync_todo`, ...).
- Sensor-/Binary-Sensor-State und Attribute.
- Notification-Action-Event → Erledigen/Snooze → Kette schreitet fort (gemockter Notify-Service, simuliertes `mobile_app_notification_action`-Event).
- Presence-State-Change → Pausieren/Nachholen.
- Repairs-Issues bei fehlender Person/Notify-Service.

### 11.3 Akzeptanzkriterien-Mapping

Jedes AK aus Lastenheft §26 muss mindestens einen Test haben. Mapping-Tabelle in `tests/README.md` pflegen (AK-01 … AK-19 → Testfunktion).

---

## 12. MVP-Phasen (Umsetzungsreihenfolge)

**MVP 0.1** (Lastenheft §25.1): Gerüst, Config/Options Flow, Personen, Push-Ziele, Aufgabenregeln im Store, einmalige Aufgaben, Wichtigkeiten, Räume/Kategorien, präsenzabhängige Push-Kette inkl. Startzeiten/Nachholen/Tagesende/Tageslimit, Logging, globale + personenbezogene Sensoren, Basis-Services.

**MVP 0.2** (Lastenheft §25.2): Todo-Mapping & Import, bidirektionaler Erledigt-Sync, kalenderbasierte `high`-Aufgaben mit Abfuhr-Logik und Dedup.

**Nach MVP:** Custom Card produktiv, Dashboard-Anlage, Historienansicht, Export-Komfort, erweiterte Filter, Fairness/Rotation.

---

## 13. Definition of Done (MVP)

Eine MVP-Stufe gilt als fertig, wenn:

1. Alle zugehörigen Akzeptanzkriterien (§26) durch automatisierte Tests abgedeckt und grün sind.
2. Integration sauber lädt/entlädt, keine blockierende I/O im Event Loop (Check via HA-Logwarnungen).
3. Config/Options Flow vollständig nutzbar, Eingaben validiert.
4. Logging schreibt alle relevanten Eventtypen inkl. `decision_reason`.
5. HACS-Struktur vollständig, `manifest.json`/`hacs.json` valide.
6. de/en-Übersetzungen vorhanden.
7. README mit Setup-Anleitung und Service-Dokumentation.
