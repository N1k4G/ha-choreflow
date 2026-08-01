"""Push delivery and notification-action parsing (Pflichtenheft §5.4).

ChoreFlow sends one task per push via the person's ``notify.mobile_app_*``
service, embedding action ids that encode the task and person so the
``mobile_app_notification_action`` listener (wired in ``__init__``) can route a
tap back to the coordinator without any user automation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .const import (
    ACTION_OPEN_DASHBOARD,
    ACTION_PREFIX_DONE,
    ACTION_PREFIX_SNOOZE,
    ACTION_SEPARATOR,
    DASHBOARD_URI,
    NOTIFICATION_TAG_TEMPLATE,
)
from .models import Importance, TaskInstance

_LOGGER = logging.getLogger(__name__)

_NOTIFICATION_TEXT: dict[str, dict[str, str]] = {
    "de": {
        "done": "Erledigt",
        "snooze": "Später erinnern",
        "dashboard": "Dashboard öffnen",
        "overdue": "Überfällig",
        "due_today": "Heute fällig",
        "important": "Wichtig",
    },
    "en": {
        "done": "Done",
        "snooze": "Remind later",
        "dashboard": "Open dashboard",
        "overdue": "Overdue",
        "due_today": "Due today",
        "important": "Important",
    },
}


@dataclass(frozen=True)
class NotificationAction:
    """A parsed notification action tap."""

    kind: str  # "done" | "snooze"
    task_id: str
    person_slug: str


def build_action_id(prefix: str, task_id: str, person_slug: str) -> str:
    """Compose ``<PREFIX>__<task_id>__<person_slug>`` (§5.4)."""
    return ACTION_SEPARATOR.join((prefix, task_id, person_slug))


def parse_action_id(action: str) -> NotificationAction | None:
    """Parse a ChoreFlow action id, or return None if it is not one of ours."""
    parts = action.split(ACTION_SEPARATOR)
    if len(parts) != 3:
        return None
    prefix, task_id, person_slug = parts
    if prefix == ACTION_PREFIX_DONE:
        kind = "done"
    elif prefix == ACTION_PREFIX_SNOOZE:
        kind = "snooze"
    else:
        return None
    return NotificationAction(kind=kind, task_id=task_id, person_slug=person_slug)


def _text_for(hass: HomeAssistant) -> dict[str, str]:
    """Return notification text for the HA language, falling back to English."""
    language = hass.config.language.lower().replace("_", "-").split("-", 1)[0]
    return _NOTIFICATION_TEXT.get(language, _NOTIFICATION_TEXT["en"])


def _message_for(
    task: TaskInstance, today_iso: str, text: dict[str, str]
) -> str:
    parts: list[str] = []
    if task.due_date is not None:
        due_iso = task.due_date.isoformat()
        if due_iso < today_iso:
            parts.append(text["overdue"])
        elif due_iso == today_iso:
            parts.append(text["due_today"])
    if task.importance == Importance.HIGH:
        parts.append(text["important"])
    return " · ".join(parts) if parts else task.category


async def async_send_task_push(
    hass: HomeAssistant,
    notify_service: str | None,
    task: TaskInstance,
    person_slug: str,
    today_iso: str,
) -> bool:
    """Send one task push. Returns False if no usable notify service exists."""
    if not notify_service:
        _LOGGER.warning("No notify service configured; skipping push for %s", task.id)
        return False

    domain, _, service = notify_service.partition(".")
    if not service or not hass.services.has_service(domain, service):
        _LOGGER.error("Notify service %s is unavailable", notify_service)
        return False

    text = _text_for(hass)
    actions = [
        {
            "action": build_action_id(ACTION_PREFIX_DONE, task.id, person_slug),
            "title": text["done"],
        },
        {
            "action": build_action_id(ACTION_PREFIX_SNOOZE, task.id, person_slug),
            "title": text["snooze"],
        },
        {
            "action": ACTION_OPEN_DASHBOARD,
            "title": text["dashboard"],
            "uri": DASHBOARD_URI,
        },
    ]
    service_data = {
        "title": f"{task.room}: {task.title}",
        "message": _message_for(task, today_iso, text),
        "data": {
            "tag": NOTIFICATION_TAG_TEMPLATE.format(task_id=task.id),
            "actions": actions,
        },
    }
    await hass.services.async_call(domain, service, service_data, blocking=False)
    return True
