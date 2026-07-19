#!/usr/bin/env python3
"""WL-124: team_cmds stable import surface (extracted from cli.py monolith).

Team-domain command wrappers. The three team_create/team_task_* commands
delegate to the existing real implementations in `team_commands`; all
other team-domain stubs return 0.
"""

from __future__ import annotations

from typing import Any

from .team_commands import team_create_cmd, team_task_add_cmd, team_task_list_cmd


def summary_cmd(*args: Any, **kwargs: Any) -> int:
    """Show team summary. Stub returning 0."""
    return 0


def explain_cmd(*args: Any, **kwargs: Any) -> int:
    """Explain a team decision. Stub returning 0."""
    return 0


def fallbacks_cmd(*args: Any, **kwargs: Any) -> int:
    """Show fallbacks. Stub returning 0."""
    return 0


def handoff_cmd(*args: Any, **kwargs: Any) -> int:
    """Hand off work. Stub returning 0."""
    return 0


def handoff_show_cmd(*args: Any, **kwargs: Any) -> int:
    """Show a handoff. Stub returning 0."""
    return 0


def handoff_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List handoffs. Stub returning 0."""
    return 0


def handoff_confirm_cmd(*args: Any, **kwargs: Any) -> int:
    """Confirm a handoff. Stub returning 0."""
    return 0


def watchdog_cmd(*args: Any, **kwargs: Any) -> int:
    """Run watchdog. Stub returning 0."""
    return 0


def dlq_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List DLQ entries. Stub returning 0."""
    return 0


def traffic_cmd(*args: Any, **kwargs: Any) -> int:
    """Show traffic. Stub returning 0."""
    return 0


def drift_monitor_cmd(*args: Any, **kwargs: Any) -> int:
    """Monitor drift. Stub returning 0."""
    return 0


def roadmap_cmd(*args: Any, **kwargs: Any) -> int:
    """Show roadmap. Stub returning 0."""
    return 0


def self_heal_tests_cmd(*args: Any, **kwargs: Any) -> int:
    """Run self-heal tests. Stub returning 0."""
    return 0


def teammates_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List teammates. Stub returning 0."""
    return 0


def teammates_delegate_cmd(*args: Any, **kwargs: Any) -> int:
    """Delegate to a teammate. Stub returning 0."""
    return 0


def teammates_status_cmd(*args: Any, **kwargs: Any) -> int:
    """Show teammate status. Stub returning 0."""
    return 0


def queue_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List queue. Stub returning 0."""
    return 0


def recover_status_cmd(*args: Any, **kwargs: Any) -> int:
    """Show recovery status. Stub returning 0."""
    return 0


def project_register_cmd(*args: Any, **kwargs: Any) -> int:
    """Register a project. Stub returning 0."""
    return 0


def project_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List projects. Stub returning 0."""
    return 0


__all__ = [
    "summary_cmd",
    "explain_cmd",
    "fallbacks_cmd",
    "handoff_cmd",
    "handoff_show_cmd",
    "handoff_list_cmd",
    "handoff_confirm_cmd",
    "watchdog_cmd",
    "dlq_list_cmd",
    "traffic_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "teammates_list_cmd",
    "teammates_delegate_cmd",
    "teammates_status_cmd",
    "queue_list_cmd",
    "team_create_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
    "recover_status_cmd",
    "project_register_cmd",
    "project_list_cmd",
]
