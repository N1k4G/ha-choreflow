import { LitElement, html, css, nothing, type TemplateResult, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { classMap } from "lit/directives/class-map.js";

import "./choreflow-card-editor";

import type {
  ChoreFlowCardConfig,
  ChoreFlowTask,
  CurrentOpenTask,
  EditForm,
  HistoryEvent,
  Page,
  PersonConfig,
  Importance,
  RecurrenceType,
  ServiceResult,
  HomeAssistant,
} from "./types";

const HISTORY_PAGE = 10;
const TASK_PAGE = 100;

type RowState = "idle" | "pending" | "done" | "snoozed";

@customElement("choreflow-card")
export class ChoreFlowCard extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private _config!: ChoreFlowCardConfig;

  // UI state
  @state() private _tab: "tasks" | "history" = "tasks";
  @state() private _personFilter = "all";
  @state() private _roomFilter = "all";
  @state() private _categoryFilter = "all";
  @state() private _groupByRoom = false;
  @state() private _dialogOpen = false;
  @state() private _personPickerOpen = false;
  @state() private _pendingAction: { taskId: string; action: "complete" | "snooze" } | null = null;

  // per-task transient state (optimistic UI + double-click protection)
  @state() private _rowState: Record<string, RowState> = {};
  @state() private _rowError: Record<string, string> = {};

  // Authoritative open tasks loaded through the response service. The sensor
  // attribute remains a bounded preview while the first request is running.
  @state() private _tasks: CurrentOpenTask[] | null = null;
  @state() private _tasksLoading = false;
  @state() private _tasksError: string | null = null;
  private _taskRequestGeneration = 0;

  // task edit dialog
  @state() private _editForm: EditForm | null = null;
  @state() private _editSaving = false;

  // history (loaded lazily via get_history response service)
  @state() private _history: HistoryEvent[] = [];
  @state() private _historyTotal = 0;
  @state() private _historyLoading = false;
  @state() private _historyOffset = 0;

  // ---- card lifecycle ----

  public static getConfigElement(): HTMLElement {
    return document.createElement("choreflow-card-editor");
  }

  public static getStubConfig(): Partial<ChoreFlowCardConfig> {
    return {
      title: "Haushalt",
      entities: {
        open_tasks: "sensor.choreflow_open_tasks",
        due_tasks: "sensor.choreflow_due_tasks",
        overdue_tasks: "sensor.choreflow_overdue_tasks",
        completed_today: "sensor.choreflow_completed_today",
        completed_this_week: "sensor.choreflow_completed_this_week",
        active_chains: "sensor.choreflow_active_chains",
      },
      persons: [],
      show_create: true,
      show_history: true,
    };
  }

  public setConfig(config: ChoreFlowCardConfig): void {
    if (!config || !config.entities || !config.entities.open_tasks) {
      throw new Error(
        "choreflow-card: 'entities.open_tasks' ist erforderlich (z. B. sensor.choreflow_open_tasks)."
      );
    }
    this._config = {
      show_create: true,
      show_history: true,
      ...config,
      persons: config.persons ?? [],
    };
    this._personFilter = config.default_person ?? "all";
    this._roomFilter = config.default_room ?? "all";
    this._categoryFilter = "all";
    this._tasks = null;
    this._tasksError = null;
    this._taskRequestGeneration += 1;
  }

  public getCardSize(): number {
    return 6;
  }

  protected updated(changed: PropertyValues): void {
    const previousHass = changed.get("hass") as HomeAssistant | undefined;
    const previousConfig = changed.get("_config") as ChoreFlowCardConfig | undefined;
    const previousOpenSensorEntity =
      previousConfig?.entities.open_tasks ?? this._config?.entities.open_tasks;
    const configChanged = changed.has("_config");
    const openSensorChanged =
      changed.has("hass") &&
      (previousOpenSensorEntity ? previousHass?.states[previousOpenSensorEntity] : undefined) !==
        this._openSensor;

    if (this.hass && this._config && (configChanged || openSensorChanged)) {
      void this._loadTasks(configChanged || this._tasks === null);
    }

    // Load history the first time the tab is opened.
    if (
      this._tab === "history" &&
      this._config?.show_history &&
      this._history.length === 0 &&
      !this._historyLoading &&
      this._historyOffset === 0
    ) {
      void this._loadHistory(true);
    }
  }

  // ---- data adapters (read only from hass.states) ----

  private get _openSensor() {
    const entityId = this._config?.entities.open_tasks;
    return entityId ? this.hass?.states[entityId] : undefined;
  }

  /** open_tasks attribute, normalised. The only place that attribute exists. */
  private _openTasks(): CurrentOpenTask[] {
    const attr = this._openSensor?.attributes?.open_tasks;
    return Array.isArray(attr) ? (attr as CurrentOpenTask[]) : [];
  }

  /** Full task collection, falling back to the sensor preview on first load. */
  private _baseTasks(): CurrentOpenTask[] {
    if (this._tasks !== null) return this._tasks;
    return this._personFilter === "all" ? this._openTasks() : [];
  }

  private async _setPersonFilter(personEntity: string): Promise<void> {
    if (personEntity === this._personFilter && this._tasks !== null) return;
    this._personFilter = personEntity;
    this._roomFilter = "all";
    this._categoryFilter = "all";
    this._tasks = null;
    this._tasksError = null;
    await this._loadTasks(true);
  }

  private _retryTasks(): void {
    void this._loadTasks(this._tasks === null);
  }

  private async _loadTasks(reset: boolean): Promise<void> {
    const generation = ++this._taskRequestGeneration;
    const previousTasks = reset ? null : this._tasks;
    if (reset) this._tasks = null;
    this._tasksLoading = true;
    this._tasksError = null;

    const personEntity = this._personFilter === "all" ? undefined : this._personFilter;
    const items: CurrentOpenTask[] = [];
    let offset = 0;

    try {
      while (true) {
        const serviceData: Record<string, unknown> = {
          status: "open",
          person_scope: "visible",
          limit: TASK_PAGE,
          offset,
        };
        if (personEntity) serviceData.person_entity = personEntity;

        const result = await this.hass.connection.sendMessagePromise<{
          response?: unknown;
        }>({
          type: "call_service",
          domain: "choreflow",
          service: "get_tasks",
          service_data: serviceData,
          return_response: true,
        });
        const page = this._validateTaskPage(result?.response);
        items.push(...page.items);

        if (!page.has_more) break;
        if (page.items.length === 0) {
          throw new Error("get_tasks returned an empty page with has_more=true");
        }
        offset += page.items.length;
      }

      if (generation !== this._taskRequestGeneration) return;
      this._tasks = items;
    } catch (err) {
      if (generation !== this._taskRequestGeneration) return;
      console.error("[choreflow] get_tasks", err);
      this._tasks = previousTasks;
      this._tasksError = "Aufgaben konnten nicht geladen werden.";
    } finally {
      if (generation === this._taskRequestGeneration) this._tasksLoading = false;
    }
  }

  private _validateTaskPage(value: unknown): { items: CurrentOpenTask[]; has_more: boolean } {
    if (!value || typeof value !== "object") throw new Error("Invalid get_tasks response");
    const page = value as Record<string, unknown>;
    if (!Array.isArray(page.items) || typeof page.has_more !== "boolean") {
      throw new Error("Invalid get_tasks page");
    }
    if (!page.items.every((item) => this._isTask(item))) {
      throw new Error("Invalid task in get_tasks page");
    }
    return { items: page.items, has_more: page.has_more };
  }

  private _isTask(value: unknown): value is CurrentOpenTask {
    if (!value || typeof value !== "object") return false;
    const task = value as Record<string, unknown>;
    return (
      typeof task.task_id === "string" &&
      typeof task.title === "string" &&
      typeof task.room === "string" &&
      typeof task.category === "string" &&
      (task.importance === "low" || task.importance === "normal" || task.importance === "high") &&
      (task.estimated_duration_minutes == null || typeof task.estimated_duration_minutes === "number") &&
      (task.due_date == null || typeof task.due_date === "string") &&
      (task.snooze_until == null || typeof task.snooze_until === "string")
    );
  }

  private _num(entityId?: string): number | null {
    if (!entityId) return null;
    const st = this.hass?.states[entityId];
    if (!st || st.state === "unknown" || st.state === "unavailable") return null;
    const n = Number(st.state);
    return Number.isFinite(n) ? n : null;
  }

  private _personName(cfg: PersonConfig): string {
    const st = this.hass?.states[cfg.entity];
    return (st?.attributes?.friendly_name as string) || cfg.entity.split(".").pop() || cfg.entity;
  }

  // ---- date helpers ----

  private _dueInfo(due: string | null) {
    if (!due) return { label: "Kein Termin", overdueDays: 0, isOverdue: false, isToday: false, rank: 100 };
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const d = new Date(due + "T00:00:00");
    const diff = Math.round((d.getTime() - today.getTime()) / 86_400_000);
    if (diff < 0) {
      const n = -diff;
      return {
        label: n === 1 ? "Gestern" : `vor ${n} Tagen`,
        overdueDays: n,
        isOverdue: true,
        isToday: false,
        rank: 1000 + n,
      };
    }
    if (diff === 0) return { label: "Heute", overdueDays: 0, isOverdue: false, isToday: true, rank: 600 };
    if (diff === 1) return { label: "Morgen", overdueDays: 0, isOverdue: false, isToday: false, rank: 300 };
    return {
      label: d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" }),
      overdueDays: 0,
      isOverdue: false,
      isToday: false,
      rank: 200,
    };
  }

  private _relTime(iso: string): string {
    const d = new Date(iso);
    const now = new Date();
    const sameDay = d.toDateString() === now.toDateString();
    const yest = new Date(now);
    yest.setDate(now.getDate() - 1);
    const time = d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
    if (sameDay) return `Heute ${time}`;
    if (d.toDateString() === yest.toDateString()) return `Gestern ${time}`;
    return d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" });
  }

  // ---- services (Home Assistant service API only) ----

  private _defaultPerson(): string | undefined {
    return (
      this._config.default_person ??
      (this._personFilter !== "all" ? this._personFilter : undefined) ??
      this._config.persons?.[0]?.entity
    );
  }

  private _availablePersonsForPicker(): Array<{ entity: string; name: string }> {
    if (this._config.persons?.length) {
      return this._config.persons.map((p) => ({ entity: p.entity, name: this._personName(p) }));
    }
    return Object.keys(this.hass.states)
      .filter((id) => id.startsWith("person."))
      .map((id) => ({
        entity: id,
        name: (this.hass.states[id].attributes?.friendly_name as string) || id.split(".").pop() || id,
      }));
  }

  private async _completeTask(taskId: string): Promise<void> {
    if (this._rowState[taskId] === "pending" || this._rowState[taskId] === "done") return; // dbl-click guard
    const person = this._defaultPerson();
    if (!person) {
      this._pendingAction = { taskId, action: "complete" };
      this._personPickerOpen = true;
      return;
    }
    await this._executeComplete(taskId, person);
  }

  private async _executeComplete(taskId: string, person: string): Promise<void> {
    this._setRow(taskId, "pending");
    this._clearRowError(taskId);
    try {
      await this.hass.callService("choreflow", "complete_task", {
        task_id: taskId,
        person_entity: person,
        source: "dashboard",
      });
      this._setRow(taskId, "done");
    } catch (err) {
      this._setRow(taskId, "idle");
      this._setRowError(taskId, this._friendlyError(err));
    }
  }

  private async _snoozeTask(taskId: string): Promise<void> {
    if (this._rowState[taskId] === "pending" || this._rowState[taskId] === "snoozed") return;
    const person = this._defaultPerson();
    if (!person) {
      this._pendingAction = { taskId, action: "snooze" };
      this._personPickerOpen = true;
      return;
    }
    await this._executeSnooze(taskId, person);
  }

  private async _executeSnooze(taskId: string, person: string): Promise<void> {
    this._setRow(taskId, "pending");
    this._clearRowError(taskId);
    try {
      await this.hass.callService("choreflow", "snooze_task", { task_id: taskId, person_entity: person });
      this._setRow(taskId, "snoozed");
    } catch (err) {
      this._setRow(taskId, "idle");
      this._setRowError(taskId, this._friendlyError(err));
    }
  }

  private async _reopenTask(taskId: string): Promise<void> {
    try {
      await this.hass.callService("choreflow", "reopen_task", { task_id: taskId });
      await this._loadHistory(true);
    } catch (err) {
      console.error("[choreflow] reopen_task", err);
    }
  }

  private async _openEdit(taskId: string): Promise<void> {
    const res = await this.hass.connection.sendMessagePromise<{ response?: ChoreFlowTask }>({
      type: "call_service",
      domain: "choreflow",
      service: "get_task",
      service_data: { task_id: taskId },
      return_response: true,
    });
    const task = res?.response;
    if (!task) return;
    this._editForm = {
      task_id: taskId,
      task_rule_id: task.task_rule_id ?? null,
      title: task.title ?? "",
      description: task.description ?? "",
      room: task.room ?? "",
      category: task.category ?? "",
      importance: task.importance ?? "normal",
      due_date: task.due_date ?? "",
      estimated_duration_minutes: task.estimated_duration_minutes != null ? String(task.estimated_duration_minutes) : "",
      recurrence_type: (task.recurrence_type as RecurrenceType) ?? "once",
      recurrence_interval: task.recurrence_interval != null ? String(task.recurrence_interval) : "1",
      recurrence_weekdays: task.recurrence_weekdays ?? [],
    };
  }

  private _closeEdit(): void {
    this._editForm = null;
    this._editSaving = false;
  }

  private _setEditField<K extends keyof EditForm>(key: K, value: EditForm[K]): void {
    if (!this._editForm) return;
    this._editForm = { ...this._editForm, [key]: value };
  }

  private _toggleEditWeekday(day: number): void {
    if (!this._editForm) return;
    const days = this._editForm.recurrence_weekdays;
    const next = days.includes(day) ? days.filter((d) => d !== day) : [...days, day];
    this._editForm = { ...this._editForm, recurrence_weekdays: next };
  }

  private async _saveEdit(): Promise<void> {
    if (!this._editForm || this._editSaving) return;
    this._editSaving = true;
    const f = this._editForm;
    const changes: Record<string, unknown> = {
      task_id: f.task_id,
      title: f.title,
      description: f.description.trim() || null,
      room: f.room || undefined,
      category: f.category || undefined,
      importance: f.importance,
      due_date: f.due_date || null,
      estimated_duration_minutes: f.estimated_duration_minutes
        ? Number(f.estimated_duration_minutes)
        : null,
    };
    if (f.task_rule_id) {
      changes.recurrence_type = f.recurrence_type;
      if (f.recurrence_type === "every_n_days") {
        changes.recurrence_interval = Number(f.recurrence_interval) || 1;
      } else if (f.recurrence_type === "weekdays") {
        changes.recurrence_weekdays = f.recurrence_weekdays;
      }
    }
    try {
      await this.hass.callService("choreflow", "update_task", changes);
      this._closeEdit();
    } catch (err) {
      console.error("[choreflow] update_task", err);
      this._editSaving = false;
    }
  }

  private async _createTask(data: Record<string, unknown>): Promise<ServiceResult> {
    // return_response gives back { success, task_id } for optimistic UI.
    const res = await this.hass.connection.sendMessagePromise<{
      response?: ServiceResult;
    }>({
      type: "call_service",
      domain: "choreflow",
      service: "create_task",
      service_data: data,
      return_response: true,
    });
    return res?.response ?? {};
  }

  private async _loadHistory(reset = false): Promise<void> {
    if (!this._config.show_history) return;
    this._historyLoading = true;
    const offset = reset ? 0 : this._historyOffset;
    try {
      const res = await this.hass.connection.sendMessagePromise<{
        response?: Page<HistoryEvent>;
      }>({
        type: "call_service",
        domain: "choreflow",
        service: "get_history",
        service_data: { limit: HISTORY_PAGE, offset },
        return_response: true,
      });
      const page = res?.response;
      if (page) {
        this._history = reset ? page.items : [...this._history, ...page.items];
        this._historyTotal = page.total;
        this._historyOffset = offset + page.items.length;
      }
    } catch (err) {
      console.error("[choreflow] get_history", err);
    } finally {
      this._historyLoading = false;
    }
  }

  private _friendlyError(err: unknown): string {
    const msg = (err as { message?: string })?.message ?? "";
    if (/visib|sicht/i.test(msg)) return "Aufgabe ist dir nicht sichtbar.";
    if (/assign|zuweis/i.test(msg)) return "Aufgabe ist dir nicht zugewiesen.";
    if (/not open|nicht offen|unknown|unbekannt/i.test(msg)) return "Aufgabe ist nicht mehr offen.";
    if (/person/i.test(msg)) return "Person ist nicht aktiviert.";
    return "Aktion fehlgeschlagen.";
  }

  private _setRow(id: string, s: RowState) {
    this._rowState = { ...this._rowState, [id]: s };
  }
  private _setRowError(id: string, msg: string) {
    this._rowError = { ...this._rowError, [id]: msg };
    // non-blocking: clear automatically
    window.setTimeout(() => this._clearRowError(id), 5000);
  }
  private _clearRowError(id: string) {
    if (!this._rowError[id]) return;
    const next = { ...this._rowError };
    delete next[id];
    this._rowError = next;
  }

  // ---- derived view model ----

  private _localDate(date = new Date()): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  private _isSnoozed(t: CurrentOpenTask): boolean {
    const todayIso = this._localDate();
    return (
      this._rowState[t.task_id] === "snoozed" ||
      (!!t.snooze_until && t.snooze_until > todayIso)
    );
  }

  private _visibleTasks(): CurrentOpenTask[] {
    let tasks = this._baseTasks().filter((t) => this._rowState[t.task_id] !== "done");
    if (this._roomFilter !== "all") tasks = tasks.filter((t) => t.room === this._roomFilter);
    if (this._categoryFilter !== "all") tasks = tasks.filter((t) => t.category === this._categoryFilter);
    return tasks.slice().sort((a, b) => {
      const aSnoozed = this._isSnoozed(a);
      const bSnoozed = this._isSnoozed(b);
      if (aSnoozed !== bSnoozed) return aSnoozed ? 1 : -1;
      return this._dueInfo(b.due_date).rank + impWeight(b.importance) - (this._dueInfo(a.due_date).rank + impWeight(a.importance));
    });
  }

  private _rooms(): string[] {
    return [...new Set(this._baseTasks().map((t) => t.room).filter(Boolean))];
  }
  private _categories(): string[] {
    return [...new Set(this._baseTasks().map((t) => t.category).filter(Boolean))];
  }

  // ---- render ----

  protected render(): TemplateResult {
    if (!this._config || !this.hass) return html``;

    if (!this._openSensor) {
      return html`<ha-card>
        <div class="error">
          <ha-icon icon="mdi:alert"></ha-icon>
          <div>
            <div class="error-title">ChoreFlow nicht verfügbar</div>
            <div class="error-body">
              Der Pflicht-Sensor <code>${this._config.entities.open_tasks}</code> wurde nicht gefunden.
              Prüfe die Card-Konfiguration und die ChoreFlow-Integration.
            </div>
          </div>
        </div>
      </ha-card>`;
    }

    const open = this._num(this._config.entities.open_tasks) ?? this._openTasks().length;
    const due = this._num(this._config.entities.due_tasks);
    const overdue = this._num(this._config.entities.overdue_tasks);
    const today = this._num(this._config.entities.completed_today);

    return html`
      <ha-card>
        <div class="head">
          <div class="title">
            <span class="title-text">${this._config.title ?? "ChoreFlow"}</span>
            <span class="sub">${open} offen</span>
          </div>
          <div class="head-actions">
            ${this._config.show_history
              ? html`<div class="seg" role="tablist">
                  <button role="tab" class=${classMap({ on: this._tab === "tasks" })} @click=${() => (this._tab = "tasks")}>Aufgaben</button>
                  <button role="tab" class=${classMap({ on: this._tab === "history" })} @click=${() => (this._tab = "history")}>Verlauf</button>
                </div>`
              : nothing}
            ${this._config.show_create
              ? html`<button class="icon-btn primary" aria-label="Aufgabe erstellen" title="Aufgabe erstellen" @click=${() => (this._dialogOpen = true)}>
                  <ha-icon icon="mdi:plus"></ha-icon>
                </button>`
              : nothing}
          </div>
        </div>

        <div class="stats">
          ${this._stat(open, "Offen")} ${this._stat(due, "Fällig")}
          ${this._stat(overdue, "Überfällig", overdue && overdue > 0 ? "error" : "")}
          ${this._stat(today, "Heute erledigt")}
        </div>

        ${this._tab === "tasks" ? this._renderTasks() : this._renderHistory()}
      </ha-card>

      ${this._dialogOpen ? this._renderDialog() : nothing}
      ${this._personPickerOpen ? this._renderPersonPicker() : nothing}
      ${this._editForm ? this._renderEditDialog() : nothing}
    `;
  }

  private _stat(value: number | null, label: string, tone = ""): TemplateResult {
    return html`<div class="stat">
      <div class="stat-num ${tone}">${value ?? "—"}</div>
      <div class="stat-label">${label}</div>
    </div>`;
  }

  private _renderTasks(): TemplateResult {
    const tasks = this._visibleTasks();
    const rooms = this._rooms();
    const categories = this._categories();

    return html`
      <div class="filters">
        <div class="seg">
          <button class=${classMap({ on: this._personFilter === "all" })} @click=${() => void this._setPersonFilter("all")}>Alle</button>
          ${(this._config.persons ?? []).map(
            (p) => html`<button class=${classMap({ on: this._personFilter === p.entity })} @click=${() => void this._setPersonFilter(p.entity)}>${this._personName(p)}</button>`
          )}
        </div>
        <select aria-label="Raum filtern" .value=${this._roomFilter} @change=${(e: Event) => (this._roomFilter = (e.target as HTMLSelectElement).value)}>
          <option value="all">Alle Räume</option>
          ${rooms.map((r) => html`<option value=${r}>${r}</option>`)}
        </select>
        <select aria-label="Kategorie filtern" .value=${this._categoryFilter} @change=${(e: Event) => (this._categoryFilter = (e.target as HTMLSelectElement).value)}>
          <option value="all">Alle Kategorien</option>
          ${categories.map((c) => html`<option value=${c}>${c}</option>`)}
        </select>
        <button class=${classMap({ chiptoggle: true, on: this._groupByRoom })} @click=${() => (this._groupByRoom = !this._groupByRoom)}>
          <ha-icon icon="mdi:view-list"></ha-icon>Nach Raum
        </button>
      </div>

      ${this._tasksLoading
        ? html`<div class="task-status"><span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>${this._tasks === null ? "Aufgaben werden geladen …" : "Aufgaben werden aktualisiert …"}</div>`
        : nothing}
      ${this._tasksError
        ? html`<div class="task-status task-error">
            <ha-icon icon="mdi:alert-outline"></ha-icon>
            <span>${this._tasksError}</span>
            <button type="button" @click=${() => this._retryTasks()}>Erneut versuchen</button>
          </div>`
        : nothing}

      ${tasks.length === 0 && (this._tasksLoading || this._tasksError)
        ? nothing
        : tasks.length === 0
        ? html`<div class="empty"><ha-icon icon="mdi:check"></ha-icon><p>Für diesen Filter ist nichts offen.</p></div>`
        : this._groupByRoom
        ? this._groupTasks(tasks)
        : html`<div class="list">${tasks.map((t) => this._renderRow(t))}</div>`}
    `;
  }

  private _groupTasks(tasks: CurrentOpenTask[]): TemplateResult {
    const groups = new Map<string, CurrentOpenTask[]>();
    for (const t of tasks) {
      const k = t.room || "Ohne Raum";
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k)!.push(t);
    }
    return html`<div class="list">
      ${[...groups.entries()].map(
        ([room, items]) => html`
          <div class="group-head"><ha-icon icon="mdi:map-marker"></ha-icon>${room}<span class="group-count">· ${items.length}</span></div>
          ${items.map((t) => this._renderRow(t))}
        `
      )}
    </div>`;
  }

  private _renderRow(t: CurrentOpenTask): TemplateResult {
    const due = this._dueInfo(t.due_date);
    const daysUntil = t.due_date
      ? Math.round((new Date(t.due_date + "T00:00:00").getTime() - new Date().setHours(0,0,0,0)) / 86_400_000)
      : null;

    // urgClass drives the left border accent and the due-date pill colour.
    // High importance always gets the amber accent regardless of due date.
    let urgClass = "normal";
    if (due.isOverdue) urgClass = "overdue";
    else if (t.importance === "high") urgClass = "high";
    else if (due.isToday) urgClass = "today";

    // urgLabel/urgIcon are the text badge — only shown when actionably soon.
    let urgIcon = "";
    let urgLabel = "";
    if (due.isOverdue) {
      urgIcon = "mdi:alert";
      urgLabel = `Überfällig · ${due.overdueDays} ${due.overdueDays === 1 ? "Tag" : "Tage"}`;
    } else if (due.isToday && t.importance === "high") {
      urgIcon = "mdi:alert-circle";
      urgLabel = "Heute fällig · Wichtig";
    } else if (due.isToday) {
      urgIcon = "mdi:clock-outline";
      urgLabel = "Heute fällig";
    } else if (t.importance === "high" && daysUntil !== null && daysUntil <= 2) {
      urgIcon = "mdi:chevron-up";
      urgLabel = daysUntil === 1 ? "Morgen fällig · Wichtig" : "Bald fällig · Wichtig";
    }
    const rs = this._rowState[t.task_id] ?? "idle";
    const isSnoozed = this._isSnoozed(t);
    const err = this._rowError[t.task_id];
    const hasId = !!t.task_id;
    const meta = [t.room, t.category];
    if (t.estimated_duration_minutes) meta.push(`${t.estimated_duration_minutes} Min`);

    return html`<div class=${classMap({ row: true, [urgClass]: true, settled: rs === "done", "row-snoozed": isSnoozed })}>
      <div class="row-main">
        <div class="row-top">
          <span class="row-title ${rs === "done" ? "struck" : ""}">${t.title}</span>
          <span class="due ${urgClass}">${due.label}</span>
        </div>
        <div class="row-meta">
          ${urgLabel ? html`<span class="urg ${urgClass}"><ha-icon icon=${urgIcon}></ha-icon>${urgLabel}</span>` : nothing}
          <span class="meta-text">${urgLabel ? "· " : ""}${meta.join(" · ")}</span>
        </div>
        ${isSnoozed ? html`<div class="snooze-badge"><ha-icon icon="mdi:clock-outline"></ha-icon>Aufgeschoben bis morgen</div>` : nothing}
        ${err ? html`<div class="row-error"><ha-icon icon="mdi:alert"></ha-icon>${err}</div>` : nothing}
      </div>
      <div class="row-actions">
        ${rs === "pending"
          ? html`<span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>`
          : rs === "done"
          ? html`<span class="settle ok"><ha-icon icon="mdi:check-circle"></ha-icon>Erledigt</span>`
          : isSnoozed
          ? html`
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${() => this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `
          : hasId
          ? html`
              <button class="icon-btn" aria-label="Bearbeiten" title="Bearbeiten" @click=${() => this._openEdit(t.task_id)}>
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="icon-btn" aria-label="Später erinnern" title="Später erinnern" @click=${() => this._snoozeTask(t.task_id)}>
                <ha-icon icon="mdi:clock-outline"></ha-icon>
              </button>
              <button class="icon-btn ok" aria-label="Erledigen" title="Erledigen" @click=${() => this._completeTask(t.task_id)}>
                <ha-icon icon="mdi:check-circle"></ha-icon>
              </button>
            `
          : nothing}
      </div>
    </div>`;
  }

  private _renderHistory(): TemplateResult {
    return html`
      <div class="hist-head">Verlauf</div>
      ${this._history.length === 0 && this._historyLoading
        ? html`<div class="empty"><p>Lädt…</p></div>`
        : this._history.length === 0
        ? html`<div class="empty"><p>Noch keine Einträge.</p></div>`
        : html`<div class="list">
            ${this._history.map((h) => {
              const v = eventVisual(h.event_type);
              const canReopen =
                (h.event_type === "task_completed" || h.event_type === "task_completed_from_todo") &&
                !!h.task_id;
              const meta = [v.label, h.room, h.person_entity ? personLabel(this.hass, h.person_entity) : null].filter(Boolean);
              return html`<div class="hist">
                <ha-icon class=${v.tone} icon=${v.icon}></ha-icon>
                <div class="hist-main">
                  <div class="hist-top">
                    <span class="hist-title">${h.title ?? "—"}</span>
                    <span class="hist-time">${this._relTime(h.timestamp)}</span>
                  </div>
                  <div class="hist-meta">${meta.join(" · ")}</div>
                </div>
                ${canReopen
                  ? html`<button class="icon-btn" aria-label="Korrigieren" title="Erledigung rückgängig machen" @click=${() => this._reopenTask(h.task_id!)}>
                      <ha-icon icon="mdi:undo"></ha-icon>
                    </button>`
                  : nothing}
              </div>`;
            })}
          </div>`}
      ${this._historyOffset < this._historyTotal
        ? html`<button class="loadmore" ?disabled=${this._historyLoading} @click=${() => this._loadHistory(false)}>
            ${this._historyLoading ? "Lädt…" : "Mehr laden"}
          </button>`
        : nothing}
    `;
  }

  private _renderPersonPicker(): TemplateResult {
    const persons = this._availablePersonsForPicker();
    const close = () => {
      this._personPickerOpen = false;
      this._pendingAction = null;
    };
    const pick = async (entity: string) => {
      this._personPickerOpen = false;
      const pending = this._pendingAction;
      this._pendingAction = null;
      if (!pending) return;
      if (pending.action === "complete") {
        await this._executeComplete(pending.taskId, entity);
      } else {
        await this._executeSnooze(pending.taskId, entity);
      }
    };
    return html`<div class="overlay" @click=${close}>
      <div class="dialog" style="max-width:320px" @click=${(e: Event) => e.stopPropagation()}>
        <div class="dlg-head">
          <span>Wer bist du?</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${close}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          ${persons.length
            ? persons.map(
                (p) => html`<button class="person-pick-btn" @click=${() => pick(p.entity)}>${p.name}</button>`
              )
            : html`<p style="margin:0;font-size:13px;color:var(--secondary-text-color)">Keine Personen gefunden. Bitte <code>persons</code> oder <code>default_person</code> in der Kartenkonfiguration setzen.</p>`}
        </div>
      </div>
    </div>`;
  }

  private _renderEditDialog(): TemplateResult {
    const f = this._editForm!;
    const isRule = !!f.task_rule_id;
    const DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
    return html`<div class="overlay" @click=${() => this._closeEdit()}>
      <div class="dialog edit-dialog" @click=${(e: Event) => e.stopPropagation()}>
        <div class="dlg-head">
          <span>Aufgabe bearbeiten</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${() => this._closeEdit()}>
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="dlg-body edit-body">
          <label class="edit-label">Titel
            <input class="edit-input" type="text" .value=${f.title}
              @input=${(e: Event) => this._setEditField("title", (e.target as HTMLInputElement).value)} />
          </label>
          <label class="edit-label">Beschreibung
            <textarea class="edit-input edit-textarea" rows="2"
              @input=${(e: Event) => this._setEditField("description", (e.target as HTMLTextAreaElement).value)}
            >${f.description}</textarea>
          </label>
          <div class="edit-row2">
            <label class="edit-label">Raum
              <input class="edit-input" type="text" .value=${f.room}
                @input=${(e: Event) => this._setEditField("room", (e.target as HTMLInputElement).value)} />
            </label>
            <label class="edit-label">Kategorie
              <input class="edit-input" type="text" .value=${f.category}
                @input=${(e: Event) => this._setEditField("category", (e.target as HTMLInputElement).value)} />
            </label>
          </div>
          <div class="edit-row2">
            <label class="edit-label">Wichtigkeit
              <select class="edit-input" .value=${f.importance}
                @change=${(e: Event) => this._setEditField("importance", (e.target as HTMLSelectElement).value as Importance)}>
                <option value="high" ?selected=${f.importance === "high"}>Hoch</option>
                <option value="normal" ?selected=${f.importance === "normal"}>Normal</option>
                <option value="low" ?selected=${f.importance === "low"}>Niedrig</option>
              </select>
            </label>
            <label class="edit-label">Dauer (Min)
              <input class="edit-input" type="number" min="1" max="1440" .value=${f.estimated_duration_minutes}
                @input=${(e: Event) => this._setEditField("estimated_duration_minutes", (e.target as HTMLInputElement).value)} />
            </label>
          </div>
          <label class="edit-label">Fälligkeitsdatum
            <input class="edit-input" type="date" .value=${f.due_date}
              @change=${(e: Event) => this._setEditField("due_date", (e.target as HTMLInputElement).value)} />
          </label>
          ${isRule ? html`
            <div class="edit-section-head">Wiederholung</div>
            <div class="edit-recurrence-btns">
              ${(["once", "every_n_days", "weekdays"] as RecurrenceType[]).map((rt) => html`
                <button class=${classMap({ "recurrence-btn": true, active: f.recurrence_type === rt })}
                  type="button" @click=${() => this._setEditField("recurrence_type", rt)}>
                  ${{ once: "Einmalig", every_n_days: "Alle N Tage", weekdays: "Wochentage" }[rt]}
                </button>`)}
            </div>
            ${f.recurrence_type === "every_n_days" ? html`
              <label class="edit-label">Intervall (Tage)
                <input class="edit-input" type="number" min="1" max="365" .value=${f.recurrence_interval}
                  @input=${(e: Event) => this._setEditField("recurrence_interval", (e.target as HTMLInputElement).value)} />
              </label>` : nothing}
            ${f.recurrence_type === "weekdays" ? html`
              <div class="weekday-picker">
                ${DAYS.map((d, i) => html`
                  <button type="button"
                    class=${classMap({ "wd-btn": true, active: f.recurrence_weekdays.includes(i) })}
                    @click=${() => this._toggleEditWeekday(i)}>${d}</button>`)}
              </div>` : nothing}
          ` : nothing}
        </div>
        <div class="dlg-footer">
          <button class="dlg-btn secondary" type="button" @click=${() => this._closeEdit()}>Abbrechen</button>
          <button class="dlg-btn primary" type="button" ?disabled=${this._editSaving} @click=${() => this._saveEdit()}>
            ${this._editSaving ? html`<ha-icon icon="mdi:loading" style="animation:spin .8s linear infinite"></ha-icon>` : nothing}
            Speichern
          </button>
        </div>
      </div>
    </div>`;
  }

  private _renderDialog(): TemplateResult {
    const rooms = this._rooms();
    const categories = this._categories();
    const persons = this._config.persons ?? [];
    const close = () => (this._dialogOpen = false);
    const submit = async (e: Event) => {
      e.preventDefault();
      const form = (e.target as HTMLElement).closest("form") as HTMLFormElement;
      const fd = new FormData(form);
      const title = String(fd.get("title") ?? "").trim();
      if (!title) {
        (form.querySelector("[name=title]") as HTMLInputElement)?.focus();
        return;
      }
      const visMode = String(fd.get("visibility_mode") || "all_enabled_persons");
      const assignMode = String(fd.get("assignment_mode") || "random");
      const calendarEntityId = String(fd.get("calendar_export_entity_id") || "").trim() || undefined;
      const data: Record<string, unknown> = {
        title,
        description: String(fd.get("description") || "") || undefined,
        room: String(fd.get("room") || "") || undefined,
        category: String(fd.get("category") || "") || undefined,
        importance: (String(fd.get("importance") || "normal") as Importance),
        estimated_duration_minutes: fd.get("duration") ? Number(fd.get("duration")) : undefined,
        due_date: String(fd.get("due_date") || "") || undefined,
        visibility_mode: visMode,
        visibility_persons: visMode === "selected_persons" ? fd.getAll("visibility_persons").map(String) : undefined,
        assignment_mode: assignMode,
        assignment_person: assignMode === "assigned" ? String(fd.get("assignment_person") || "") || undefined : undefined,
        calendar_export_entity_id: calendarEntityId,
      };
      try {
        await this._createTask(data);
        close();
      } catch (err) {
        console.error("[choreflow] create_task", err);
      }
    };

    return html`<div class="overlay" @click=${close}>
      <form class="dialog" @click=${(e: Event) => e.stopPropagation()} @submit=${submit}>
        <div class="dlg-head">
          <span>Neue Aufgabe</span>
          <button type="button" class="icon-btn" aria-label="Schließen" @click=${close}><ha-icon icon="mdi:close"></ha-icon></button>
        </div>
        <div class="dlg-body">
          <label>Titel<input name="title" placeholder="z. B. Bad putzen" autofocus /></label>
          <div class="two">
            <label>Raum<input name="room" list="cf-rooms" placeholder="Küche" /></label>
            <label>Kategorie<input name="category" list="cf-cats" placeholder="Reinigung" /></label>
          </div>
          <datalist id="cf-rooms">${rooms.map((r) => html`<option value=${r}></option>`)}</datalist>
          <datalist id="cf-cats">${categories.map((c) => html`<option value=${c}></option>`)}</datalist>
          <fieldset class="radios">
            <legend>Wichtigkeit</legend>
            ${["low", "normal", "high"].map(
              (v, i) => html`<label class="radio"><input type="radio" name="importance" value=${v} ?checked=${i === 1} />${{ low: "Niedrig", normal: "Normal", high: "Hoch" }[v]}</label>`
            )}
          </fieldset>
          <div class="two">
            <label>Dauer (Min)<input name="duration" type="number" min="0" placeholder="15" /></label>
            <label>Fällig am<input name="due_date" type="date" /></label>
          </div>
          <details>
            <summary>Sichtbarkeit &amp; Zuweisung</summary>
            <fieldset class="radios">
              <legend>Sichtbar für</legend>
              <label class="radio"><input type="radio" name="visibility_mode" value="all_enabled_persons" checked />Alle Personen</label>
              <label class="radio"><input type="radio" name="visibility_mode" value="selected_persons" />Ausgewählte</label>
            </fieldset>
            ${persons.length
              ? html`<div class="chips">
                  ${persons.map((p) => html`<label class="chip-check"><input type="checkbox" name="visibility_persons" value=${p.entity} />${this._personName(p)}</label>`)}
                </div>`
              : nothing}
            <fieldset class="radios">
              <legend>Zuweisung</legend>
              <label class="radio"><input type="radio" name="assignment_mode" value="random" checked />Zufällig</label>
              <label class="radio"><input type="radio" name="assignment_mode" value="assigned" />Feste Person</label>
            </fieldset>
            <label>Person<select name="assignment_person">
              <option value="">Person wählen…</option>
              ${persons.map((p) => html`<option value=${p.entity}>${this._personName(p)}</option>`)}
            </select></label>
          </details>
          <details>
            <summary>Kalender-Export</summary>
            <label style="margin-top:8px">
              Kalender-Entität (optional)
              <input
                name="calendar_export_entity_id"
                placeholder="calendar.outlook_kalender"
                autocomplete="off"
              />
            </label>
            <p style="font-size:11px;color:var(--secondary-text-color);margin:4px 0 0">
              Falls angegeben, wird der Fälligkeitstermin als Termin im gewählten Kalender angelegt.
            </p>
          </details>
        </div>
        <div class="dlg-foot">
          <button type="button" class="btn ghost" @click=${close}>Abbrechen</button>
          <button type="submit" class="btn primary">Erstellen</button>
        </div>
      </form>
    </div>`;
  }

  // ---- styles: HA theme variables ONLY ----

  static styles = css`
    :host { display: block; }
    ha-card { overflow: hidden; }
    ha-icon { --mdc-icon-size: 20px; display: inline-flex; }

    .head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 16px 12px; }
    .title { display: flex; align-items: baseline; gap: 9px; min-width: 0; }
    .title-text { font-size: 16px; font-weight: 500; }
    .sub { font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; }
    .head-actions { display: flex; align-items: center; gap: 6px; }

    .seg { display: flex; gap: 2px; background: var(--primary-background-color); border-radius: 6px; padding: 2px; }
    .seg button { border: none; border-radius: 5px; padding: 5px 11px; font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; background: transparent; color: var(--secondary-text-color); }
    .seg button.on { background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 1px 2px rgba(0,0,0,.15); }

    .icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 6px; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .icon-btn.ok { color: var(--success-color, var(--primary-color)); }
    .icon-btn.primary { width: 34px; height: 34px; background: var(--primary-color); color: var(--text-primary-color, #fff); }

    .stats { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--divider-color); border-bottom: 1px solid var(--divider-color); }
    .stat { padding: 11px 14px; }
    .stat + .stat { border-left: 1px solid var(--divider-color); }
    .stat-num { font-size: 22px; font-weight: 500; line-height: 1.1; }
    .stat-num.error { color: var(--error-color); }
    .stat-label { font-size: 10.5px; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; color: var(--secondary-text-color); margin-top: 3px; }



    .filters { padding: 10px 16px; border-bottom: 1px solid var(--divider-color); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .filters select { font: inherit; font-size: 12px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 6px 8px; cursor: pointer; }
    .task-status { display: flex; align-items: center; gap: 8px; padding: 10px 16px; font-size: 12px; color: var(--secondary-text-color); border-bottom: 1px solid var(--divider-color); }
    .task-status.task-error { color: var(--error-color); }
    .task-status button { margin-left: auto; border: 1px solid var(--divider-color); border-radius: 6px; padding: 5px 8px; color: var(--primary-text-color); background: transparent; font: inherit; cursor: pointer; }
    .chiptoggle { display: inline-flex; align-items: center; gap: 5px; border: 1px solid var(--divider-color); border-radius: 6px; padding: 6px 9px; font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; background: transparent; color: var(--secondary-text-color); }
    .chiptoggle ha-icon { --mdc-icon-size: 14px; }
    .chiptoggle.on { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }

    .list { display: flex; flex-direction: column; }
    .group-head { display: flex; align-items: center; gap: 7px; padding: 9px 16px 5px; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--secondary-text-color); background: var(--primary-background-color); }
    .group-head ha-icon { --mdc-icon-size: 13px; }
    .group-count { font-weight: 400; text-transform: none; letter-spacing: 0; }

    .row { position: relative; display: flex; gap: 11px; align-items: flex-start; padding: 13px 16px; border-bottom: 1px solid var(--divider-color); transition: opacity .3s; }
    .row::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--divider-color); }
    .row.overdue::before { background: var(--error-color); }
    .row.high::before { background: var(--warning-color); }
    .row.today::before { background: var(--primary-color); }
    .row.settled { opacity: .5; }
    .row.row-snoozed { opacity: .65; }
    .snooze-badge { display: inline-flex; align-items: center; gap: 4px; margin-top: 5px; font-size: 11.5px; color: var(--warning-color); }
    .snooze-badge ha-icon { --mdc-icon-size: 13px; }
    .row-main { flex: 1; min-width: 0; }
    .row-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
    .row-title { font-size: 14px; font-weight: 500; line-height: 1.35; }
    .row-title.struck { text-decoration: line-through; }
    .due { flex: none; border: 1px solid var(--divider-color); border-radius: 4px; padding: 1px 6px; font-size: 11px; line-height: 1.5; white-space: nowrap; color: var(--secondary-text-color); }
    .due.overdue { color: var(--error-color); }
    .due.today { color: var(--primary-color); }
    .row-meta { display: flex; align-items: center; gap: 6px; margin-top: 5px; flex-wrap: wrap; }
    .urg { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 500; }
    .urg ha-icon { --mdc-icon-size: 14px; }
    .urg.overdue { color: var(--error-color); }
    .urg.high { color: var(--warning-color); }
    .urg.today { color: var(--primary-color); }
    .meta-text { font-size: 12px; color: var(--secondary-text-color); }
    .row-error { display: flex; align-items: center; gap: 5px; margin-top: 6px; color: var(--error-color); font-size: 11.5px; }
    .row-error ha-icon { --mdc-icon-size: 13px; }
    .row-actions { flex: none; display: flex; align-items: center; gap: 2px; min-height: 32px; }
    .settle { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding-right: 6px; }
    .settle.ok { color: var(--success-color, var(--primary-color)); }
    .settle.warn { color: var(--warning-color); }
    .settle ha-icon { --mdc-icon-size: 16px; }
    .spin ha-icon { color: var(--secondary-text-color); animation: spin .8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    .empty { padding: 38px 16px; text-align: center; color: var(--secondary-text-color); }
    .empty ha-icon { --mdc-icon-size: 30px; opacity: .55; }
    .empty p { margin: 10px 0 0; font-size: 13px; }

    .hist-head { padding: 9px 16px; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--secondary-text-color); border-bottom: 1px solid var(--divider-color); }
    .hist { display: flex; gap: 11px; align-items: flex-start; padding: 11px 16px; border-bottom: 1px solid var(--divider-color); }
    .hist ha-icon { flex: none; margin-top: 1px; }
    .hist ha-icon.ok { color: var(--success-color, var(--primary-color)); }
    .hist ha-icon.warn { color: var(--warning-color); }
    .hist ha-icon.err { color: var(--error-color); }
    .hist ha-icon.muted { color: var(--secondary-text-color); }
    .hist-main { flex: 1; min-width: 0; }
    .hist-top { display: flex; justify-content: space-between; gap: 8px; }
    .hist-title { font-size: 13.5px; font-weight: 500; }
    .hist-time { flex: none; font-size: 11.5px; color: var(--secondary-text-color); white-space: nowrap; }
    .hist-meta { font-size: 12px; color: var(--secondary-text-color); margin-top: 3px; }
    .loadmore { width: 100%; border: none; background: transparent; color: var(--primary-color); font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; padding: 13px; }

    .error { display: flex; gap: 10px; padding: 18px; border-left: 3px solid var(--error-color); }
    .error ha-icon { color: var(--error-color); --mdc-icon-size: 22px; }
    .error-title { font-size: 15px; font-weight: 500; }
    .error-body { margin-top: 8px; font-size: 13px; line-height: 1.5; color: var(--secondary-text-color); }
    code { font-family: ui-monospace, monospace; font-size: 12px; background: var(--primary-background-color); padding: 1px 5px; border-radius: 4px; }

    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.46); display: flex; align-items: flex-start; justify-content: center; padding: 40px 16px; z-index: 9; overflow: auto; }
    .dialog { width: 100%; max-width: 440px; background: var(--card-background-color); color: var(--primary-text-color); border-radius: 8px; box-shadow: 0 12px 40px rgba(0,0,0,.4); overflow: hidden; }
    .dlg-head { display: flex; align-items: center; justify-content: space-between; padding: 15px 16px; border-bottom: 1px solid var(--divider-color); font-size: 15px; font-weight: 500; }
    .dlg-body { padding: 16px; display: flex; flex-direction: column; gap: 13px; max-height: 64vh; overflow: auto; }
    .dlg-body label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: var(--secondary-text-color); font-weight: 500; }
    .person-pick-btn { width: 100%; font: inherit; font-size: 14px; font-weight: 500; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 8px; padding: 12px 16px; cursor: pointer; text-align: left; }
    .person-pick-btn:hover { background: var(--secondary-background-color); }
    .dlg-body input, .dlg-body select { font: inherit; font-size: 14px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 9px 10px; outline: none; }
    .two { display: flex; gap: 10px; }
    .two label { flex: 1; }
    fieldset.radios { border: none; padding: 0; margin: 0; }
    fieldset.radios legend { font-size: 12px; color: var(--secondary-text-color); font-weight: 500; padding: 0; margin-bottom: 6px; }
    .radio, .chip-check { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; color: var(--primary-text-color); margin-right: 12px; }
    .chips { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
    details summary { font-size: 13px; font-weight: 500; cursor: pointer; padding: 8px 0; border-top: 1px solid var(--divider-color); }
    .dlg-foot { display: flex; justify-content: flex-end; gap: 8px; padding: 13px 16px; border-top: 1px solid var(--divider-color); }
    .btn { border-radius: 6px; padding: 9px 16px; font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; }
    .btn.ghost { border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); }
    .btn.primary { border: none; background: var(--primary-color); color: var(--text-primary-color, #fff); }

    /* ---- edit dialog ---- */
    .edit-dialog { max-width: 500px; }
    .edit-body { gap: 12px; }
    .edit-label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: var(--secondary-text-color); font-weight: 500; }
    .edit-input { font: inherit; font-size: 14px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 8px 10px; outline: none; width: 100%; box-sizing: border-box; }
    .edit-input:focus { border-color: var(--primary-color); }
    .edit-textarea { resize: vertical; min-height: 56px; font-family: inherit; }
    .edit-row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .edit-section-head { font-size: 12px; font-weight: 600; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: .05em; padding-top: 4px; border-top: 1px solid var(--divider-color); }
    .edit-recurrence-btns { display: flex; gap: 6px; flex-wrap: wrap; }
    .recurrence-btn { font: inherit; font-size: 13px; padding: 6px 12px; border: 1px solid var(--divider-color); border-radius: 20px; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .recurrence-btn.active { border-color: var(--primary-color); background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .weekday-picker { display: flex; gap: 5px; flex-wrap: wrap; }
    .wd-btn { font: inherit; font-size: 13px; font-weight: 500; width: 38px; height: 38px; border: 1px solid var(--divider-color); border-radius: 50%; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
    .wd-btn.active { border-color: var(--primary-color); background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .dlg-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 13px 16px; border-top: 1px solid var(--divider-color); }
    .dlg-btn { border-radius: 6px; padding: 9px 18px; font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
    .dlg-btn.secondary { border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); }
    .dlg-btn.primary { border: none; background: var(--primary-color); color: var(--text-primary-color, #fff); }
    .dlg-btn:disabled { opacity: .6; cursor: default; }
    .dlg-btn ha-icon { --mdc-icon-size: 16px; }

    @media (prefers-reduced-motion: reduce) { * { animation-duration: .001ms !important; transition-duration: .001ms !important; } }
  `;
}

function impWeight(imp: Importance): number {
  return imp === "high" ? 40 : imp === "low" ? -20 : 0;
}

function personLabel(hass: HomeAssistant, entity: string): string {
  const st = hass.states[entity];
  return (st?.attributes?.friendly_name as string) || entity.split(".").pop() || entity;
}

function eventVisual(type: string): { icon: string; tone: string; label: string } {
  switch (type) {
    case "task_completed": return { icon: "mdi:check-circle", tone: "ok", label: "Erledigt" };
    case "task_completed_from_todo": return { icon: "mdi:clipboard-check", tone: "ok", label: "Erledigt (To-do)" };
    case "task_reopened": return { icon: "mdi:undo", tone: "warn", label: "Korrigiert" };
    case "task_snoozed": return { icon: "mdi:clock-outline", tone: "warn", label: "Später erinnert" };
    case "task_created": return { icon: "mdi:plus-circle-outline", tone: "muted", label: "Erstellt" };
    case "task_updated": return { icon: "mdi:pencil", tone: "muted", label: "Geändert" };
    case "task_deleted": return { icon: "mdi:delete-outline", tone: "muted", label: "Gelöscht" };
    case "task_notified": return { icon: "mdi:bell-outline", tone: "muted", label: "Benachrichtigt" };
    case "task_missed_no_presence": return { icon: "mdi:account-off-outline", tone: "err", label: "Verpasst (abwesend)" };
    case "task_expired": return { icon: "mdi:close-circle-outline", tone: "err", label: "Abgelaufen" };
    case "task_synced_from_todo": return { icon: "mdi:sync", tone: "muted", label: "Aus To-do" };
    case "calendar_task_created": return { icon: "mdi:calendar-plus", tone: "muted", label: "Kalender erstellt" };
    case "calendar_task_removed": return { icon: "mdi:calendar-remove", tone: "muted", label: "Kalender entfernt" };
    default: return { icon: "mdi:information-outline", tone: "muted", label: type };
  }
}

// Register card with the picker.
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "choreflow-card",
  name: "ChoreFlow Card",
  description: "Ruhige, kompakte Aufgaben-Card für die ChoreFlow-Integration.",
  preview: true,
  documentationURL: "https://github.com/your-org/ha-choreflow-card",
});

declare global {
  interface HTMLElementTagNameMap {
    "choreflow-card": ChoreFlowCard;
  }
}
