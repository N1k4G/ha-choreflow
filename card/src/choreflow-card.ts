import { LitElement, html, css, nothing, type TemplateResult, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { classMap } from "lit/directives/class-map.js";

import "./choreflow-card-editor";

import type {
  ChoreFlowCardConfig,
  CurrentOpenTask,
  HistoryEvent,
  ChainAttributes,
  Page,
  PersonConfig,
  Importance,
  ServiceResult,
  HomeAssistant,
} from "./types";

const HISTORY_PAGE = 10;

interface PersonView {
  entity: string;
  name: string;
  active: boolean;
  completedToday: number | null;
  remaining: number | null;
  limit: number | null;
  hasDue: boolean;
}

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

  // per-task transient state (optimistic UI + double-click protection)
  @state() private _rowState: Record<string, RowState> = {};
  @state() private _rowError: Record<string, string> = {};

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
    if (config.default_person) this._personFilter = config.default_person;
    if (config.default_room) this._roomFilter = config.default_room;
  }

  public getCardSize(): number {
    return 6;
  }

  protected updated(changed: PropertyValues): void {
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
    void changed;
  }

  // ---- data adapters (read only from hass.states) ----

  private get _openSensor() {
    return this.hass?.states[this._config.entities.open_tasks];
  }

  /** open_tasks attribute, normalised. The only place that attribute exists. */
  private _openTasks(): CurrentOpenTask[] {
    const attr = this._openSensor?.attributes?.open_tasks;
    return Array.isArray(attr) ? (attr as CurrentOpenTask[]) : [];
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

  private _personViews(): PersonView[] {
    return (this._config.persons ?? []).map((p) => {
      const chain = p.chain_active ? this.hass?.states[p.chain_active] : undefined;
      const attrs = (chain?.attributes ?? {}) as ChainAttributes;
      const hasDueState = p.has_due_tasks ? this.hass?.states[p.has_due_tasks]?.state : undefined;
      return {
        entity: p.entity,
        name: this._personName(p),
        active: chain?.state === "on" || attrs.active === true,
        completedToday: attrs.tasks_completed_today ?? this._num(p.completed_today),
        remaining: attrs.remaining_today ?? this._num(p.remaining_today),
        limit: attrs.daily_limit ?? null,
        hasDue: hasDueState === "on",
      };
    });
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
    return this._config.default_person ?? this._config.persons?.[0]?.entity;
  }

  private async _completeTask(taskId: string): Promise<void> {
    if (this._rowState[taskId] === "pending" || this._rowState[taskId] === "done") return; // dbl-click guard
    const person = this._defaultPerson();
    if (!person) {
      this._setRowError(taskId, "Keine Person konfiguriert.");
      return;
    }
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
      this._setRowError(taskId, "Keine Person konfiguriert.");
      return;
    }
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

  private async _startFlow(person: string): Promise<void> {
    try {
      await this.hass.callService("choreflow", "start_daily_flow", { person_entity: person });
    } catch (err) {
      console.error("[choreflow] start_daily_flow", err);
    }
  }

  private async _sendNext(person: string): Promise<void> {
    try {
      await this.hass.callService("choreflow", "send_next_task", { person_entity: person });
    } catch (err) {
      console.error("[choreflow] send_next_task", err);
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

  private _visibleTasks(): CurrentOpenTask[] {
    let tasks = this._openTasks().filter((t) => {
      const rs = this._rowState[t.task_id];
      return rs !== "done" && rs !== "snoozed";
    });
    if (this._roomFilter !== "all") tasks = tasks.filter((t) => t.room === this._roomFilter);
    if (this._categoryFilter !== "all") tasks = tasks.filter((t) => t.category === this._categoryFilter);
    // Person filter is delegated to get_tasks in production via _refreshFilteredTasks();
    // the open_tasks attribute is the global, urgency-sorted feed.
    return tasks
      .slice()
      .sort((a, b) => this._dueInfo(b.due_date).rank + impWeight(b.importance) - (this._dueInfo(a.due_date).rank + impWeight(a.importance)));
  }

  private _rooms(): string[] {
    return [...new Set(this._openTasks().map((t) => t.room).filter(Boolean))];
  }
  private _categories(): string[] {
    return [...new Set(this._openTasks().map((t) => t.category).filter(Boolean))];
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
    `;
  }

  private _stat(value: number | null, label: string, tone = ""): TemplateResult {
    return html`<div class="stat">
      <div class="stat-num ${tone}">${value ?? "—"}</div>
      <div class="stat-label">${label}</div>
    </div>`;
  }

  private _renderTasks(): TemplateResult {
    const persons = this._personViews();
    const tasks = this._visibleTasks();
    const rooms = this._rooms();
    const categories = this._categories();

    return html`
      ${persons.length
        ? html`<div class="chains">
            ${persons.map(
              (p) => html`<div class="chain">
                <span class="chain-name">
                  <span class="dot ${p.active ? "ok" : "off"}"></span>${p.name}
                </span>
                <span class="fact">${p.active ? "Kette aktiv" : "Kette inaktiv"}</span>
                <span class="fact">· Heute ${p.completedToday ?? 0}</span>
                <span class="fact">· Slots ${p.remaining ?? 0}/${p.limit ?? "—"}</span>
                <button class="link" @click=${() => (p.active ? this._sendNext(p.entity) : this._startFlow(p.entity))}>
                  ${p.active ? "Nächste Aufgabe" : "Tag starten"}
                </button>
              </div>`
            )}
          </div>`
        : nothing}

      <div class="filters">
        <div class="seg">
          <button class=${classMap({ on: this._personFilter === "all" })} @click=${() => (this._personFilter = "all")}>Alle</button>
          ${(this._config.persons ?? []).map(
            (p) => html`<button class=${classMap({ on: this._personFilter === p.entity })} @click=${() => (this._personFilter = p.entity)}>${this._personName(p)}</button>`
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

      ${tasks.length === 0
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
    let urgClass = "normal";
    let urgIcon = "";
    let urgLabel = "";
    if (due.isOverdue) {
      urgClass = "overdue";
      urgIcon = "mdi:alert";
      urgLabel = `Überfällig · ${due.overdueDays} ${due.overdueDays === 1 ? "Tag" : "Tage"}`;
    } else if (t.importance === "high") {
      urgClass = "high";
      urgIcon = "mdi:chevron-up";
      urgLabel = "Wichtig";
    } else if (due.isToday) {
      urgClass = "today";
      urgIcon = "mdi:clock-outline";
      urgLabel = "Heute fällig";
    }
    const rs = this._rowState[t.task_id] ?? "idle";
    const err = this._rowError[t.task_id];
    const hasId = !!t.task_id;
    const meta = [t.room, t.category];
    if (t.estimated_duration_minutes) meta.push(`${t.estimated_duration_minutes} Min`);

    return html`<div class=${classMap({ row: true, [urgClass]: true, settled: rs === "done" || rs === "snoozed" })}>
      <div class="row-main">
        <div class="row-top">
          <span class="row-title ${rs === "done" ? "struck" : ""}">${t.title}</span>
          <span class="due ${urgClass}">${due.label}</span>
        </div>
        <div class="row-meta">
          ${urgLabel ? html`<span class="urg ${urgClass}"><ha-icon icon=${urgIcon}></ha-icon>${urgLabel}</span>` : nothing}
          <span class="meta-text">${urgLabel ? "· " : ""}${meta.join(" · ")}</span>
        </div>
        ${err ? html`<div class="row-error"><ha-icon icon="mdi:alert"></ha-icon>${err}</div>` : nothing}
      </div>
      <div class="row-actions">
        ${rs === "pending"
          ? html`<span class="spin"><ha-icon icon="mdi:loading"></ha-icon></span>`
          : rs === "done"
          ? html`<span class="settle ok"><ha-icon icon="mdi:check-circle"></ha-icon>Erledigt</span>`
          : rs === "snoozed"
          ? html`<span class="settle warn"><ha-icon icon="mdi:clock-outline"></ha-icon>Später</span>`
          : hasId
          ? html`
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

    .chains { padding: 12px 16px; border-bottom: 1px solid var(--divider-color); display: flex; flex-direction: column; gap: 10px; }
    .chain { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .chain-name { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 500; min-width: 78px; }
    .dot { width: 7px; height: 7px; border-radius: 50%; }
    .dot.ok { background: var(--success-color, var(--primary-color)); }
    .dot.off { background: var(--disabled-text-color); }
    .fact { font-size: 11.5px; color: var(--secondary-text-color); }
    .link { margin-left: auto; border: none; background: transparent; color: var(--primary-color); font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; }

    .filters { padding: 10px 16px; border-bottom: 1px solid var(--divider-color); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .filters select { font: inherit; font-size: 12px; color: var(--primary-text-color); background: var(--primary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; padding: 6px 8px; cursor: pointer; }
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
