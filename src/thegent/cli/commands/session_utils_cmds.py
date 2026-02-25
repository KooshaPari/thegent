"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys


from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _default_owner_tag,
    _normalize_output_format,
    _resolve_run_id,
    console,
)
from thegent.cli.commands.session_cmds_helpers import (
    parse_sources_csv,
    print_high_session_count_tip,
    render_ps_markdown,
    render_ps_rich_table,
)


"""Session utility and monitoring commands.

Commands for viewing session history, events, monitoring status.
Extracted from session_cmds.py to manage module size.
"""

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


def inbox_list_cmd(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List unified inbox events (run registry + escalation) with optional filters."""
    from thegent.cli.commands.impl import inbox_list_impl

    src_tuple = parse_sources_csv(sources)
    events = inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=src_tuple,
        limit=limit,
    )
    if not format or format == "rich":
        if not events:
            console.print("[dim]No inbox events.[/dim]")
            return
        table = Table(title="Inbox")
        table.add_column("Source", style="dim")
        table.add_column("Event", style="magenta")
        table.add_column("Run ID", style="cyan")
        table.add_column("Owner", style="green")
        table.add_column("Agent", style="yellow")
        table.add_column("Timestamp", style="blue")
        for ev in events:
            ts = (ev.get("timestamp") or "")[:19].replace("T", " ")
            table.add_row(
                ev.get("source", "?"),
                ev.get("event_type", "?"),
                ev.get("run_id", "?")[:12],
                ev.get("owner", "?") or "—",
                ev.get("agent", "?") or "—",
                ts,
            )
        console.print(table)
    elif format == "json":
        console.print_json(data=events)
    else:
        for ev in events:
            console.print(ev)


def inbox_wait_cmd(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    notify: bool = True,
    format: str | None = None,
) -> None:
    """Wait for next inbox event matching filters. Blocks until new event or timeout."""
    from thegent.cli.commands.impl import inbox_wait_impl

    _src_tuple = parse_sources_csv(sources)
    events_result = inbox_wait_impl(
        timeout=int(timeout) if timeout else None,
    )
    events = events_result.get("items", []) if isinstance(events_result, dict) else []
    if not events:
        console.print("[dim]No new events (timeout or empty).[/dim]")
        return
    if not format or format == "rich":
        for ev in events:
            ts = (ev.get("timestamp") or "")[:19].replace("T", " ")
            console.print(
                f"[green]→[/green] {ev.get('source')}/{ev.get('event_type')} "
                f"[cyan]{ev.get('run_id', '?')[:12]}[/cyan] "
                f"owner={ev.get('owner', '—')} agent={ev.get('agent', '—')} {ts}"
            )
    elif format == "json":
        console.print_json(data=events)
    else:
        for ev in events:
            console.print(ev)


def feedback_cmd(run_id: str | None = None, score: float = 1.0, note: str | None = None) -> None:
    """Provide operator feedback for a specific run."""
    rid = _resolve_run_id(run_id)
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    registry.register_feedback(rid, score, note)
    console.print(f"[green]Feedback recorded for run {rid}.[/green]")


def ps_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    from thegent.cli.commands.impl import ps_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    rows = ps_impl(owner=own if not all_sessions else None, all=all_sessions, include_contract=include_contract)
    if not rows:
        console.print("[dim]No sessions.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(rows).decode() + "\n")
        return
    if fmt == "md":
        render_ps_markdown(console=console, rows=rows, include_contract=include_contract)
    else:
        render_ps_rich_table(console=console, rows=rows, include_contract=include_contract)
        print_high_session_count_tip(console=console, rows=rows)


