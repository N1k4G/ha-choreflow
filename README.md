# ChoreFlow — Home Assistant Integration

[![Tests](https://github.com/N1k4G/ha-choreflow/actions/workflows/test.yaml/badge.svg)](https://github.com/N1k4G/ha-choreflow/actions/workflows/test.yaml)
[![Hassfest](https://github.com/N1k4G/ha-choreflow/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/N1k4G/ha-choreflow/actions/workflows/hassfest.yaml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

Track recurring household **chores** in Home Assistant. ChoreFlow recomputes
which chores are due on a schedule and exposes them as sensors, with buttons and
a service for on-demand control.

> **Status:** early scaffold. The setup, entities, and CI are in place; the
> chore data model and due-date logic are stubbed and marked with `TODO`.

---

## Features

- Config flow — set up entirely from the Home Assistant UI (single instance).
- `DataUpdateCoordinator` recomputes chore due-states on a configurable interval.
- Entities grouped under one HA device:
  - Sensors: **Chores due**, **Chores total**.
  - Button: **Refresh** (recompute now).
- `refresh` service for use in automations or Developer Tools.
- Diagnostics download (config entry data) from the HA UI.
- English and German UI translations.

---

## Installation

### HACS (recommended)

1. In HACS, add this repository as a **custom repository** (category: *Integration*).
2. Install **ChoreFlow**.
3. Restart Home Assistant.

### Manual

Copy `custom_components/choreflow` into your Home Assistant `config/custom_components/`
directory and restart.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **ChoreFlow** and follow the setup form.
3. Adjust the recompute interval later via the integration's **Configure** button.

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup, test, and
code-style guidelines.

```bash
pip install -r requirements_test.txt
pytest --cov=custom_components/choreflow
```

---

## License

[MIT](LICENSE) © 2026 Niklas Gorman
