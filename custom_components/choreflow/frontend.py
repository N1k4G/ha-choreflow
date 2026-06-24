"""Auto-registration of the bundled ChoreFlow Lovelace card.

The card is built from the standalone project in ``card/`` and the bundled
artifact ships as ``www/choreflow-card.js``. Registering it here means users get
the card without manually adding a Lovelace resource.

The card is decoupled from the Python code — it only consumes the documented
service/sensor contract — so this module is the single seam to remove if the
card is later split into its own HACS frontend repository.
"""

from __future__ import annotations

import logging
import os

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import CARD_FILENAME, CARD_URL

_LOGGER = logging.getLogger(__name__)

# Guards against re-registration: the card is per HA instance, not per entry.
_REGISTERED_KEY = "choreflow_card_registered"


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve and register the bundled card once per Home Assistant instance."""
    if hass.data.get(_REGISTERED_KEY):
        return

    # ``frontend`` (and its ``http`` dependency) are always present in a real
    # Home Assistant but not in the lightweight test harness. Skip cleanly there
    # so the card stays a pure UI nicety that can never break entry setup.
    if "frontend" not in hass.config.components:
        _LOGGER.debug("frontend not loaded; skipping ChoreFlow card registration")
        return

    card_path = os.path.join(os.path.dirname(__file__), "www", CARD_FILENAME)
    if not await hass.async_add_executor_job(os.path.isfile, card_path):
        _LOGGER.warning(
            "ChoreFlow card bundle missing at %s; card not registered", card_path
        )
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, card_path, cache_headers=False)]
    )
    add_extra_js_url(hass, CARD_URL)
    hass.data[_REGISTERED_KEY] = True
    _LOGGER.debug("ChoreFlow card registered at %s", CARD_URL)
