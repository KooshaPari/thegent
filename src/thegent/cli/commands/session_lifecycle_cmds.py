"""Re-export facade for session lifecycle CLI commands (WL-124).

This module consolidates imports from:
- session_status_cmds: Session introspection and monitoring (status, inspect, logs)
- session_control_cmds: Session lifecycle control (wait, stop, pause, resume, fork, rollback, deferral)
"""

from __future__ import annotations

# Re-export from session_status_cmds
from thegent.cli.commands.session_status_cmds import (
    status_cmd,
    inspect_cmd,
    logs_cmd,
)

# Re-export from session_control_cmds
from thegent.cli.commands.session_control_cmds import (
    wait_cmd,
    stop_cmd,
    pause_cmd,
    resume_cmd,
    session_fork_cmd,
    session_rollback_cmd,
    session_cmd,
    deferral_list_cmd,
    deferral_resume_cmd,
)

__all__ = [
    "deferral_list_cmd",
    "deferral_resume_cmd",
    "inspect_cmd",
    "logs_cmd",
    "pause_cmd",
    "resume_cmd",
    "session_cmd",
    "session_fork_cmd",
    "session_rollback_cmd",
    "status_cmd",
    "stop_cmd",
    "wait_cmd",
]
