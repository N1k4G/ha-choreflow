"""Auto-registration of the bundled ChoreFlow Lovelace card.

The card is built from the standalone project in ``card/`` and the bundled
artifact ships as ``www/choreflow-card.js``. Registering it here means users get
the card without manually adding a Lovelace resource.

On every integration setup the resource URL is updated with a content hash so
that all connected browser sessions receive a websocket notification and display
the "reload" prompt automatically — no manual cache clearing needed.

The card is decoupled from the Python code — it only consumes the documented
service/sensor contract — so this module is the single seam to remove if the
card is later split into its own HACS frontend repository.
"""

from __future__ import annotations

import hashlib
import logging
import os

from homeassistant.components.frontend import add_extra_js_url

# isort: split
# HA 2026.8.0b0 re-exports this implicitly; strict mypy cannot see it.
from homeassistant.components.http import StaticPathConfig  # type: ignore[attr-defined]
from homeassistant.core import HomeAssistant

from .const import CARD_FILENAME, CARD_URL

_LOGGER = logging.getLogger(__name__)

# Static path can only be registered once per HA instance.
_STATIC_PATH_KEY = "choreflow_card_static_path"
_CARD_RESOURCE_TYPE = "module"


def _file_hash(path: str) -> str:
    """Return a short SHA-256 hex digest of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:12]


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve and register the bundled card, updating the version URL each time.

    Calling this on every entry setup (including reloads) ensures that whenever
    the card bundle changes the Lovelace resource URL is updated, which triggers
    a browser-reload notification in all connected HA frontends.
    """
    if "frontend" not in hass.config.components:
        _LOGGER.debug("frontend not loaded; skipping ChoreFlow card registration")
        return

    card_path = os.path.join(os.path.dirname(__file__), "www", CARD_FILENAME)
    if not await hass.async_add_executor_job(os.path.isfile, card_path):
        _LOGGER.warning(
            "ChoreFlow card bundle missing at %s; card not registered", card_path
        )
        return

    # Register the static file path once — re-registration raises an error.
    if not hass.data.get(_STATIC_PATH_KEY):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL, card_path, cache_headers=False)]
        )
        hass.data[_STATIC_PATH_KEY] = True

    card_hash = await hass.async_add_executor_job(_file_hash, card_path)
    versioned_url = f"{CARD_URL}?v={card_hash}"

    # Prefer the Lovelace resource registry: updating the URL fires a websocket
    # event that prompts all connected browsers to reload the page.
    if not await _sync_lovelace_resource(hass, versioned_url):
        # Fallback for YAML-mode Lovelace or when the registry isn't available.
        add_extra_js_url(hass, versioned_url)


async def _sync_lovelace_resource(hass: HomeAssistant, versioned_url: str) -> bool:
    """Create or update the card entry in the Lovelace resource registry.

    Returns True when the registry was available and the resource was managed,
    False when storage-mode Lovelace is not active (YAML mode or not loaded).
    """
    try:
        from homeassistant.components.lovelace.const import (  # noqa: PLC0415
            LOVELACE_DATA,
        )
    except ImportError:
        return False

    lovelace = hass.data.get(LOVELACE_DATA)
    if lovelace is None:
        return False

    resources = getattr(lovelace, "resources", None)
    if resources is None or not hasattr(resources, "async_create_item"):
        # YAML mode — resource registry is read-only.
        return False

    existing = next(
        (r for r in resources.async_items() if CARD_URL in r.get("url", "")),
        None,
    )

    if existing is None:
        await resources.async_create_item(
            {"res_type": _CARD_RESOURCE_TYPE, "url": versioned_url}
        )
        _LOGGER.debug("ChoreFlow card resource created: %s", versioned_url)
    elif existing["url"] != versioned_url:
        await resources.async_update_item(existing["id"], {"url": versioned_url})
        _LOGGER.debug("ChoreFlow card resource updated: %s", versioned_url)
    else:
        _LOGGER.debug("ChoreFlow card resource already current: %s", versioned_url)

    return True
