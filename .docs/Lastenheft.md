# Lastenheft: ChoreFlow Home Assistant Integration

## 1. Allgemeine Informationen

**Projektname:** ChoreFlow
**Repository:** `ha-choreflow`
**Home-Assistant-Integration-Domain:** `choreflow`
**Anzeigename in Home Assistant:** `ChoreFlow`
**Art der Integration:** Home Assistant Custom Integration, installierbar über HACS
**Zielplattform:** Home Assistant
**Version des Lastenhefts:** 0.1
**Status:** Entwurf

---

## 2. Ziel des Projekts

ChoreFlow ist eine Home-Assistant-Integration zur Organisation kleinteiliger Haushaltsaufgaben.

Die Integration soll wiederkehrende und einmalige Aufgaben verwalten, fällige und überfällige Aufgaben priorisieren, anwesende Haushaltsmitglieder per Push-Nachricht erinnern und erledigte Aufgaben dauerhaft protokollieren.

Der Schwerpunkt liegt nicht auf Gamification oder Punktesystemen, sondern auf einer alltagstauglichen, präsenzabhängigen und möglichst unaufdringlichen Aufgabensteuerung.

ChoreFlow soll Aufgaben so bereitstellen, dass sie leicht erledigt werden können: kleinteilig, raumbezogen, sichtbarkeitsgesteuert und in sinnvollen Push-Ketten.

---

## 3. Abgrenzung

### 3.1 Enthalten

ChoreFlow soll folgende Kernfunktionen bereitstellen:

* Verwaltung wiederkehrender Haushaltsaufgaben
* Verwaltung einmaliger Aufgaben
* Import einmaliger Aufgaben aus Home-Assistant-`todo.*`-Entitäten, insbesondere Microsoft To Do über bestehende Home-Assistant-Integration
* optionale Synchronisation des Erledigt-Status zwischen ChoreFlow und `todo.*`
* kalenderbasierte Erzeugung von Aufgaben, insbesondere Müllabfuhrtermine
* präsenzabhängige Push-Benachrichtigungen
* Push-Ketten mit maximal fünf Aufgaben pro Person und Tag
* Priorisierung nach Wichtigkeit, Fälligkeit, Überfälligkeit, Raum und Benachrichtigungshistorie
* dauerhaftes Logging für spätere Auswertungen
* globale Sensoren und Sensoren pro aktivierter Person
* spätere Dashboard-/Lovelace-Custom-Card-Unterstützung

### 3.2 Nicht enthalten im initialen Zielbild

Nicht Bestandteil des initialen Funktionsumfangs sind:

* Punktesystem
* Badges
* Ranglisten
* direkte Microsoft-Graph-Anbindung
* komplexe Fairness- oder Rotationsalgorithmen
* automatische KI-basierte Aufgabenplanung
* vollständige Projektmanagement-Funktionalität
* Nutzung für alle Home-Assistant-Personen ohne explizite Aktivierung

---

## 4. Grundprinzipien

### 4.1 ChoreFlow ist führend

ChoreFlow besitzt ein eigenes kanonisches Datenmodell. Externe Quellen wie YAML, Dashboard, Kalender und `todo.*` können Aufgaben erzeugen oder synchronisieren, ersetzen aber nicht das interne Datenmodell.

Datenfluss:

```text
YAML / Dashboard / todo.* / Kalender
        ↓
ChoreFlow Task Model
        ↓
Push, Logging, Sensoren, Dashboard, Sync
```

### 4.2 Aufgaben sollen kleinteilig sein

Aufgaben sollen bewusst klein formuliert werden, damit sie schnell erledigt werden können.

Beispiele:

Nicht:

```text
Küche reinigen
```

Sondern:

```text
Arbeitsplatte abwischen
Spülmaschine ausräumen
Müll rausbringen
Herd abwischen
Biomüll leeren
```

### 4.3 Präsenzabhängigkeit

Push-Benachrichtigungen dürfen nur an Personen gesendet werden, die zuhause sind.

Als zuhause gilt ausschließlich:

```text
person_entity.state == "home"
```

Andere Zonen werden im MVP nicht berücksichtigt.

### 4.4 Keine Doppelbearbeitung

Wenn mehrere Personen zuhause sind, sollen sie unterschiedliche Aufgaben erhalten. Eine Aufgabe darf nicht parallel an mehrere Personen gesendet werden, außer bei zeitkritischen `high`-Aufgaben, bei denen eine parallele Benachrichtigung ausdrücklich vorgesehen ist.

### 4.5 Logging ist Pflichtbestandteil

Alle relevanten Aktionen müssen dauerhaft protokolliert werden. Das Logging muss Jahresauswertungen ermöglichen, zum Beispiel:

* Wer hat wie oft das Bad geputzt?
* Welche Aufgaben wurden häufig aufgeschoben?
* Welche Räume bleiben häufig liegen?
* Welche Aufgaben wurden über Microsoft To Do erledigt?
* Welche `high`-Aufgaben wurden rechtzeitig erledigt?

---

## 5. Nutzerrollen

### 5.1 Administrator

Der Administrator richtet ChoreFlow ein und verwaltet:

* aktivierte Personen
* Push-Ziele
* To-do-Mapping
* Kalenderquellen
* Aufgabenregeln
* globale Einstellungen
* Synchronisationsverhalten

### 5.2 Haushaltsmitglied

Ein Haushaltsmitglied kann:

* Push-Benachrichtigungen erhalten
* Aufgaben als erledigt markieren
* Aufgaben für später zurückstellen
* Aufgaben im Dashboard ansehen
* eigene oder allgemein sichtbare Aufgaben erledigen

### 5.3 Nicht aktivierte Home-Assistant-Person

Eine nicht aktivierte Person bleibt in Home Assistant vorhanden, nimmt aber nicht an ChoreFlow teil.

Sie erhält:

* keine ChoreFlow-Pushes
* keine automatische Aufgabenzuweisung
* keine Teilnahme an Push-Ketten
* keine Auswertung im ChoreFlow-Kontext

---

## 6. Teilnehmerkreis

ChoreFlow darf nicht automatisch alle in Home Assistant vorhandenen Personen verwenden.

In den Einstellungen der Integration muss festgelegt werden können, welche `person.*`-Entitäten teilnehmen.

Beispiel:

```yaml
enabled_persons:
  - person.niklas
  - person.person_b
```

Für jede aktivierte Person müssen mindestens folgende Einstellungen verwaltbar sein:

```yaml
person_settings:
  person.niklas:
    enabled: true
    notify_service: notify.mobile_app_niklas_iphone
    presence_required: true
    weekday_push_enabled: true
    weekend_push_enabled: true
```

---

## 7. Aufgabenmodell

### 7.1 Aufgabenregel

Eine Aufgabenregel beschreibt eine wiederkehrende Aufgabe.

Beispiel:

```yaml
id: clean_bathroom_sink
title: Waschbecken wischen
description: Waschbecken im Bad kurz auswischen
room: Bad
category: Putzen
importance: normal
estimated_duration_minutes: 5
recurrence:
  type: every_n_days
  interval: 3
```

### 7.2 Aufgabeninstanz

Eine Aufgabeninstanz ist eine konkrete Aufgabe, die offen, erledigt, gelöscht, synchronisiert oder protokolliert werden kann.

Instanzen können entstehen aus:

* Aufgabenregel
* Dashboard
* `todo.*`-Import
* Kalenderereignis
* manueller Service-Action

Beispiel:

```yaml
id: inst_2026_06_18_clean_bathroom_sink
rule_id: clean_bathroom_sink
title: Waschbecken wischen
room: Bad
category: Putzen
importance: normal
estimated_duration_minutes: 5
due_date: "2026-06-18"
status: open
source: rule
```

### 7.3 Einmalige Aufgaben

Einmalige Aufgaben sind Aufgabeninstanzen ohne Wiederholungsregel.

Sie können insbesondere entstehen durch:

* Dashboard-Erstellung
* Import aus `todo.*`
* manuelle Service-Action

Beispiel:

```yaml
id: task_kellerregal_ausmessen
title: Kellerregal ausmessen
room: Keller
category: Organisation
importance: normal
status: open
source: todo_sync
```

---

## 8. Aufgabenquellen

ChoreFlow soll Aufgaben aus mehreren Quellen erzeugen können.

### 8.1 YAML

YAML eignet sich für wiederkehrende, versionierbare Aufgabenregeln.

YAML-Aufgaben sollen im Dashboard sichtbar sein, aber zunächst nicht vom Dashboard in die YAML-Datei zurückgeschrieben werden.

Anforderung:

* YAML darf Aufgabenregeln erzeugen.
* YAML-Aufgaben sollen im internen ChoreFlow-Modell abgebildet werden.
* Dashboard darf YAML-Aufgaben anzeigen.
* Dashboard soll YAML-Aufgaben im MVP nicht direkt überschreiben.

### 8.2 Dashboard

Das Dashboard soll später Aufgaben anlegen, bearbeiten und erledigen können.

Da die Custom Card später ausgegliedert werden soll, muss die Integration bereits im Backend geeignete Services bereitstellen, zum Beispiel:

```yaml
choreflow.create_task
choreflow.update_task
choreflow.complete_task
choreflow.snooze_task
choreflow.delete_task
```

### 8.3 Home Assistant `todo.*`

ChoreFlow soll eine bestehende Home-Assistant-To-do-Liste als Sync-Quelle nutzen können.

Dies dient insbesondere dazu, Aufgaben aus Microsoft To Do zu übernehmen, ohne direkt Microsoft Graph anzubinden.

Konfigurationsbeispiel:

```yaml
todo_sync:
  enabled: true
  entity_id: todo.haushalt
  import_new_items: true
  sync_completion_from_todo: true
  sync_completion_to_todo: true
```

### 8.4 Kalender

Kalender dienen zur Erzeugung zeitgebundener `high`-Aufgaben, insbesondere Müllabfuhrtermine.

Beispiel:

```yaml
calendar_tasks:
  - id: take_out_residual_waste
    title: Restmülltonne rausstellen
    room: Außenbereich
    category: Müll
    importance: high
    calendar_entity_id: calendar.abfuhrtermine
    match:
      summary_contains:
        - Restmüll
        - Restabfall
    due_offset_days: -1
```

---

## 9. Wichtigkeiten

ChoreFlow verwendet drei Wichtigkeitsstufen:

| Wichtigkeit | Bedeutung                          | Beispiele                           |
| ----------- | ---------------------------------- | ----------------------------------- |
| `high`      | zeitkritisch, Frist, Pflichttermin | Mülltonne vor Abfuhr, Vertragsfrist |
| `normal`    | reguläre Haushaltsaufgabe          | Bad putzen, Küche wischen           |
| `low`       | optional oder weniger dringend     | Vorratsschrank sortieren            |

`mandatory_date` und `deadline` sind keine eigenen Wichtigkeiten, sondern Typen oder Gründe innerhalb von `high`.

Beispiel:

```yaml
importance: high
urgency_type: mandatory_date
```

Oder:

```yaml
importance: high
urgency_type: deadline
deadline: "2026-07-01"
```

---

## 10. Räume, Kategorien und Sichtbarkeit

### 10.1 Räume

Jede Aufgabe kann einem Raum zugeordnet werden.

Beispiele:

* Küche
* Bad
* Wohnzimmer
* Schlafzimmer
* Flur
* Keller
* Außenbereich
* Allgemein

### 10.2 Kategorien

Jede Aufgabe kann einer Kategorie zugeordnet werden.

Beispiele:

* Putzen
* Aufräumen
* Müll
* Wäsche
* Einkauf
* Wartung
* Pflanzen
* Haustiere
* Verwaltung
* Organisation

### 10.3 Sichtbarkeit

Aufgaben können sichtbarkeitsgesteuert sein.

Mögliche Sichtbarkeiten:

```yaml
visibility:
  mode: all_enabled_persons
```

oder:

```yaml
visibility:
  mode: selected_persons
  persons:
    - person.niklas
```

Eine Person darf eine Aufgabe nur sehen oder per Push erhalten, wenn sie für diese Aufgabe sichtbar ist.

---

## 11. Zuständigkeit

ChoreFlow unterstützt im MVP nur zwei Zuständigkeitsarten.

### 11.1 Nur bestimmte Person

Bestimmte Aufgaben können nur von einer festgelegten Person erledigt werden.

Beispiel:

```yaml
assignment:
  mode: assigned
  person: person.niklas
```

Verhalten:

* Push nur an diese Person
* nur wenn diese Person zuhause ist
* keine zufällige Verteilung an andere Personen

### 11.2 Zufällige Person

Alle anderen Aufgaben werden zufällig an eine geeignete aktivierte Person vergeben.

Beispiel:

```yaml
assignment:
  mode: random
```

Geeignet ist eine Person, wenn:

* sie in ChoreFlow aktiviert ist
* sie zuhause ist
* die Aufgabe für sie sichtbar ist
* sie das Tageslimit noch nicht erreicht hat
* die Aufgabe nicht bereits reserviert ist

---

## 12. Push-Logik

### 12.1 Startzeiten

ChoreFlow startet täglich eine Push-Kette.

| Tag                 | Initialer Start |
| ------------------- | --------------: |
| Montag bis Freitag  |           17:30 |
| Samstag und Sonntag |           10:00 |

Das Tagesfenster endet immer um:

```text
20:00
```

### 12.2 Nachholen bei Abwesenheit

Wenn eine Person zum initialen Zeitpunkt nicht zuhause ist, wird kein Push gesendet.

Stattdessen wartet ChoreFlow bis 20:00 Uhr auf Heimkehr.

Wenn die Person bis einschließlich 20:00 Uhr nach Hause kommt, wird die Push-Kette nachgeholt.

Wenn die Person nicht bis 20:00 Uhr nach Hause kommt, wird für diesen Tag keine Push-Kette gestartet und ein Logeintrag erzeugt.

### 12.3 Push nur zuhause

Vor jedem Push muss geprüft werden:

```text
person_entity.state == "home"
```

Ist die Person nicht zuhause, wird kein Push versendet.

Wenn eine Person während einer Push-Kette das Haus verlässt, darf kein weiterer Push gesendet werden. Kehrt die Person vor 20:00 Uhr zurück, kann die Kette fortgesetzt werden.

### 12.4 Maximale Anzahl Aufgaben

Pro Person und Tag dürfen maximal fünf Aufgaben per Push-Kette gesendet werden.

Konfiguration:

```yaml
max_tasks_per_person_per_day: 5
```

Nach Erreichen des Limits endet die Push-Kette für diese Person. Weitere Aufgaben bleiben im Dashboard sichtbar.

### 12.5 Push-Kette

ChoreFlow sendet immer genau eine Aufgabe pro Push.

Nach dem Erledigen einer Aufgabe wird automatisch die nächste Aufgabe ausgewählt und gepusht.

Dieser Ablauf wiederholt sich, bis eine der folgenden Bedingungen eintritt:

* die Person tippt auf „Später erinnern“
* die Person ist nicht mehr zuhause
* es gibt keine passende Aufgabe mehr
* das Tageslimit von fünf Aufgaben ist erreicht
* das Tagesfenster endet um 20:00 Uhr

### 12.6 Push-Aktionen

Jede Push-Nachricht muss mindestens folgende Aktionen enthalten:

* `Erledigt`
* `Später erinnern`
* `Dashboard öffnen`

Beispiel:

```text
🧽 Bad: Waschbecken wischen
Heute fällig · ca. 5 Min

[Erledigt] [Später erinnern] [Dashboard öffnen]
```

### 12.7 Bedeutung von „Später erinnern“

„Später erinnern“ verändert nicht das fachliche Fälligkeitsdatum.

Die Aufgabe bleibt:

* offen
* fällig oder überfällig
* im Dringlichkeitspool enthalten

Für `normal`- und `low`-Aufgaben beendet „Später erinnern“ die Push-Kette dieser Person für den Tag.

Für `high`-Aufgaben gilt eine Sonderregel: Sie dürfen bis zum relevanten Due Date erneut erinnert werden.

---

## 13. Auswahlalgorithmus

### 13.1 Dringlichkeitspool

ChoreFlow bildet aus allen offenen, fälligen und überfälligen Aufgaben einen Dringlichkeitspool.

Berücksichtigt werden:

* Wichtigkeit
* Fälligkeit
* Überfälligkeit
* Raum
* Kategorie
* Sichtbarkeit
* Zuständigkeit
* Benachrichtigungshistorie
* vorherige Pushes an Personen
* Reservierungen
* Tageslimit

### 13.2 Top-5-Pool

Für jede Person wird ein Pool der fünf dringendsten passenden Aufgaben gebildet.

Aus diesem Pool wird die nächste Aufgabe ausgewählt.

### 13.3 Erste Aufgabe

Die erste Aufgabe einer Push-Kette wird sanft rotierend aus den fünf dringendsten Aufgaben gewählt.

`high`-Aufgaben werden bevorzugt.

### 13.4 Folgeaufgaben

Nach Erledigung einer Aufgabe wird die nächste Aufgabe wie folgt ausgewählt:

1. Top-5-Pool neu berechnen.
2. Prüfen, ob eine Aufgabe im selben Raum wie die erledigte Aufgabe vorhanden ist.
3. Falls ja: dringendste Aufgabe aus demselben Raum wählen.
4. Falls nein: sanft rotierend aus dem Top-5-Pool wählen.
5. `high`-Aufgaben dürfen durch Raum-Bündelung nicht dauerhaft verdrängt werden.

### 13.5 Reservierung

Sobald eine Aufgabe per Push an eine Person gesendet wurde, wird sie für diese Person reserviert.

Reservierte Aufgaben dürfen nicht gleichzeitig an andere Personen gesendet werden.

Ausnahme:

* zeitkritische `high`-Aufgaben dürfen am letzten relevanten Tag an mehrere zuhause anwesende Personen gesendet werden.

---

## 14. Verhalten bei mehreren Personen zuhause

Wenn mehrere aktivierte Personen zuhause sind, sollen sie unterschiedliche Aufgaben erhalten.

Beispiel:

```text
Niklas zuhause
Person B zuhause

ChoreFlow:
- Aufgabe A an Niklas
- Aufgabe B an Person B
```

Die Pushes müssen nicht exakt gleichzeitig versendet werden. Durch Reservierungen wird verhindert, dass dieselbe Aufgabe doppelt erledigt wird.

Bei `high`-Aufgaben kann eine parallele Benachrichtigung an mehrere Personen erlaubt sein, wenn die Aufgabe zeitkritisch ist.

---

## 15. High-Aufgaben

### 15.1 Definition

Eine `high`-Aufgabe ist eine Aufgabe, die zeitkritisch ist oder zwingend zu einem bestimmten Zeitpunkt erledigt werden muss.

Beispiele:

* Mülltonne rausstellen, wenn am Folgetag Abfuhrtermin ist
* Vertragsfrist
* Terminbezogene Vorbereitung
* wichtige Wartungsaufgabe

### 15.2 Verhalten

`high`-Aufgaben werden bevorzugt in den Dringlichkeitspool aufgenommen.

Sie dürfen wiederholt erinnert werden:

* bis zum Due Date
* bei Rückkehr nach Hause innerhalb des Tagesfensters
* ggf. an alle zuhause anwesenden aktivierten Personen, wenn die Aufgabe zeitkritisch ist

### 15.3 Müllabfuhr

Abfuhrtermine werden aus einem Home-Assistant-Kalender gelesen.

Annahmen:

* Abfuhrtermine sind ganztägige Kalenderereignisse.
* Die Aufgabe ist am Vortag zu erledigen.

Beispiel:

```text
Kalenderereignis:
Restmüll, ganztägig am 19.06.2026

ChoreFlow-Aufgabe:
Restmülltonne rausstellen
Fällig am 18.06.2026
Wichtigkeit: high
```

### 15.4 Kalenderänderungen

Wenn ein Kalenderereignis gelöscht wird, wird die zugehörige offene ChoreFlow-Aufgabe entfernt.

Wenn ein neues passendes Kalenderereignis erstellt wird, wird eine neue ChoreFlow-Aufgabe erzeugt.

Wenn ein Kalenderereignis geändert wird, wird die zugehörige ChoreFlow-Aufgabe aktualisiert.

Bereits erledigte Aufgaben werden nicht aus der Historie gelöscht. Das Logging bleibt erhalten.

Deduplizierung erfolgt über eine stabile externe Referenz:

```text
calendar_entity_id + calendar_event_uid + task_rule_id
```

---

## 16. To-do-Synchronisation

### 16.1 Grundsatz

ChoreFlow ist führend.

Home-Assistant-`todo.*`-Entitäten dienen als externe Quelle und Synchronisationsziel.

Eine direkte Microsoft-Graph-Anbindung ist nicht vorgesehen. Microsoft To Do wird über eine bereits vorhandene Home-Assistant-To-do-Integration angebunden.

### 16.2 Mapping

In den Einstellungen muss eine To-do-Entität ausgewählt werden können.

Beispiel:

```yaml
todo_sync:
  enabled: true
  entity_id: todo.haushalt
```

### 16.3 Import

Neue offene Einträge aus der gemappten To-do-Liste sollen als einmalige ChoreFlow-Aufgaben importiert werden können.

Da To-do-Items weniger Metadaten besitzen als ChoreFlow-Aufgaben, müssen Standardwerte verwendet werden können:

```yaml
todo_import_defaults:
  room: Allgemein
  category: Allgemein
  importance: normal
  assignment:
    mode: random
```

### 16.4 Erledigt-Sync von To-do zu ChoreFlow

Wenn eine Aufgabe in der To-do-Liste abgehakt wird, muss die entsprechende ChoreFlow-Aufgabe als erledigt markiert werden.

Dabei wird ein Logeintrag erzeugt:

```text
task_completed_from_todo
```

### 16.5 Erledigt-Sync von ChoreFlow zu To-do

Wenn eine synchronisierte ChoreFlow-Aufgabe erledigt wird, soll der entsprechende To-do-Eintrag ebenfalls als erledigt markiert werden.

### 16.6 Externe Referenz

Jede synchronisierte Aufgabe muss eine externe Referenz speichern.

Beispiel:

```yaml
external_refs:
  todo:
    entity_id: todo.haushalt
    item_uid: abc123
```

---

## 17. Logging und Auswertbarkeit

### 17.1 Pflicht-Logging

ChoreFlow muss relevante Ereignisse dauerhaft protokollieren.

Mindestens folgende Eventtypen sind erforderlich:

| Eventtyp                   | Bedeutung                               |
| -------------------------- | --------------------------------------- |
| `task_created`             | Aufgabe wurde erzeugt                   |
| `task_updated`             | Aufgabe wurde geändert                  |
| `task_deleted`             | Aufgabe wurde gelöscht                  |
| `task_notified`            | Push wurde gesendet                     |
| `task_completed`           | Aufgabe wurde erledigt                  |
| `task_snoozed`             | Aufgabe wurde zurückgestellt            |
| `task_missed_no_presence`  | Person war nicht zuhause                |
| `task_expired`             | Tagesfenster ist abgelaufen             |
| `task_synced_from_todo`    | Aufgabe wurde aus To-do importiert      |
| `task_completed_from_todo` | Aufgabe wurde über To-do erledigt       |
| `calendar_task_created`    | Kalenderbasierte Aufgabe wurde erzeugt  |
| `calendar_task_removed`    | Kalenderbasierte Aufgabe wurde entfernt |

### 17.2 Logdaten

Ein Logeintrag muss mindestens folgende Felder unterstützen:

```yaml
event_id: evt_2026_06_18_174200
event_type: task_completed
task_id: inst_2026_06_18_clean_bathroom_sink
task_rule_id: clean_bathroom_sink
title: Waschbecken wischen
room: Bad
category: Putzen
importance: normal
person_entity: person.niklas
timestamp: "2026-06-18T17:42:00+02:00"
source: push_action
completion_source: push
overdue_days_at_completion: 0
```

### 17.3 Auswertungen

Das Logging muss spätere Auswertungen ermöglichen, insbesondere:

* Anzahl erledigter Aufgaben pro Person
* Anzahl erledigter Aufgaben pro Raum
* Anzahl erledigter Aufgaben pro Kategorie
* Anzahl erledigter Aufgaben pro Aufgabe
* Anzahl aufgeschobener Aufgaben
* häufig aufgeschobene Aufgaben
* erledigte Aufgaben pro Monat/Jahr
* rechtzeitig erledigte `high`-Aufgaben
* überfällige Aufgaben bei Erledigung
* Erledigungsquelle: Push, Dashboard, To-do

### 17.4 Export

ChoreFlow soll perspektivisch einen Export als JSON oder CSV ermöglichen.

Mögliche Services:

```yaml
choreflow.export_log
choreflow.export_tasks
```

---

## 18. Home-Assistant-Entitäten

### 18.1 Globale Sensoren

ChoreFlow soll globale Sensoren erzeugen.

Beispiele:

```text
sensor.choreflow_open_tasks
sensor.choreflow_due_tasks
sensor.choreflow_overdue_tasks
sensor.choreflow_completed_today
sensor.choreflow_completed_this_week
sensor.choreflow_active_chains
```

### 18.2 Sensoren pro Person

Für jede aktivierte Person sollen eigene Sensoren erzeugt werden.

Beispiele:

```text
sensor.choreflow_niklas_open_tasks
sensor.choreflow_niklas_due_tasks
sensor.choreflow_niklas_completed_today
sensor.choreflow_niklas_tasks_remaining_today
binary_sensor.choreflow_niklas_has_due_tasks
binary_sensor.choreflow_niklas_chain_active
```

### 18.3 Sensor-Attribute

Sensoren sollen nützliche Attribute enthalten, zum Beispiel:

```yaml
open_tasks:
  - task_id: inst_2026_06_18_clean_bathroom_sink
    title: Waschbecken wischen
    room: Bad
    category: Putzen
    importance: normal
    estimated_duration_minutes: 5
    due_date: "2026-06-18"
```

Das Attribut des globalen Open-Tasks-Sensors ist eine nach Dringlichkeit
sortierte Vorschau mit maximal 30 Einträgen. Zusätzlich enthält der Sensor:

```yaml
api_version: 1
total: 42
truncated: true
```

Vollständige und gefilterte Listen werden paginiert über
`choreflow.get_tasks` abgefragt.

Der personenspezifische `chain_active`-Binary-Sensor enthält mindestens:

```yaml
api_version: 1
person_entity: person.niklas
date: "2026-06-18"
started: true
active: true
pending_catchup: false
current_task_id: inst_2026_06_18_clean_bathroom_sink
current_task_title: Waschbecken wischen
tasks_sent_today: 3
tasks_completed_today: 2
daily_limit: 5
remaining_today: 2
ended_reason: null
```

---

## 19. Services / Actions

ChoreFlow soll eigene Home-Assistant-Actions bereitstellen.

Mindestumfang:

```yaml
choreflow.create_task
choreflow.update_task
choreflow.delete_task
choreflow.complete_task
choreflow.snooze_task
choreflow.start_daily_flow
choreflow.send_next_task
choreflow.rebuild_calendar_tasks
choreflow.sync_todo
choreflow.export_log
choreflow.get_tasks
choreflow.get_history
```

### 19.1 `complete_task`

Markiert eine Aufgabe als erledigt.

Parameter:

```yaml
task_id: string
person_entity: string
source: string
```

### 19.2 `snooze_task`

Stellt die Benachrichtigung zurück, ohne das Fälligkeitsdatum zu ändern.

Parameter:

```yaml
task_id: string
person_entity: string
```

### 19.3 `start_daily_flow`

Startet die tägliche Push-Kette manuell.

Parameter:

```yaml
person_entity: optional string
```

### 19.4 `sync_todo`

Löst einen manuellen To-do-Sync aus.

Parameter:

```yaml
entity_id: optional string
```

### 19.5 `get_tasks`

Read-only-Abfrage für vollständige, gefilterte und paginierte Aufgabenlisten.
Filter: Status, Person (`visible` oder `assigned`), Raum und Kategorie.
`limit` ist auf maximal 100 begrenzt.

```yaml
request:
  status: open
  person_entity: person.niklas
  person_scope: visible
  limit: 50
  offset: 0
response:
  api_version: 1
  items: []
  total: 0
  limit: 50
  offset: 0
  has_more: false
```

### 19.6 `get_history`

Read-only-Abfrage für gefilterte und paginierte Logereignisse. Ohne
`event_types` werden Erledigungen aus ChoreFlow und To-do geliefert. Die
Antwort verwendet denselben versionierten Pagination-Envelope wie
`get_tasks`.

---

## 20. Dashboard und Custom Card

ChoreFlow soll später durch eine Lovelace Custom Card ergänzt werden.

Die Custom Card kann später in ein separates Repository ausgelagert werden:

```text
ha-choreflow-card
```

Das Lastenheft der Integration muss dennoch sicherstellen, dass das Backend alle notwendigen Daten und Services bereitstellt.

Die spätere Card soll mindestens ermöglichen:

* offene Aufgaben anzeigen
* fällige Aufgaben anzeigen
* überfällige Aufgaben anzeigen
* Aufgaben nach Person filtern
* Aufgaben nach Raum filtern
* Aufgaben nach Kategorie filtern
* Aufgabe als erledigt markieren
* Aufgabe zurückstellen
* neue einmalige Aufgabe erstellen
* Aufgabenhistorie anzeigen
* Status der heutigen Push-Kette anzeigen

Die erste Version von `ha-choreflow` muss noch keine vollständige Custom Card enthalten, aber die Architektur muss darauf vorbereitet sein.

---

## 21. Konfiguration

### 21.1 Config Flow

Die Integration soll über die Home-Assistant-UI eingerichtet werden.

Beim ersten Setup sollen mindestens folgende Angaben möglich sein:

* Name der Instanz
* aktivierte Personen
* Push-Ziele je Person
* Standardzeiten für Pushes
* To-do-Sync aktiv/inaktiv
* To-do-Entität
* Kalender-Sync aktiv/inaktiv
* Kalender-Entität für Abfuhrtermine

### 21.2 Options Flow

Nach der Einrichtung sollen Einstellungen über einen Options Flow änderbar sein.

Änderbar sein sollen insbesondere:

* aktivierte Personen
* Notify-Service pro Person
* Tageslimit
* Push-Zeit unter der Woche
* Push-Zeit am Wochenende
* Tagesende
* To-do-Mapping
* Kalenderquellen
* Standardwerte für importierte To-do-Aufgaben

### 21.3 Beispielkonfiguration

```yaml
choreflow:
  weekday_start_time: "17:30"
  weekend_start_time: "10:00"
  day_end_time: "20:00"
  max_tasks_per_person_per_day: 5

  persons:
    - person_entity: person.niklas
      notify_service: notify.mobile_app_niklas_iphone
      enabled: true

  todo_sync:
    enabled: true
    entity_id: todo.haushalt
    import_new_items: true
    sync_completion_from_todo: true
    sync_completion_to_todo: true

  calendar_sources:
    - entity_id: calendar.abfuhrtermine
      enabled: true
```

---

## 22. Datenhaltung

ChoreFlow benötigt eigene persistente Datenhaltung für:

* Aufgabenregeln
* Aufgabeninstanzen
* externe Referenzen
* Push-Kettenstatus
* Reservierungen
* Logging
* Synchronisationsstatus
* Kalenderreferenzen

Die Datenhaltung soll lokal in Home Assistant erfolgen.

Persistente Daten müssen update- und migrationsfähig sein.

Datenstrukturversionen müssen unterstützt werden, zum Beispiel:

```yaml
storage_version: 1
```

---

## 23. Fehlerfälle

ChoreFlow muss mit folgenden Fehlerfällen umgehen können:

### 23.1 Person existiert nicht mehr

Wenn eine konfigurierte `person.*`-Entität nicht mehr existiert:

* keine Pushes an diese Person senden
* Warnung erzeugen
* Repair-Hinweis bereitstellen

### 23.2 Notify-Service existiert nicht mehr

Wenn ein konfigurierter Notify-Service nicht mehr existiert:

* Push nicht senden
* Fehler loggen
* Repair-Hinweis bereitstellen

### 23.3 To-do-Entität nicht verfügbar

Wenn die gemappte To-do-Entität nicht verfügbar ist:

* ChoreFlow läuft lokal weiter
* Sync wird ausgesetzt
* Fehler wird protokolliert
* späterer Sync soll möglich bleiben

### 23.4 Kalender nicht verfügbar

Wenn ein Kalender nicht verfügbar ist:

* bestehende Aufgaben nicht vorschnell löschen
* Fehler protokollieren
* bei erneuter Verfügbarkeit neu synchronisieren

### 23.5 Doppelte Aufgaben

Doppelte Aufgaben sollen über externe Referenzen vermieden werden.

Für To-do:

```text
todo_entity_id + todo_item_uid
```

Für Kalender:

```text
calendar_entity_id + calendar_event_uid + task_rule_id
```

---

## 24. Nichtfunktionale Anforderungen

### 24.1 Home-Assistant-Konformität

ChoreFlow soll nach Home-Assistant-Best-Practices entwickelt werden:

* Config Flow
* Options Flow
* Services mit `services.yaml`
* Übersetzungen
* Diagnostics
* Repair-Hinweise
* saubere Entity-Struktur
* keine blockierenden I/O-Operationen im Event Loop
* lokale Datenhaltung
* migrationsfähige Storage-Struktur

### 24.2 HACS-Kompatibilität

Das Repository soll HACS-kompatibel aufgebaut sein.

Zielstruktur:

```text
ha-choreflow/
├─ custom_components/
│  └─ choreflow/
│     ├─ __init__.py
│     ├─ manifest.json
│     ├─ const.py
│     ├─ config_flow.py
│     ├─ coordinator.py
│     ├─ sensor.py
│     ├─ binary_sensor.py
│     ├─ services.yaml
│     ├─ diagnostics.py
│     ├─ repairs.py
│     └─ translations/
├─ README.md
├─ hacs.json
├─ LICENSE
└─ pyproject.toml
```

### 24.3 Datenschutz

ChoreFlow verarbeitet haushaltsbezogene Aufgaben, Anwesenheitsstatus und Erledigungshistorie.

Daher gilt:

* Daten werden lokal gespeichert.
* Keine Cloud-Anbindung durch ChoreFlow selbst.
* Microsoft To Do wird nur über bestehende Home-Assistant-`todo.*`-Entitäten genutzt.
* Diagnoseexporte dürfen keine sensiblen Daten unnötig offenlegen.

### 24.4 Stabilität

ChoreFlow darf Home Assistant nicht blockieren.

Fehler in To-do-Sync, Kalender-Sync oder Push-Versand dürfen die Integration nicht vollständig lahmlegen.

### 24.5 Nachvollziehbarkeit

Alle automatischen Entscheidungen müssen nachvollziehbar sein.

Insbesondere soll protokolliert werden:

* warum eine Aufgabe ausgewählt wurde
* an wen sie gesendet wurde
* warum kein Push gesendet wurde
* warum eine Aufgabe nicht berücksichtigt wurde

---

## 25. MVP-Zuschnitt

### 25.1 MVP 0.1

MVP 0.1 umfasst:

* HACS-kompatible Integration
* Config Flow
* Options Flow
* aktivierte Personen
* Push-Ziele je Person
* lokale Aufgabenregeln
* einmalige Aufgaben im internen Store
* Wichtigkeiten `high`, `normal`, `low`
* Räume und Kategorien
* präsenzabhängige Push-Kette
* Startzeiten 17:30 unter der Woche und 10:00 am Wochenende
* Nachholen bis 20:00 bei Heimkehr
* maximal fünf Aufgaben pro Person und Tag
* Logging
* globale Sensoren
* Sensoren pro Person
* Basis-Services

### 25.2 MVP 0.2

MVP 0.2 umfasst:

* To-do-Mapping
* Import einmaliger Aufgaben aus `todo.*`
* Erledigt-Sync von To-do nach ChoreFlow
* Erledigt-Sync von ChoreFlow nach To-do
* kalenderbasierte `high`-Aufgaben
* Abfuhrtermin-Logik für ganztägige Kalenderereignisse
* Deduplizierung über externe Referenzen

### 25.3 Nach MVP

Nach dem MVP sollen folgen:

* Lovelace Custom Card
* Aufgabenanlage über Dashboard
* komfortable Historienansicht
* CSV-/JSON-Export
* erweiterte Filter
* bessere Bearbeitung von Aufgabenregeln
* optionale Fairness-/Rotationslogik
* erweiterte Auswertungen

---

## 26. Akzeptanzkriterien

### AK-01 Einrichtung

ChoreFlow kann über die Home-Assistant-UI eingerichtet werden.

### AK-02 Teilnehmer

Es können gezielt Home-Assistant-Personen aktiviert werden. Nicht aktivierte Personen erhalten keine Pushes.

### AK-03 Präsenz

Eine Person erhält nur dann einen Push, wenn ihre `person.*`-Entität den Zustand `home` hat.

### AK-04 Push-Zeit unter der Woche

Montag bis Freitag wird die Push-Kette um 17:30 gestartet, sofern die Person zuhause ist.

### AK-05 Push-Zeit Wochenende

Samstag und Sonntag wird die Push-Kette um 10:00 gestartet, sofern die Person zuhause ist.

### AK-06 Nachholen

Ist eine Person zum Startzeitpunkt nicht zuhause, wird die Push-Kette nachgeholt, wenn sie bis 20:00 nach Hause kommt.

### AK-07 Tagesende

Nach 20:00 wird keine neue Push-Kette gestartet oder fortgesetzt.

### AK-08 Push-Kette

Nach Erledigung einer gepushten Aufgabe wird automatisch die nächste Aufgabe gepusht.

### AK-09 Aufschieben

„Später erinnern“ verändert nicht das Fälligkeitsdatum und beendet für `normal`- und `low`-Aufgaben die heutige Push-Kette der Person.

### AK-10 Tageslimit

Pro Person werden maximal fünf Aufgaben pro Tag per Push-Kette gesendet.

### AK-11 Unterschiedliche Aufgaben

Wenn mehrere Personen zuhause sind, erhalten sie unterschiedliche Aufgaben, sofern ausreichend passende Aufgaben vorhanden sind.

### AK-12 High-Aufgaben

`high`-Aufgaben werden bevorzugt behandelt und können bis zum Due Date erneut erinnert werden.

### AK-13 Kalender

Ein ganztägiger Abfuhrtermin am Folgetag erzeugt am Vortag eine `high`-Aufgabe.

### AK-14 Kalenderlöschung

Wird ein Kalenderereignis gelöscht, wird die zugehörige offene ChoreFlow-Aufgabe entfernt.

### AK-15 To-do-Import

Ein neuer offener Eintrag in der gemappten To-do-Liste kann als einmalige ChoreFlow-Aufgabe importiert werden.

### AK-16 To-do-Erledigung

Wird ein synchronisierter To-do-Eintrag abgehakt, wird die entsprechende ChoreFlow-Aufgabe als erledigt markiert.

### AK-17 Logging

Jede Erledigung wird mit Person, Zeit, Raum, Kategorie, Aufgabe, Quelle und Überfälligkeit protokolliert.

### AK-18 Sensoren

Globale Sensoren und Sensoren pro aktivierter Person werden in Home Assistant bereitgestellt.

### AK-19 Dashboard-Vorbereitung

Die Integration stellt Services und Daten bereit, die eine spätere Lovelace Custom Card nutzen kann.

---

## 27. Offene spätere Erweiterungen

Folgende Punkte sind bewusst nicht Bestandteil des initialen Lastenhefts, können aber später ergänzt werden:

* komplexe Aufgabenrotation
* faire Aufgabenverteilung nach historischer Last
* Raumverantwortliche
* Kategorieverantwortliche
* Eskalationen über mehrere Personen
* Ruhezeiten pro Person
* Urlaubsmodus
* Mehrhaushalt-Unterstützung
* mehrere To-do-Listen
* direkte Microsoft-Graph-Anbindung
* Statistiken als eigene Dashboard-Ansichten
* Exportberichte pro Monat oder Jahr

---

## 28. Zusammenfassung

ChoreFlow soll eine lokale, Home-Assistant-native Aufgabenintegration für Haushalte werden.

Die Integration verwaltet wiederkehrende und einmalige Aufgaben, priorisiert sie nach Wichtigkeit und Fälligkeit, berücksichtigt Anwesenheit, sendet präsenzabhängige Push-Ketten und protokolliert alle relevanten Ereignisse dauerhaft.

ChoreFlow ist die führende Datenquelle. YAML, Dashboard, Kalender und `todo.*` dienen als Eingabe- oder Synchronisationsquellen.

Das System soll bewusst ohne Punktesystem oder Ranglisten auskommen. Motivation entsteht durch kleinteilige Aufgaben, sinnvolle Raum-Bündelung, reduzierte Reibung und nachvollziehbare Erledigungshistorie.
