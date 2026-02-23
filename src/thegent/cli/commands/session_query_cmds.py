"""Thegent CLI session query commands (from session_cmds.py)."""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _default_owner_tag,
    _find_session_meta,
    _is_pid_running,
    _normalize_output_format,
    _read_session_meta,
    _resolve_run_id,
    _resolve_session_id,
    _resolve_session_status,
    _session_paths,
    console,
    _LOG_FOLLOW_POLL_SECONDS,
)
from thegent.cli.commands.session_cmds_helpers import (
    follow_log_stream,
    print_high_session_count_tip,
    render_ps_markdown,
    render_ps_rich_table,
)

__all__ = [
    "events_cmd",
    "feedback_cmd",
    "history_cmd",
    "inspect_cmd",
    "logs_cmd",
    "ps_cmd",
    "status_cmd",
]


def history_cmd(limit: int = 50, format: str | None = None) -> None:
    """List execution run history (sync and background)."""
    from thegent.cli.commands.impl import history_impl

    runs = history_impl(limit=limit)
    if not format or format == "rich":
        if not runs:
            console.print("[dim]No execution history found.[/dim]")
            return

        table = Table(title=f"Execution History (last {limit})")
        table.add_column("Run ID", style="cyan")
        table.add_column("Started (UTC)", style="magenta")
        table.add_column("Agent", style="green")
        table.add_column("Lane", style="dim")
        table.add_column("Conf", justify="right")
        table.add_column("Role", style="italic")
        table.add_column("Status", style="bold")
        table.add_column("Exit", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Prompt Preview", style="dim")

        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "").split("T")[-1][:8]
            agent = run.get("agent", "?")
            lane = run.get("lane", "standard")
            conf = f"{run.get('confidence', 1.0):.2f}" if run.get("confidence") is not None else "—"
            role = run.get("arbitration", "—")
            status = run.get("status", "started")
            status_style = "green" if status == "completed" else "yellow" if status == "started" else "red"
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"

            prompt = run.get("prompt", "")
            prompt_preview = (prompt[:30] + "...") if len(prompt) > 30 else prompt

            table.add_row(
                rid,
                started,
                agent,
                lane,
                conf,
                role,
                f"[{status_style}]{status}[/{status_style}]",
                exit_code,
                duration,
                prompt_preview,
            )
        console.print(table)
    elif format == "json":
        console.print_json(data=runs)
    elif format == "md":
        lines = ["# Execution History", ""]
        lines.append("| Run ID | Started | Agent | Status | Exit | Duration | Prompt |")
        lines.append("|--------|---------|-------|--------|------|----------|--------|")
        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "?")
            agent = run.get("agent", "?")
            status = run.get("status", "?")
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"
            prompt = run.get("prompt", "").replace("\n", " ")
            lines.append(f"| {rid} | {started} | {agent} | {status} | {exit_code} | {duration} | {prompt} |")
        console.print("\n".join(lines))


def events_cmd(run_id: str | None = None, limit: int = 100, format: str | None = None) -> None:
    """List raw telemetry events."""
    from thegent.cli.commands.impl import events_impl

    events = events_impl(run_id=run_id, limit=limit)
    if not format or format == "rich":
        if not events:
            console.print("[dim]No events found.[/dim]")
            return

        table = Table(title="Telemetry Events")
        table.add_column("Run ID", style="cyan")
        table.add_column("Event/Status", style="magenta")
        table.add_column("Timestamp", style="green")
        table.add_column("Payload Details", style="dim")

        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            ts = ts.split("T")[-1][:8]

            details = []
            if event.get("agent"):
                details.append(f"agent={event['agent']}")
            if event.get("exit_code") is not None:
                details.append(f"exit={event['exit_code']}")
            if event.get("duration_s"):
                details.append(f"dur={event['duration_s']:.1f}s")

            table.add_row(rid, ev_type, ts, ", ".join(details))
        console.print(table)
    elif format == "json":
        console.print_json(data=events)
    elif format == "md":
        lines = ["# Telemetry Events", ""]
        lines.append("| Run ID | Event | Timestamp | Details |")
        lines.append("|--------|-------|-----------|---------|")
        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            ev_details = str(event)
            lines.append(f"| {rid} | {ev_type} | {ts} | {ev_details} |")
        console.print("\n".join(lines))


def ps_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    from thegent.cli.commands.session_ops_impl import ps_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    rows = ps_impl(owner=own if not all_sessions else None, all=all_sessions, include_contract=include_contract)
    if not rows:
        console.print("[dim]No sessions.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(rows).decode().decode() + "\n")
        return
    if fmt == "md":
        render_ps_markdown(console=console, rows=rows, include_contract=include_contract)
    else:
        render_ps_rich_table(console=console, rows=rows, include_contract=include_contract)
        print_high_session_count_tip(console=console, rows=rows)


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
        sys.stdout.write(json.dumps(out).decode().decode() + "\n")
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
            console.print(f"route_request: {json.dumps(out['route_request']).decode().decode()}")


def inspect_cmd(
    session_ids: list[str] | None = None,
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    from thegent.cli.commands.impl import logs_impl, status_impl
    from thegent.cli.commands.session_ops_impl import ps_impl

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


def feedback_cmd(run_id: str | None = None, score: float = 1.0, note: str | None = None) -> None:
    """Provide operator feedback for a specific run."""
    from thegent.execution import RunRegistry

    rid = _resolve_run_id(run_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    registry.register_feedback(rid, score, note)
    console.print(f"[green]Feedback recorded for run {rid}.[/green]")
