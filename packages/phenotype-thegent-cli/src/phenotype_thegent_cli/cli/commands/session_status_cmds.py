"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer


from phenotype_thegent_cli.cli.commands._cli_shared import (
    ThegentSettings,
    _find_session_meta,
    _is_pid_running,
    _normalize_output_format,
    _read_session_meta,
    _resolve_session_id,
    _resolve_session_status,
    _session_paths,
    console,
    _LOG_FOLLOW_POLL_SECONDS,
)
from phenotype_thegent_cli.cli.commands.session_cmds_helpers import (
    follow_log_stream,
)


"""Session lifecycle management commands.

Commands for session status, inspection, logs, control (stop/pause/resume), and delegation.
Extracted from session_cmds.py to manage module size.
"""


def status_cmd(session_id: str | None = None, format: str | None = None, include_contract: bool = False) -> None:
    settings = ThegentSettings()
    sid = _resolve_session_id(session_id)
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _resolve_session_status(m, p["rc"], running=running)
    out = {
        "session_id": session_id,
        "status": status,
        "running": running,
        "pid": pid,
        "owner": m.get("owner", ""),
        "host": m.get("host"),
        "agent": m.get("agent"),
        "mode": m.get("mode"),
        "cwd": m.get("cwd"),
        "started_at_utc": m.get("started_at_utc"),
        "ended_at_utc": m.get("ended_at_utc"),
        "duration_seconds": m.get("duration_seconds"),
        "timed_out": m.get("timed_out", False),
        "paths": m.get("paths", {}),
    }
    if include_contract:
        out["route_contract"] = m.get("route_contract")
        out["route_request"] = m.get("route_request")
    fmt = _normalize_output_format(format, default="json")
    if fmt == "json":
        sys.stdout.write(json.dumps(out).decode() + "\n")
    else:
        status_text = status
        console.print(f"session_id: {session_id}")
        console.print(f"status: {status_text}")
        console.print(f"owner: {out['owner']}")
        console.print(f"pid: {pid}")
        if out["host"]:
            console.print(f"host: {out['host']}")
        if out["duration_seconds"] is not None:
            console.print(f"duration_seconds: {out['duration_seconds']}")
        if include_contract and out.get("route_contract") is not None:
            console.print("route_contract:")
            console.print_json(data=out["route_contract"])
        if include_contract and out.get("route_request") is not None:
            console.print(f"route_request: {json.dumps(out['route_request']).decode()}")


def inspect_cmd(
    session_ids: list[str] | None = None,
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    from phenotype_thegent_cli.cli.commands.impl import logs_impl, ps_impl, status_impl

    if not session_ids and not owner:
        raise typer.BadParameter("Provide session_ids or --owner")
    if not session_ids and owner:
        rows = ps_impl(owner=owner, all=False)
        session_ids = [r["id"] for r in rows]
    if not session_ids:
        console.print("[dim]No sessions found[/dim]")
        return

    for i, sid in enumerate(session_ids):
        if i > 0:
            console.print()
        console.print(f"[bold]=== {sid} ===[/bold]")
        fmt = _normalize_output_format(format, default="json")
        try:
            st = status_impl(session_id=sid, include_contract=include_contract)
            if fmt == "json":
                if include_contract:
                    console.print_json(data=st)
                else:
                    output = {
                        "session_id": sid,
                        "status": st,
                    }
                    console.print_json(data=output)
            else:
                console.print(st.get("status", ""))
        except Exception as e:
            console.print(f"[red]status error: {e}[/red]")
            continue
        try:
            log_text = logs_impl(session_id=sid, tail=tail, stderr=stderr)
            console.print(log_text)
        except Exception as e:
            console.print(f"[red]logs error: {e}[/red]")


def logs_cmd(
    session_id: str | None = None,
    follow: bool = False,
    stderr: bool = False,
    tail: int = 200,
    timeout: int = 0,
    harness: bool = False,
) -> None:
    settings = ThegentSettings()
    if harness:
        target = Path(settings.harness_root) / "var" / "log" / "harness.log"
        if not target.exists():
            console.print("[yellow]Harness log file not found.[/yellow]")
            return

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-tail:]:
            console.print(line)
        return

    sid = _resolve_session_id(session_id)
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, sid)
    p = _session_paths(meta_path.parent, sid)
    target = p["stderr"] if stderr else p["stdout"]
    if not target.exists():
        if meta_path.parent.name == "discovered":
            console.print(
                "[dim]No log file for this session. Discovered agents (cursor-agent, "
                "claude-code, codex) run in-process; logs are managed by the IDE.[/dim]"
            )
            return
        raise typer.BadParameter(f"Log file missing: {target}")

    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-tail:]:
        console.print(line)
    if not follow:
        return

    follow_log_stream(
        target=target,
        pid=pid,
        timeout=timeout,
        poll_seconds=_LOG_FOLLOW_POLL_SECONDS,
        console=console,
    )


__all__ = [
    "status_cmd",
    "inspect_cmd",
    "logs_cmd",
]
