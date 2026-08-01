"""Repair issues for ChoreFlow (Pflichtenheft §5.8 / §9, Lastenheft §23).

Creates informational (non-fixable) issues when a configured person entity,
notify service, or assigned to-do import target is invalid, and clears them once
resolved. To-do/calendar availability issues are added with their sources in
P4/P5.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import (
    CONF_IMPORT_ASSIGNMENT_MODE,
    CONF_IMPORT_ASSIGNMENT_PERSON,
    CONF_TODO_IMPORT_DEFAULTS,
    DOMAIN,
)
from .models import AssignmentMode
from .settings import ChoreFlowSettings

_ISSUE_INVALID_TODO_IMPORT_ASSIGNMENT = "invalid_todo_import_assignment"
_ISSUE_MISSING_PERSON = "missing_person"
_ISSUE_MISSING_NOTIFY = "missing_notify_service"


def _person_issue_id(entry_id: str, person: str) -> str:
    return f"{entry_id}_{_ISSUE_MISSING_PERSON}_{person}"


def _notify_issue_id(entry_id: str, person: str) -> str:
    return f"{entry_id}_{_ISSUE_MISSING_NOTIFY}_{person}"


def _todo_assignment_issue_id(entry_id: str) -> str:
    return f"{entry_id}_{_ISSUE_INVALID_TODO_IMPORT_ASSIGNMENT}"


def _notify_services(hass: HomeAssistant) -> set[str]:
    return {
        f"notify.{name}" for name in hass.services.async_services().get("notify", {})
    }


@callback
def async_check_issues(
    hass: HomeAssistant, entry: ConfigEntry, settings: ChoreFlowSettings
) -> None:
    """(Re)evaluate repair issues for the current configuration."""
    available_notify = _notify_services(hass)

    defaults = settings.todo.get(CONF_TODO_IMPORT_DEFAULTS, {})
    assignment_person = defaults.get(CONF_IMPORT_ASSIGNMENT_PERSON)
    todo_assignment_issue_id = _todo_assignment_issue_id(entry.entry_id)
    if defaults.get(CONF_IMPORT_ASSIGNMENT_MODE) == AssignmentMode.ASSIGNED and (
        not assignment_person or assignment_person not in settings.enabled_persons
    ):
        ir.async_create_issue(
            hass,
            DOMAIN,
            todo_assignment_issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=_ISSUE_INVALID_TODO_IMPORT_ASSIGNMENT,
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, todo_assignment_issue_id)

    for person in settings.enabled_persons:
        issue_id = _person_issue_id(entry.entry_id, person)
        if hass.states.get(person) is None:
            ir.async_create_issue(
                hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=_ISSUE_MISSING_PERSON,
                translation_placeholders={"person": person},
            )
        else:
            ir.async_delete_issue(hass, DOMAIN, issue_id)

    for person, person_settings in settings.person_settings.items():
        issue_id = _notify_issue_id(entry.entry_id, person)
        service = person_settings.notify_service
        if service and service not in available_notify:
            ir.async_create_issue(
                hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=_ISSUE_MISSING_NOTIFY,
                translation_placeholders={
                    "person": person,
                    "service": service,
                },
            )
        else:
            ir.async_delete_issue(hass, DOMAIN, issue_id)


@callback
def async_clear_issues(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Delete every ChoreFlow repair issue owned by an entry."""
    prefix = f"{entry.entry_id}_"
    registry = ir.async_get(hass)
    issue_ids = [
        issue_id
        for domain, issue_id in registry.issues
        if domain == DOMAIN and issue_id.startswith(prefix)
    ]
    for issue_id in issue_ids:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
