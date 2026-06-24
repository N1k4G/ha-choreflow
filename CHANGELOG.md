# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (P0 — Plan & scaffold)
- HACS-compatible repository layout and metadata (`manifest.json`, `hacs.json`,
  `pyproject.toml`) targeting Home Assistant 2026.6.
- `const.py` with domain, config/option keys, defaults, log event types and the
  selector scoring weights (single source of truth).
- Config-entry lifecycle skeleton (`__init__.py`) and a minimal single-instance
  config flow placeholder.
- CI pipelines: hassfest, HACS validation, ruff, mypy, pytest with coverage.
