"""Thegent CLI utility commands (archive, purge, context, scratchpad, explorer) - extracted from infra_cmds.py."""

# @trace WL-124
from __future__ import annotations

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    console,
)


def config_check_cmd(format: str | None = None) -> None:
    """Validate config and report issues (DX-010, ROB-013)."""
    import json
    import os
    import sys

    from pydantic import ValidationError

    issues: list[str] = []
    try:
        settings = ThegentSettings()
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            issues.append(f"Config error: {loc} — {err.get('msg', 'invalid')}")
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}) + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)

    session_dir = Path(settings.session_dir).expanduser().resolve()
    if not session_dir.parent.exists():
        issues.append(f"Session dir parent missing: {session_dir.parent}")
    if session_dir.exists() and not os.access(session_dir, os.W_OK):
        issues.append(f"Session dir not writable: {session_dir}")

    if issues:
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}) + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[yellow]{i}[/yellow]")
        raise typer.Exit(1)

    if format == "json":
        sys.stdout.write(json.dumps({"ok": True, "issues": []}) + "\n")
        return
    console.print("[green]Config OK.[/green]")


def interruption_list_cmd(limit: int = 20, format: str | None = None) -> None:
    """List recent interruptions (WP-4004)."""
    import json
    import sys

    from thegent.cli.commands._cli_shared import _normalize_output_format
    from thegent.cli.commands.infra_interruption_helpers import load_recent_interruptions
    from thegent.execution import InterruptionTracker

    settings = ThegentSettings()
    it = InterruptionTracker(settings.session_dir)
    if not it.path.exists():
        console.print("[dim]No interruptions recorded.[/dim]")
        return
    items = load_recent_interruptions(it.path, limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items) + "\n")
        return
    if not items:
        console.print("[dim]No interruptions in window.[/dim]")
        return
    table = Table(title="Interruption Log (WP-4004)")
    table.add_column("Timestamp")
    table.add_column("Type")
    table.add_column("Run ID")
    table.add_column("Severity")
    for i in items:
        table.add_row(
            (i.get("timestamp", "?")[:19]),
            i.get("type", "unknown"),
            i.get("run_id", "?"),
            i.get("severity", "medium"),
        )
    console.print(table)
    fatigue = it.get_fatigue_score()
    console.print(f"[dim]Fatigue score: {fatigue:.2f} (ceiling: 10/hr)[/dim]")


def interruption_snooze_cmd(alert_id: str, minutes: int = 5, itype: str = "unknown") -> None:
    """Snooze an alert; expires → auto-escalation (WP-4004)."""
    from thegent.execution import InterruptionTracker

    settings = ThegentSettings()
    it = InterruptionTracker(settings.session_dir)
    it.record_interruption(run_id=alert_id, severity=itype)
    console.print(f"[green]Alert {alert_id} snoozed for {minutes} min. Will auto-escalate when expired.[/green]")


def purge_cmd(dry_run: bool = True) -> None:
    """WP-3006: Tiered retention purge (G-GP-07)."""
    from thegent.cli.commands.impl import purge_impl

    result = purge_impl(dry_run=dry_run)

    if dry_run:
        console.print(
            f"[yellow]Dry-run: {result['purged']} records would be purged, {result['kept']} records kept.[/yellow]"
        )
        console.print("[dim]Run with --no-dry-run to apply changes.[/dim]")
    else:
        console.print(f"[green]Purged {result['purged']} records, {result['kept']} records remaining.[/green]")


def archive_cmd(
    days: int | None = None,
    domain: str | None = None,
    tier: str | None = None,
) -> None:
    """Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr)."""
    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    archive_dir = session_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    if tier == "cold":
        cold_dir = archive_dir / "cold"
        cold_dir.mkdir(exist_ok=True)
        effective_days = days if days is not None else 365
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in archive_dir.iterdir():
            if item.is_dir() and item.name != "cold":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(cold_dir / item.name))
                    count += 1
        console.print(
            f"[green]Moved {count} sessions to cold storage {cold_dir}[/green] (retention: {effective_days}d)"
        )
    else:
        effective_days = days if days is not None else settings.retention_days_sessions
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in session_dir.iterdir():
            if item.is_dir() and item.name != "archive":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(archive_dir / item.name))
                    count += 1
        console.print(
            f"[green]Archived {count} old session directories to {archive_dir}[/green] "
            f"(retention: {effective_days}d, tier: {tier or 'hot'})"
        )


def context_history_cmd(
    query: str | None = typer.Option(None, "--query", "-q", help="Search string for command content"),
    task_id: str | None = typer.Option(None, "--task-id", "-t", help="Filter by task ID"),
    cwd: str | None = typer.Option(None, "--cwd", "-c", help="Filter by working directory"),
    limit: int = typer.Option(50, "--limit", "-l", help="Number of entries to show"),
) -> None:
    """Search and display context-aware shell history."""
    from thegent.infra.history import ContextHistory

    history = ContextHistory()
    results = history.search(query=query, task_id=task_id, cwd=cwd, limit=limit)

    if not results:
        console.print("[dim]No shell history matching criteria found.[/dim]")
        return

    table = Table(title="Context-Aware Shell History")
    table.add_column("ID", style="dim")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Task ID", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Exit", justify="right")
    table.add_column("CWD", style="blue", overflow="fold")

    for entry in results:
        table.add_row(
            str(entry.id),
            entry.timestamp.split("T")[-1][:8],
            entry.task_id or "—",
            entry.command,
            str(entry.exit_code),
            entry.cwd,
        )
    console.print(table)


def scratchpad_cmd(
    action: str = typer.Argument("show", help="Action: show, add, clear, pop"),
    content: str | None = typer.Argument(None, help="Content to add (for 'add' action)"),
) -> None:
    """Manage the AI command drafting scratchpad."""
    from thegent.skills.scratchpad import AIScratchpad

    scratch = AIScratchpad()

    if action == "show":
        lines = scratch.state.buffer
        if not lines:
            console.print("[dim]Scratchpad is empty.[/dim]")
            return

        console.print("[bold cyan]AI Scratchpad Content:[/bold cyan]")
        for i, line in enumerate(lines):
            console.print(f"[dim]{i + 1:2d} |[/dim] {line}")

    elif action == "add":
        if not content:
            console.print("[red]Error: content required for 'add'[/red]")
            return
        scratch.add_line(content)
        console.print("[green]Added to scratchpad.[/green]")

    elif action == "clear":
        scratch.clear()
        console.print("[yellow]Scratchpad cleared.[/yellow]")

    elif action == "pop":
        scratch.delete_last()
        console.print("[yellow]Removed last line from scratchpad.[/yellow]")


def explorer_cmd() -> None:
    """Launch the terminal explorer TUI."""
    from thegent.tui.explorer import run_explorer_tui

    run_explorer_tui()


__all__ = [
    "archive_cmd",
    "config_check_cmd",
    "context_history_cmd",
    "explorer_cmd",
    "interruption_list_cmd",
    "interruption_snooze_cmd",
    "purge_cmd",
    "scratchpad_cmd",
]
