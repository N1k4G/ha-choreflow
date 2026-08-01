"""Notification localization tests for ChoreFlow."""

from __future__ import annotations

from datetime import date

import pytest
from homeassistant.core import HomeAssistant

from custom_components.choreflow.const import (
    ACTION_OPEN_DASHBOARD,
    ACTION_PREFIX_DONE,
    ACTION_PREFIX_SNOOZE,
    DEFAULT_CALENDAR_CATEGORY,
    DEFAULT_CALENDAR_ROOM,
    DEFAULT_IMPORT_CATEGORY,
    DEFAULT_IMPORT_ROOM,
)
from custom_components.choreflow.models import Importance
from custom_components.choreflow.notify import async_send_task_push, build_action_id

from .factories import make_instance


def test_task_data_defaults_are_language_neutral() -> None:
    assert (DEFAULT_IMPORT_ROOM, DEFAULT_IMPORT_CATEGORY) == ("General", "General")
    assert (DEFAULT_CALENDAR_ROOM, DEFAULT_CALENDAR_CATEGORY) == (
        "Outside",
        "Waste",
    )


@pytest.mark.parametrize(
    ("language", "labels", "message"),
    [
        (
            "de",
            ["Erledigt", "Später erinnern", "Dashboard öffnen"],
            "Überfällig · Wichtig",
        ),
        (
            "en",
            ["Done", "Remind later", "Open dashboard"],
            "Overdue · Important",
        ),
        (
            "fr",
            ["Done", "Remind later", "Open dashboard"],
            "Overdue · Important",
        ),
    ],
)
async def test_task_push_uses_ha_language_without_changing_action_ids(
    hass: HomeAssistant,
    language: str,
    labels: list[str],
    message: str,
) -> None:
    calls: list[dict] = []
    hass.config.language = language
    hass.services.async_register(
        "notify", "mobile_app_niklas", lambda call: calls.append(dict(call.data))
    )
    task = make_instance(
        "task-1",
        room="Kitchen",
        category="Chores",
        importance=Importance.HIGH,
        due_date=date(2026, 6, 14),
    )

    assert await async_send_task_push(
        hass,
        "notify.mobile_app_niklas",
        task,
        "niklas",
        "2026-06-15",
    )
    await hass.async_block_till_done()

    payload = calls[0]
    actions = payload["data"]["actions"]
    assert [action["title"] for action in actions] == labels
    assert [action["action"] for action in actions] == [
        build_action_id(ACTION_PREFIX_DONE, task.id, "niklas"),
        build_action_id(ACTION_PREFIX_SNOOZE, task.id, "niklas"),
        ACTION_OPEN_DASHBOARD,
    ]
    assert payload["message"] == message
