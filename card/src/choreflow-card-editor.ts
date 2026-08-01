import { LitElement, html, css, nothing, type TemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { localize, type TranslationKey } from "./localize";
import type { ChoreFlowCardConfig, HomeAssistant, PersonConfig } from "./types";

/**
 * Minimal, dependency-free config editor. It exposes the global entity ids,
 * per-person entity mapping and the show_create / show_history / defaults.
 * Emits the standard `config-changed` event consumed by Lovelace.
 */
@customElement("choreflow-card-editor")
export class ChoreFlowCardEditor extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private _config!: ChoreFlowCardConfig;

  private _t(key: TranslationKey): string {
    return localize(this.hass, key);
  }

  public setConfig(config: ChoreFlowCardConfig): void {
    this._config = {
      ...config,
      entities: { ...config.entities, open_tasks: config.entities?.open_tasks ?? "" },
    };
  }

  private _emit(next: ChoreFlowCardConfig): void {
    this._config = next;
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config: next }, bubbles: true, composed: true })
    );
  }

  private _setGlobal(key: string, value: string): void {
    this._emit({ ...this._config, entities: { ...this._config.entities, [key]: value } });
  }

  private _setRoot(key: string, value: unknown): void {
    this._emit({ ...this._config, [key]: value } as ChoreFlowCardConfig);
  }

  private _setPerson(index: number, patch: Partial<PersonConfig>): void {
    const persons = [...(this._config.persons ?? [])];
    persons[index] = { ...persons[index], ...patch };
    this._emit({ ...this._config, persons });
  }

  private _addPerson(): void {
    this._emit({ ...this._config, persons: [...(this._config.persons ?? []), { entity: "" }] });
  }

  private _removePerson(index: number): void {
    const persons = [...(this._config.persons ?? [])];
    persons.splice(index, 1);
    this._emit({ ...this._config, persons });
  }

  private _sensorPicker(label: string, value: string | undefined, onChange: (v: string) => void, domains = ["sensor"]): TemplateResult {
    // Prefer ha-entity-picker when available; fall back to a plain input.
    if (customElements.get("ha-entity-picker")) {
      return html`<ha-entity-picker
        .hass=${this.hass}
        .label=${label}
        .value=${value ?? ""}
        .includeDomains=${domains}
        allow-custom-entity
        @value-changed=${(e: CustomEvent) => onChange(e.detail.value)}
      ></ha-entity-picker>`;
    }
    return html`<label class="row"><span>${label}</span><input .value=${value ?? ""} @input=${(e: Event) => onChange((e.target as HTMLInputElement).value)} /></label>`;
  }

  protected render(): TemplateResult {
    if (!this._config || !this.hass) return html``;
    const e = this._config.entities;
    return html`
      <div class="form">
        <label class="row"><span>${this._t("field.title")}</span><input .value=${this._config.title ?? ""} @input=${(ev: Event) => this._setRoot("title", (ev.target as HTMLInputElement).value)} /></label>

        <h4>${this._t("editor.global_sensors")}</h4>
        ${this._sensorPicker(this._t("editor.open_required"), e.open_tasks, (v) => this._setGlobal("open_tasks", v))}
        ${this._sensorPicker(this._t("editor.due"), e.due_tasks, (v) => this._setGlobal("due_tasks", v))}
        ${this._sensorPicker(this._t("editor.overdue"), e.overdue_tasks, (v) => this._setGlobal("overdue_tasks", v))}
        ${this._sensorPicker(this._t("editor.completed_today"), e.completed_today, (v) => this._setGlobal("completed_today", v))}
        ${this._sensorPicker(this._t("editor.completed_week"), e.completed_this_week, (v) => this._setGlobal("completed_this_week", v))}
        ${this._sensorPicker(this._t("editor.active_chains"), e.active_chains, (v) => this._setGlobal("active_chains", v))}

        <h4>${this._t("editor.persons")}</h4>
        ${(this._config.persons ?? []).map(
          (p, i) => html`
            <div class="person">
              <div class="person-head">
                ${this._sensorPicker(this._t("field.person"), p.entity, (v) => this._setPerson(i, { entity: v }), ["person"])}
                <button class="del" @click=${() => this._removePerson(i)} title=${this._t("editor.remove")}>✕</button>
              </div>
              ${this._sensorPicker(this._t("editor.open"), p.open_tasks, (v) => this._setPerson(i, { open_tasks: v }))}
              ${this._sensorPicker(this._t("stat.due"), p.due_tasks, (v) => this._setPerson(i, { due_tasks: v }))}
              ${this._sensorPicker(this._t("editor.completed_today"), p.completed_today, (v) => this._setPerson(i, { completed_today: v }))}
              ${this._sensorPicker(this._t("editor.remaining_today"), p.remaining_today, (v) => this._setPerson(i, { remaining_today: v }))}
              ${this._sensorPicker(this._t("editor.has_due"), p.has_due_tasks, (v) => this._setPerson(i, { has_due_tasks: v }), ["binary_sensor"])}
              ${this._sensorPicker(this._t("editor.chain_active"), p.chain_active, (v) => this._setPerson(i, { chain_active: v }), ["binary_sensor"])}
            </div>`
        )}
        <button class="add" @click=${this._addPerson}>${this._t("editor.add_person")}</button>

        <h4>${this._t("editor.options")}</h4>
        <label class="check"><input type="checkbox" .checked=${this._config.show_create !== false} @change=${(ev: Event) => this._setRoot("show_create", (ev.target as HTMLInputElement).checked)} />${this._t("editor.show_create")}</label>
        <label class="check"><input type="checkbox" .checked=${this._config.show_history !== false} @change=${(ev: Event) => this._setRoot("show_history", (ev.target as HTMLInputElement).checked)} />${this._t("editor.show_history")}</label>
        ${this._sensorPicker(this._t("editor.default_person"), this._config.default_person, (v) => this._setRoot("default_person", v), ["person"])}
      </div>
    `;
  }

  static styles = css`
    .form { display: flex; flex-direction: column; gap: 10px; padding: 4px; }
    h4 { margin: 8px 0 0; font-size: 13px; color: var(--secondary-text-color); }
    .row { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--secondary-text-color); }
    .row input { font: inherit; padding: 8px; border: 1px solid var(--divider-color); border-radius: 6px; background: var(--primary-background-color); color: var(--primary-text-color); }
    .person { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
    .person-head { display: flex; gap: 8px; align-items: flex-end; }
    .person-head ha-entity-picker, .person-head .row { flex: 1; }
    .del { border: none; background: transparent; color: var(--error-color); cursor: pointer; font-size: 14px; padding: 6px; }
    .add { align-self: flex-start; border: 1px dashed var(--divider-color); background: transparent; color: var(--primary-color); border-radius: 6px; padding: 8px 12px; cursor: pointer; font: inherit; }
    .check { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--primary-text-color); }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "choreflow-card-editor": ChoreFlowCardEditor;
  }
}

void nothing;
