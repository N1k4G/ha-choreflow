"""Config flow for ChoreFlow.

P0 SKELETON: a single confirmation step so the (single-instance) config entry
can be created and the manifest's ``config_flow: true`` is valid. The full
multi-step Config Flow and the Options Flow — persons, per-person notify
targets, schedule, to-do and calendar sync (Pflichtenheft §5.5) — are
implemented in P3.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN


class ChoreFlowConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup of ChoreFlow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single ChoreFlow config entry."""
        # manifest `single_config_entry: true` already enforces one instance.
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, DEFAULT_NAME), data={}
            )

        schema = vol.Schema({vol.Required(CONF_NAME, default=DEFAULT_NAME): str})
        return self.async_show_form(step_id="user", data_schema=schema)
