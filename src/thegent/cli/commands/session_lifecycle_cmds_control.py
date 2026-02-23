"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import os
import signal
import sys
import time
from pathlib import Path

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _find_session_meta,
    _is_pid_running,
    _normalize_output_format,
    _read_session_meta,
    _resolve_session_id,
    _resolve_session_status,
    _session_paths,
    console,
    EXIT_TIMEOUT,
    _LOG_FOLLOW_POLL_SECONDS,
)
from thegent.cli.commands.session_cmds_helpers import (
    follow_log_stream,
)



def stop_cmd(
    session_id: str | None = None,
    force: bool = False,
    wind_down: bool = False,
    grace: int = 20,
) -> None:
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    if not _is_pid_running(pid):
        console.print("[dim]session not running[/dim]")
        return
    if force:
        os.killpg(pid, signal.SIGKILL)
        console.print("stopped (force)")
        return

    if wind_down:
        if grace < 0:
            raise typer.BadParameter("--grace must be >= 0")
        os.killpg(pid, signal.SIGTERM)
        start = time.time()
        while _is_pid_running(pid):
            if time.time() - start >= grace:
                break
            time.sleep(0.5)
        if _is_pid_running(pid):
            console.print(f"wind-down grace elapsed ({grace}s); session still running")
        else:
            console.print("stopped (wind-down)")
        return

    os.killpg(pid, signal.SIGTERM)
    console.print("stopped")



def pause_cmd(session_id: str | None = None) -> None:
    """Pause a background session (register pause event)."""
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)

    # Verify session exists
    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        # Fallback to finding run_id from registry by correlation_id (sid)
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == sid:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {sid}.[/red]")
        raise typer.Exit(1)

    registry.register_pause(run_id, reason="Manual pause")
    console.print(f"[yellow]Session {sid} marked as PAUSED in registry.[/yellow]")



def resume_cmd(
    session_id: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> None:
    """Resume a session in the registry state machine."""
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    meta_path = _find_session_meta(settings, sid)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        console.print(f"[red]Could not find run_id for session {sid}.[/red]")
        raise typer.Exit(1)

    registry.register_resume(run_id)
    console.print(f"[green]Session {sid} marked as RESUMED in registry.[/green]")



__all__ = [
    "pause_cmd",
    "resume_cmd",
    "stop_cmd",
]
