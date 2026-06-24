"""Shared pytest configuration for the ChoreFlow test suite.

Pure unit tests (models, engine, SQLite log) run without Home Assistant. Tests
that need a running HA use the ``hass`` fixture and the
``enable_custom_integrations`` fixture from
``pytest-homeassistant-custom-component`` directly — no global autouse fixture,
so the pure unit tests stay fast and HA-free.

Note: the HA integration tests require Linux/macOS (or WSL); the HA pytest
plugin does not run on native Windows. CI runs them on ubuntu-latest.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _isolate_log_db() -> Iterator[None]:
    """Remove the shared SQLite log between tests for deterministic counts.

    ``pytest-homeassistant-custom-component`` reuses a single test config dir,
    so ``choreflow.db`` (written via ``hass.config.path``) would otherwise
    persist across tests and leak completion events. This stays HA-free, so the
    pure unit tests are unaffected and never spin up Home Assistant.
    """
    from pytest_homeassistant_custom_component.common import get_test_config_dir

    path = get_test_config_dir("choreflow.db")
    if os.path.exists(path):
        os.remove(path)
    yield
    if os.path.exists(path):
        os.remove(path)
