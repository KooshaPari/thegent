#!/usr/bin/env python3
"""WL-124: run_cmds stable import surface (extracted from cli.py monolith).

Run-domain command wrappers. Public `*_cmd` functions delegate to the
corresponding `*_impl` helpers in `thegent.cli.commands.impl` when one
exists; otherwise they fall back to a zero-returning stub.
"""

from __future__ import annotations

from typing import Any


def run_cmd(*args: Any, **kwargs: Any) -> int:
    """Run a prompt. Thin shim over run_impl."""
    from .impl import run_impl

    return run_impl(*args, **kwargs)  # type: ignore[arg-type]


def loop_cmd(*args: Any, **kwargs: Any) -> int:
    """Run an interactive loop. Stub returning 0."""
    return 0


def loop_send_cmd(*args: Any, **kwargs: Any) -> int:
    """Send a message into the loop. Stub returning 0."""
    return 0


def loop_stop_cmd(*args: Any, **kwargs: Any) -> int:
    """Stop the running loop. Stub returning 0."""
    return 0


def bg_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Background a session. Thin shim over bg_impl."""
    from .impl import bg_impl

    return bg_impl(*args, **kwargs)


def retry_cmd(*args: Any, **kwargs: Any) -> int:
    """Retry a failed run. Stub returning 0."""
    return 0


def replay_cmd(*args: Any, **kwargs: Any) -> int:
    """Replay a prior run. Stub returning 0."""
    return 0


def trace_replay_cmd(*args: Any, **kwargs: Any) -> int:
    """Replay a captured trace. Stub returning 0."""
    return 0


def terminal_route_cmd(*args: Any, **kwargs: Any) -> int:
    """Route a command to a terminal. Stub returning 0."""
    return 0


def deep_research_cmd(*args: Any, **kwargs: Any) -> int:
    """Run deep research. Stub returning 0."""
    return 0


def takeover_cmd(*args: Any, **kwargs: Any) -> int:
    """Take over an in-flight session. Stub returning 0."""
    return 0


def run_diff_cmd(*args: Any, **kwargs: Any) -> int:
    """Diff two runs. Stub returning 0."""
    return 0


__all__ = [
    "run_cmd",
    "loop_cmd",
    "loop_send_cmd",
    "loop_stop_cmd",
    "bg_cmd",
    "retry_cmd",
    "replay_cmd",
    "trace_replay_cmd",
    "terminal_route_cmd",
    "deep_research_cmd",
    "takeover_cmd",
    "run_diff_cmd",
]
