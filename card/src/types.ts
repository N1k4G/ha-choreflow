// Shared type definitions for the ChoreFlow Lovelace card.
// These mirror the ChoreFlow backend data contract 1:1.

import type { HomeAssistant } from "custom-card-helpers";

export type Importance = "high" | "normal" | "low";
export type TaskStatus = "open" | "completed" | "deleted";
export type VisibilityMode = "all_enabled_persons" | "selected_persons";
export type AssignmentMode = "random" | "assigned";
export type TaskSource = "rule" | "dashboard" | "todo_sync" | "calendar" | "manual";

/** Shape of one entry inside `sensor.choreflow_open_tasks` → attributes.open_tasks. */
export interface CurrentOpenTask {
  task_id: string;
  title: string;
  room: string;
  category: string;
  importance: Importance;
  estimated_duration_minutes: number | null;
  due_date: string | null; // YYYY-MM-DD
  snooze_until: string | null; // YYYY-MM-DD; null means not snoozed
}

export type RecurrenceType = "every_n_days" | "weekdays" | "once";

/** Full task as returned by `choreflow.get_task` / `choreflow.get_tasks`. */
export interface ChoreFlowTask extends CurrentOpenTask {
  task_rule_id: string | null;
  description?: string | null;
  deadline: string | null;
  status: TaskStatus;
  visibility_mode: VisibilityMode;
  assignment_person?: string | null;
  assignment_mode: AssignmentMode;
  visibility_persons: string[];
  source: TaskSource;
  created_at: string;
  completed_at: string | null;
  completed_by: string | null;
  completion_source: string | null;
  recurrence_type: RecurrenceType | null;
  recurrence_interval: number | null;
  recurrence_weekdays: number[] | null;
}

/** Mutable form state used in the task edit dialog. */
export interface EditForm {
  task_id: string;
  task_rule_id: string | null;
  title: string;
  description: string;
  room: string;
  category: string;
  importance: Importance;
  due_date: string;
  estimated_duration_minutes: string;
  recurrence_type: RecurrenceType;
  recurrence_interval: string;
  recurrence_weekdays: number[];
}

/** Generic paged envelope returned by both query services. */
export interface Page<T> {
  api_version: 1;
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export type ChoreFlowEventType =
  | "task_created"
  | "task_updated"
  | "task_deleted"
  | "task_notified"
  | "task_completed"
  | "task_reopened"
  | "task_snoozed"
  | "task_missed_no_presence"
  | "task_expired"
  | "task_synced_from_todo"
  | "task_completed_from_todo"
  | "calendar_task_created"
  | "calendar_task_removed";

export interface HistoryEvent {
  event_id: string;
  event_type: ChoreFlowEventType;
  task_id: string | null;
  task_rule_id: string | null;
  title: string | null;
  room: string | null;
  category: string | null;
  importance: Importance | null;
  person_entity: string | null;
  timestamp: string; // ISO 8601 with timezone, descending
  source: string | null;
  completion_source: string | null;
  overdue_days_at_completion: number | null;
  decision_reason: string | null;
}

/** chain_active binary_sensor attributes. */
export interface ChainAttributes {
  api_version?: number;
  person_entity?: string;
  date?: string;
  started?: boolean;
  active?: boolean;
  pending_catchup?: boolean;
  current_task_id?: string | null;
  current_task_title?: string | null;
  tasks_sent_today?: number;
  tasks_completed_today?: number;
  daily_limit?: number;
  remaining_today?: number;
  ended_reason?: string | null;
}

// ----- Card configuration -----

export interface PersonConfig {
  entity: string; // person.* entity id (also used as person_entity for services)
  open_tasks?: string;
  due_tasks?: string;
  completed_today?: string;
  remaining_today?: string;
  has_due_tasks?: string;
  chain_active?: string;
}

export interface GlobalEntities {
  open_tasks: string; // required
  due_tasks?: string;
  overdue_tasks?: string;
  completed_today?: string;
  completed_this_week?: string;
  active_chains?: string;
}

export interface ChoreFlowCardConfig {
  type: string;
  title?: string;
  entities: GlobalEntities;
  persons?: PersonConfig[];
  show_create?: boolean;
  show_history?: boolean;
  default_person?: string;
  default_room?: string | null;
}

export interface ServiceResult {
  success?: boolean;
  task_id?: string;
}

// Re-export for convenience.
export type { HomeAssistant };
