from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

import orjson as json
import typer
from rich.console import Console

from thegent_cli.cli.commands._cli_shared import (
    EXIT_TIMEOUT,
    ThegentSettings,
    _find_session_meta,
    _is_pid_running,
    _read_session_meta,
    _resolve_session_id,
    _session_paths,
)

console = Console()

def wait_cmd(session_id: str | None = None, timeout: int = 0) -> None:
    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    start = time.time()
    while _is_pid_running(pid):
        if timeout > 0 and (time.time() - start) >= timeout:
            console.print(
                f"[yellow]Operation timed out: wait for session exceeded {timeout}s. "
                "Session may still be running.[/yellow]"
            )
            raise typer.Exit(EXIT_TIMEOUT)
        time.sleep(0.5)
    rc = int(p["rc"].read_text(encoding="utf-8").strip()) if p["rc"].exists() else 0
    console.print(str(rc))
    raise typer.Exit(rc)


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


def session_fork_cmd(
    session_id: str,
    from_turn: int | None = None,
    new_session_id: str | None = None,
) -> None:
    """Fork a session via SessionManager API."""
    from thegent_execution.session import SessionManager, SessionManagerError

    session_id = session_id.strip()
    if not session_id:
        console.print("[red]Session fork failed:[/red] session_id must be non-empty")
        raise typer.Exit(2)
    if from_turn is not None and from_turn < 1:
        console.print("[red]Session fork failed:[/red] --from-turn must be >= 1 when provided")
        raise typer.Exit(2)

    if new_session_id is not None:
        cleaned_new_session_id = new_session_id.strip()
        if not cleaned_new_session_id:
            console.print("[red]Session fork failed:[/red] --new-session-id must be non-empty when provided")
            raise typer.Exit(2)
        if cleaned_new_session_id == session_id:
            console.print("[red]Session fork failed:[/red] --new-session-id must differ from source session_id")
            raise typer.Exit(2)
        new_session_id = cleaned_new_session_id

    manager = SessionManager()
    try:
        fork_id = manager.fork_session(
            session_id,
            from_turn=from_turn,
            new_session_id=new_session_id,
        )
    except SessionManagerError as exc:
        console.print(f"[red]Session fork failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print(f"[green]Forked session:[/green] {fork_id}")


def session_rollback_cmd(session_id: str, n_turns: int) -> None:
    """Rollback a session via SessionManager API."""
    from thegent_execution.session import SessionManager, SessionManagerError

    session_id = session_id.strip()
    if not session_id:
        console.print("[red]Session rollback failed:[/red] session_id must be non-empty")
        raise typer.Exit(2)
    if n_turns < 1:
        console.print("[red]Session rollback failed:[/red] --n-turns must be >= 1")
        raise typer.Exit(2)

    manager = SessionManager()
    try:
        remaining = manager.rollback_session(session_id, n_turns=n_turns)
    except SessionManagerError as exc:
        console.print(f"[red]Session rollback failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    console.print(f"[green]Rollback complete:[/green] {session_id} now has {remaining} turns")


def session_cmd(
    session_id: str | None = typer.Argument(None, help="Specific session ID to manage"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch session live"),
    action: str | None = typer.Option(None, "--action", "-a", help="Action to perform (stop, pause, resume, logs)"),
) -> None:
    """Rich TUI for session management with subagent monitoring (WP-8002)."""
    from thegent_cli.ux.session_tui import SessionTUI

    tui = SessionTUI(session_id)

    if action:
        if not session_id:
            console.print("[red]Error: Session ID required for action[/red]")
            raise typer.Exit(1)
        result = tui.manage_session(session_id, action)
        if "error" in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] {result['message']}")
        return

    if watch:
        tui.watch(session_id)
    else:
        tui.show(session_id)


def deferral_list_cmd() -> None:
    """List all currently deferred tasks (WP-5004)."""
    from thegent_execution.execution import DeferralQueue

    settings = ThegentSettings()
    dq = DeferralQueue(settings.session_dir)
    items = dq.list_deferred()

    if not items:
        console.print("No deferred tasks found.")
        return

    table = Table(title="Deferral Queue")
    table.add_column("Run ID", style="cyan")
    table.add_column("Reason", style="yellow")
    table.add_column("Deferred At", style="dim")
    table.add_column("ETA (UTC)", style="green")

    for i in items:
        table.add_row(i.get("run_id"), i.get("reason", ""), i.get("deferred_at", ""), i.get("eta_utc", ""))

    console.print(table)


def deferral_resume_cmd(run_id: str) -> None:
    """Manually resume a deferred task (WP-5004)."""
    from thegent_execution.execution import DeferralQueue

    settings = ThegentSettings()
    dq = DeferralQueue(settings.session_dir)

    if dq.resume(run_id):
        console.print(f"[bold green]Success:[/bold green] Run [cyan]{run_id}[/cyan] resumed.")
    else:
        console.print(f"[red]Error:[/red] Run [cyan]{run_id}[/cyan] not found in deferral queue.")


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
    "session_contract_negotiate_cmd",
    "session_contract_trend_analysis_cmd",
    "session_contracts_cmd",
    "session_fork_cmd",
    "session_rollback_cmd",
    "status_cmd",
    "stop_cmd",
    "wait_cmd",
]
