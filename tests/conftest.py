"""Shared pytest configuration for the ChoreFlow test suite.

Pure unit tests (models, engine, SQLite log) run without Home Assistant. Tests
that need a running HA use the ``hass`` fixture and the
``enable_custom_integrations`` fixture from
``pytest-homeassistant-custom-component`` directly — no global autouse fixture,
so the pure unit tests stay fast and HA-free.
"""

from __future__ import annotations
