#!/usr/bin/env python3
"""WL-124: session_cmds stable import surface (extracted from cli.py monolith).

Session-domain command wrappers. Public `*_cmd` functions delegate to the
corresponding `*_impl` helpers in `thegent.cli.commands.impl` when one
exists; otherwise they fall back to a zero-returning stub.
"""

from __future__ import annotations

from typing import Any


def history_cmd(*args: Any, **kwargs: Any) -> int:
    """Show session history. Stub returning 0."""
    return 0


def events_cmd(*args: Any, **kwargs: Any) -> int:
    """Show session events. Stub returning 0."""
    return 0


def inbox_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List inbox messages. Stub returning 0."""
    return 0


def inbox_wait_cmd(*args: Any, **kwargs: Any) -> int:
    """Wait for inbox messages. Stub returning 0."""
    return 0


def feedback_cmd(*args: Any, **kwargs: Any) -> int:
    """Submit feedback. Stub returning 0."""
    return 0


def ps_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """List processes. Thin shim over ps_impl."""
    from .impl import ps_impl

    return ps_impl(*args, **kwargs)


def session_contracts_cmd(*args: Any, **kwargs: Any) -> int:
    """Show session contracts. Stub returning 0."""
    return 0


def session_contract_health_gate_cmd(*args: Any, **kwargs: Any) -> int:
    """Run session contract health gate. Stub returning 0."""
    return 0


def session_contract_health_report_cmd(*args: Any, **kwargs: Any) -> int:
    """Show session contract health report. Stub returning 0."""
    return 0


def session_contract_health_trend_cmd(*args: Any, **kwargs: Any) -> int:
    """Show session contract health trend. Stub returning 0."""
    return 0


def status_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Show session status. Thin shim over status_impl."""
    from .impl import status_impl

    return status_impl(*args, **kwargs)


def inspect_cmd(*args: Any, **kwargs: Any) -> int:
    """Inspect a session. Stub returning 0."""
    return 0


def logs_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Show logs. Thin shim over logs_impl."""
    from .impl import logs_impl

    return logs_impl(*args, **kwargs)


def wait_cmd(*args: Any, **kwargs: Any) -> int:
    """Wait for a session to complete. Stub returning 0."""
    return 0


def stop_cmd(*args: Any, **kwargs: Any) -> None:
    """Stop a running session. Thin shim delegating to cli.stop_cmd.

    NOTE: We look up `cli.stop_cmd` via ``sys.modules`` at call time rather
    than ``from .cli import stop_cmd`` to avoid import-time circular
    references: cli.py re-exports many of the names in this module, and
    `stop_cmd` is the canonical implementation in cli.py (NOT a stub).
    Resolving at call time ensures we always reach the real implementation,
    never a stale shim or recursive shadow.
    """
    import sys

    cli_mod = sys.modules.get("thegent.cli.commands.cli")
    if cli_mod is None:
        # Fallback: explicit import if cli.py not yet loaded.
        from . import cli as cli_mod  # type: ignore[assignment]

    return cli_mod.stop_cmd(*args, **kwargs)


def pause_cmd(*args: Any, **kwargs: Any) -> int:
    """Pause a session. Stub returning 0."""
    return 0


def resume_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Resume a session. Thin shim over resume_impl."""
    from .impl import resume_impl

    return resume_impl(*args, **kwargs)  # type: ignore[arg-type]


def session_fork_cmd(*args: Any, **kwargs: Any) -> int:
    """Fork a session. Stub returning 0."""
    return 0


def session_rollback_cmd(*args: Any, **kwargs: Any) -> int:
    """Roll back a session. Stub returning 0."""
    return 0


def session_cmd(*args: Any, **kwargs: Any) -> int:
    """Generic session command. Stub returning 0."""
    return 0


def session_contract_negotiate_cmd(*args: Any, **kwargs: Any) -> int:
    """Negotiate session contract. Stub returning 0."""
    return 0


def session_contract_trend_analysis_cmd(*args: Any, **kwargs: Any) -> int:
    """Analyze session contract trend. Stub returning 0."""
    return 0


def deferral_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List deferrals. Stub returning 0."""
    return 0


def deferral_resume_cmd(*args: Any, **kwargs: Any) -> int:
    """Resume from deferral. Stub returning 0."""
    return 0


__all__ = [
    "history_cmd",
    "events_cmd",
    "inbox_list_cmd",
    "inbox_wait_cmd",
    "feedback_cmd",
    "ps_cmd",
    "session_contracts_cmd",
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
    "status_cmd",
    "inspect_cmd",
    "logs_cmd",
    "wait_cmd",
    "stop_cmd",
    "pause_cmd",
    "resume_cmd",
    "session_fork_cmd",
    "session_rollback_cmd",
    "session_cmd",
    "session_contract_negotiate_cmd",
    "session_contract_trend_analysis_cmd",
    "deferral_list_cmd",
    "deferral_resume_cmd",
]
