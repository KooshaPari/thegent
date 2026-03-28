"""Thegent CLI session commands domain.

This is a thin facade that re-exports commands from split submodules for backward compatibility.
"""

from __future__ import annotations

from phenotype_thegent_cli.cli.commands.session_contract_cmds import (
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contracts_cmd,
)

from phenotype_thegent_cli.cli.commands.session_lifecycle_cmds import (
    deferral_list_cmd,
    deferral_resume_cmd,
    inspect_cmd,
    logs_cmd,
    pause_cmd,
    resume_cmd,
    session_cmd,
    session_fork_cmd,
    session_rollback_cmd,
    stop_cmd,
    status_cmd,
    wait_cmd,
)

from phenotype_thegent_cli.cli.commands.session_utils_cmds import (
    events_cmd,
    feedback_cmd,
    history_cmd,
    inbox_list_cmd,
    inbox_wait_cmd,
    ps_cmd,
)

__all__ = [
    "deferral_list_cmd",
    "deferral_resume_cmd",
    "events_cmd",
    "feedback_cmd",
    "history_cmd",
    "inbox_list_cmd",
    "inbox_wait_cmd",
    "inspect_cmd",
    "logs_cmd",
    "pause_cmd",
    "ps_cmd",
    "resume_cmd",
    "session_cmd",
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
    "session_contracts_cmd",
    "session_fork_cmd",
    "session_rollback_cmd",
    "status_cmd",
    "stop_cmd",
    "wait_cmd",
]
