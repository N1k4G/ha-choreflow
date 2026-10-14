"""Tests for the Lovelace resource registration of the bundled card."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from homeassistant.components.lovelace.const import LOVELACE_DATA

from custom_components.choreflow.const import CARD_URL
from custom_components.choreflow.frontend import _sync_lovelace_resource

VERSIONED_URL = f"{CARD_URL}?v=newhash"


class FakeResourceCollection:
    """Minimal stand-in for HA's ResourceStorageCollection."""

    def __init__(self, stored: list[dict[str, Any]], *, loaded: bool) -> None:
        self._stored = stored
        self.data: dict[str, dict[str, Any]] = {}
        self.loaded = loaded
        self.load_calls = 0
        self._next_id = 100

    async def async_load(self) -> None:
        self.load_calls += 1
        self.data = {item["id"]: dict(item) for item in self._stored}

    def async_items(self) -> list[dict[str, Any]]:
        return list(self.data.values())

    async def async_create_item(self, data: dict[str, Any]) -> dict[str, Any]:
        item = {"id": str(self._next_id), "type": data["res_type"], "url": data["url"]}
        self._next_id += 1
        self.data[item["id"]] = item
        return item

    async def async_update_item(
        self, item_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        self.data[item_id].update(updates)
        return self.data[item_id]

    async def async_delete_item(self, item_id: str) -> None:
        del self.data[item_id]


def _hass(resources: FakeResourceCollection) -> Any:
    lovelace = SimpleNamespace(resources=resources)
    return SimpleNamespace(data={LOVELACE_DATA: lovelace})


async def test_unloaded_collection_is_loaded_before_lookup() -> None:
    """An existing resource must be found even if the collection wasn't loaded."""
    resources = FakeResourceCollection(
        [{"id": "1", "type": "module", "url": f"{CARD_URL}?v=oldhash"}],
        loaded=False,
    )

    assert await _sync_lovelace_resource(_hass(resources), VERSIONED_URL)

    assert resources.load_calls == 1
    assert resources.loaded is True
    assert resources.async_items() == [
        {"id": "1", "type": "module", "url": VERSIONED_URL}
    ]


async def test_repeated_syncs_do_not_create_duplicates() -> None:
    """Simulated restarts with an unloaded collection keep a single resource."""
    stored: list[dict[str, Any]] = []
    for _ in range(3):
        resources = FakeResourceCollection(stored, loaded=False)
        assert await _sync_lovelace_resource(_hass(resources), VERSIONED_URL)
        stored = resources.async_items()

    assert [r["url"] for r in stored] == [VERSIONED_URL]


async def test_existing_duplicates_are_removed() -> None:
    """Leftover duplicates are deleted; the first entry is kept and updated."""
    other = {"id": "9", "type": "module", "url": "/local/other-card.js"}
    resources = FakeResourceCollection(
        [
            {"id": "1", "type": "module", "url": f"{CARD_URL}?v=a"},
            other,
            {"id": "2", "type": "module", "url": f"{CARD_URL}?v=b"},
            {"id": "3", "type": "module", "url": VERSIONED_URL},
        ],
        loaded=False,
    )

    assert await _sync_lovelace_resource(_hass(resources), VERSIONED_URL)

    assert resources.async_items() == [
        {"id": "1", "type": "module", "url": VERSIONED_URL},
        other,
    ]


async def test_loaded_collection_is_not_reloaded() -> None:
    """An already loaded collection is used as-is."""
    resources = FakeResourceCollection([], loaded=True)

    assert await _sync_lovelace_resource(_hass(resources), VERSIONED_URL)

    assert resources.load_calls == 0
    assert [r["url"] for r in resources.async_items()] == [VERSIONED_URL]
