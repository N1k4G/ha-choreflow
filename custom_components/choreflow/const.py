"""Constants for the ChoreFlow integration.

This module is the single source of truth for the domain name, configuration
keys, defaults, log event types and the selector scoring weights. Tuning the
selection behaviour should only ever require edits here (Pflichtenheft §4.3).

Kept free of any ``homeassistant`` import so the HA-free engine (Leitplanke 3)
can import it. HA-typed constants such as the platform list live in
``__init__.py``.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Core identity
# ---------------------------------------------------------------------------
DOMAIN: Final = "choreflow"
DEFAULT_NAME: Final = "ChoreFlow"

# ---------------------------------------------------------------------------
# Persistence (§3)
# ---------------------------------------------------------------------------
STORAGE_VERSION: Final = 1
# One Store per config entry: choreflow.<entry_id>
STORAGE_KEY_TEMPLATE: Final = DOMAIN + ".{entry_id}"
# Debounce window (seconds) for bundled Store writes via the coordinator (§3.2).
STORE_SAVE_DEBOUNCE_SECONDS: Final = 2.0

# Own SQLite log database, independent of the HA recorder (§3.1/§3.3).
DB_FILENAME: Final = "choreflow.db"
EXPORT_DIRNAME: Final = "choreflow_exports"

# ---------------------------------------------------------------------------
# Config / Options keys (§5.5, Lastenheft §21)
# ---------------------------------------------------------------------------
CONF_NAME: Final = "name"

# Persons
CONF_ENABLED_PERSONS: Final = "enabled_persons"
CONF_PERSON_SETTINGS: Final = "person_settings"
CONF_NOTIFY_SERVICE: Final = "notify_service"
CONF_PRESENCE_REQUIRED: Final = "presence_required"
CONF_WEEKDAY_PUSH_ENABLED: Final = "weekday_push_enabled"
CONF_WEEKEND_PUSH_ENABLED: Final = "weekend_push_enabled"
CONF_PERSON_ENABLED: Final = "enabled"

# Schedule / window (§4.5, Lastenheft §12)
CONF_WEEKDAY_START_TIME: Final = "weekday_start_time"
CONF_WEEKEND_START_TIME: Final = "weekend_start_time"
CONF_DAY_END_TIME: Final = "day_end_time"
CONF_MAX_TASKS_PER_PERSON_PER_DAY: Final = "max_tasks_per_person_per_day"

# To-do sync (§6, Lastenheft §16)
CONF_TODO_SYNC: Final = "todo_sync"
CONF_TODO_ENABLED: Final = "enabled"
CONF_TODO_ENTITY_ID: Final = "entity_id"
CONF_TODO_IMPORT_NEW_ITEMS: Final = "import_new_items"
CONF_TODO_SYNC_FROM_TODO: Final = "sync_completion_from_todo"
CONF_TODO_SYNC_TO_TODO: Final = "sync_completion_to_todo"
CONF_TODO_IMPORT_DEFAULTS: Final = "import_defaults"
CONF_IMPORT_ROOM: Final = "room"
CONF_IMPORT_CATEGORY: Final = "category"
CONF_IMPORT_IMPORTANCE: Final = "importance"
CONF_IMPORT_ASSIGNMENT_MODE: Final = "assignment_mode"

# Calendar sync (§7, Lastenheft §15)
CONF_CALENDAR_SOURCES: Final = "calendar_sources"
CONF_CALENDAR_ENABLED: Final = "enabled"
CONF_CALENDAR_ENTITY_ID: Final = "entity_id"
CONF_CALENDAR_MATCH_SUMMARY_CONTAINS: Final = "summary_contains"
CONF_CALENDAR_DUE_OFFSET_DAYS: Final = "due_offset_days"

# ---------------------------------------------------------------------------
# Defaults (Lastenheft §12, §16.3, §21.3)
# ---------------------------------------------------------------------------
DEFAULT_WEEKDAY_START_TIME: Final = "17:30"
DEFAULT_WEEKEND_START_TIME: Final = "10:00"
DEFAULT_DAY_END_TIME: Final = "20:00"
DEFAULT_MAX_TASKS_PER_PERSON_PER_DAY: Final = 5

DEFAULT_PRESENCE_REQUIRED: Final = True
DEFAULT_WEEKDAY_PUSH_ENABLED: Final = True
DEFAULT_WEEKEND_PUSH_ENABLED: Final = True

DEFAULT_IMPORT_ROOM: Final = "Allgemein"
DEFAULT_IMPORT_CATEGORY: Final = "Allgemein"
DEFAULT_IMPORT_IMPORTANCE: Final = "normal"
DEFAULT_IMPORT_ASSIGNMENT_MODE: Final = "random"

# Calendar all-day waste events: task is due the day before (§7, Lastenheft §15.3).
DEFAULT_CALENDAR_DUE_OFFSET_DAYS: Final = -1
# Look-ahead window when reading calendar events (§7).
DEFAULT_CALENDAR_PREVIEW_DAYS: Final = 14

# Cap list-valued sensor attributes to keep HA state small (§5.6, Lastenheft §18.3).
MAX_SENSOR_ATTR_TASKS: Final = 30

# ---------------------------------------------------------------------------
# Notification actions (§5.4)
# ---------------------------------------------------------------------------
# Action IDs encode task and person context: <PREFIX><SEP><task_id><SEP><person_slug>
ACTION_SEPARATOR: Final = "__"
ACTION_PREFIX_DONE: Final = "CHOREFLOW_DONE"
ACTION_PREFIX_SNOOZE: Final = "CHOREFLOW_SNOOZE"
ACTION_OPEN_DASHBOARD: Final = "CHOREFLOW_OPEN_DASHBOARD"
DASHBOARD_URI: Final = "/lovelace/choreflow"

# HA event fired by the companion app when a notification action is tapped (§5.4).
EVENT_MOBILE_APP_NOTIFICATION_ACTION: Final = "mobile_app_notification_action"
# Per-task notification tag so a follow-up message replaces the previous one.
NOTIFICATION_TAG_TEMPLATE: Final = "choreflow_{task_id}"

# ---------------------------------------------------------------------------
# Log event types (§3.3, §8, Lastenheft §17.1)
# ---------------------------------------------------------------------------
EVENT_TASK_CREATED: Final = "task_created"
EVENT_TASK_UPDATED: Final = "task_updated"
EVENT_TASK_DELETED: Final = "task_deleted"
EVENT_TASK_NOTIFIED: Final = "task_notified"
EVENT_TASK_COMPLETED: Final = "task_completed"
EVENT_TASK_SNOOZED: Final = "task_snoozed"
EVENT_TASK_MISSED_NO_PRESENCE: Final = "task_missed_no_presence"
EVENT_TASK_EXPIRED: Final = "task_expired"
EVENT_TASK_SYNCED_FROM_TODO: Final = "task_synced_from_todo"
EVENT_TASK_COMPLETED_FROM_TODO: Final = "task_completed_from_todo"
EVENT_CALENDAR_TASK_CREATED: Final = "calendar_task_created"
EVENT_CALENDAR_TASK_REMOVED: Final = "calendar_task_removed"

LOG_EVENT_TYPES: Final[tuple[str, ...]] = (
    EVENT_TASK_CREATED,
    EVENT_TASK_UPDATED,
    EVENT_TASK_DELETED,
    EVENT_TASK_NOTIFIED,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_SNOOZED,
    EVENT_TASK_MISSED_NO_PRESENCE,
    EVENT_TASK_EXPIRED,
    EVENT_TASK_SYNCED_FROM_TODO,
    EVENT_TASK_COMPLETED_FROM_TODO,
    EVENT_CALENDAR_TASK_CREATED,
    EVENT_CALENDAR_TASK_REMOVED,
)

# Bus event used to surface ChoreFlow log events to the HA Logbook (§8).
LOGBOOK_EVENT: Final = f"{DOMAIN}_event"

# ---------------------------------------------------------------------------
# Completion sources (§2.3 completion_source, Lastenheft §17.2)
# ---------------------------------------------------------------------------
COMPLETION_SOURCE_PUSH: Final = "push"
COMPLETION_SOURCE_DASHBOARD: Final = "dashboard"
COMPLETION_SOURCE_TODO: Final = "todo"

# ---------------------------------------------------------------------------
# Selector scoring weights (§4.3)
# ---------------------------------------------------------------------------
# score = W_IMPORTANCE * importance_weight
#       + W_OVERDUE     * overdue_days
#       + W_DUE_TODAY   * is_due_today
#       - W_RECENT_PUSH * times_recently_notified
#
# Annahme: das Pflichtenheft legt nur die Score-Formel fest, nicht die konkreten
# Zahlen. Die folgenden Werte sind so gewählt, dass `high` strukturell vor
# `normal`/`low` liegt (der Importance-Term dominiert die übrigen Terme), die
# Raum-Bündelung `high` aber nicht dauerhaft verdrängt (siehe
# HIGH_FORCE_AFTER_SKIPPED). Alle Werte zentral hier änderbar.
W_IMPORTANCE: Final = 1.0
W_OVERDUE: Final = 5.0
W_DUE_TODAY: Final = 20.0
W_RECENT_PUSH: Final = 15.0

# Per-importance base weight. The high weight dominates the other score terms
# so that no realistic overdue/due-today combination lifts a normal task above
# a high task on importance alone.
IMPORTANCE_WEIGHT_HIGH: Final = 1000.0
IMPORTANCE_WEIGHT_NORMAL: Final = 100.0
IMPORTANCE_WEIGHT_LOW: Final = 10.0

IMPORTANCE_WEIGHTS: Final[dict[str, float]] = {
    "high": IMPORTANCE_WEIGHT_HIGH,
    "normal": IMPORTANCE_WEIGHT_NORMAL,
    "low": IMPORTANCE_WEIGHT_LOW,
}

# Size of the per-person candidate pool the next task is drawn from (§4.3).
TOP_POOL_SIZE: Final = 5

# Anti-starvation: if a high task for a person stays unpicked for this many
# consecutive follow-up selections (e.g. due to room bundling), it is forced
# next (§4.3, Lastenheft §13.4.5).
HIGH_FORCE_AFTER_SKIPPED: Final = 3

# ---------------------------------------------------------------------------
# Service names (§5.7, Lastenheft §19)
# ---------------------------------------------------------------------------
SERVICE_CREATE_TASK: Final = "create_task"
SERVICE_UPDATE_TASK: Final = "update_task"
SERVICE_DELETE_TASK: Final = "delete_task"
SERVICE_COMPLETE_TASK: Final = "complete_task"
SERVICE_SNOOZE_TASK: Final = "snooze_task"
SERVICE_START_DAILY_FLOW: Final = "start_daily_flow"
SERVICE_SEND_NEXT_TASK: Final = "send_next_task"
SERVICE_REBUILD_CALENDAR_TASKS: Final = "rebuild_calendar_tasks"
SERVICE_SYNC_TODO: Final = "sync_todo"
SERVICE_EXPORT_LOG: Final = "export_log"

# Common service field names.
ATTR_TASK_ID: Final = "task_id"
ATTR_PERSON_ENTITY: Final = "person_entity"
ATTR_SOURCE: Final = "source"
ATTR_ENTITY_ID: Final = "entity_id"
ATTR_EXPORT_FORMAT: Final = "format"

# ---------------------------------------------------------------------------
# Runtime data keys (hass.data[DOMAIN][entry_id])
# ---------------------------------------------------------------------------
DATA_COORDINATOR: Final = "coordinator"
DATA_STORE: Final = "store"
DATA_LOG_STORE: Final = "log_store"
DATA_SETTINGS: Final = "settings"

# ---------------------------------------------------------------------------
# Device metadata (groups entities under one ChoreFlow device, §5.6)
# ---------------------------------------------------------------------------
DEVICE_MANUFACTURER: Final = "ChoreFlow"
DEVICE_MODEL: Final = "Chore Manager"
