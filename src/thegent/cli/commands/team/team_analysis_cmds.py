"""Thegent CLI run analysis and explanation commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

import logging

import typer

from rich.table import Table
from rich.panel import Panel

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _resolve_run_id,
    console,
)

_log = logging.getLogger(__name__)


def explain_cmd(run_id: str | None = None) -> None:
    """Show detailed explanation for an agent run (WP-4002)."""
    from thegent.cli.commands.impl import history_impl

    _rid = _resolve_run_id(run_id)
    runs = history_impl(limit=1000)
    run = next((r for r in runs if r.get("run_id") == _rid), None)

    if not run:
        console.print(f"[red]Run ID {_rid} not found.[/red]")
        return

    lines = [
        f"[bold]Run ID:[/bold] {run.get('run_id')}",
        f"[bold]Agent:[/bold] {run.get('agent')}",
        f"[bold]Status:[/bold] {run.get('status')}",
        f"[bold]Exit Code:[/bold] {run.get('exit_code')}",
        f"[bold]Started:[/bold] {run.get('started_at_utc')}",
        f"[bold]Duration:[/bold] {run.get('duration_s', 0) or 0:.2f}s",
        f"[bold]Lane:[/bold] {run.get('lane', 'standard')}",
        f"[bold]Confidence:[/bold] {run.get('confidence', 1.0) or 1.0:.2f}",
        "",
        "[bold]Prompt:[/bold]",
        run.get("prompt", "")[:500] + ("..." if len(run.get("prompt", "")) > 500 else ""),
    ]

    if run.get("error"):
        lines.append(f"\n[red][bold]Error:[/bold] {run.get('error')}[/red]")

    if run.get("policy_result"):
        lines.append(f"\n[bold]Policy:[/bold] {run.get('policy_result')} ({run.get('policy_reason')})")

    panel = Panel("\n".join(lines), title=f"Run Explanation: {_rid}", border_style="blue")
    console.print(panel)


def fallbacks_cmd(run_id: str | None = None) -> None:
    """Show safe fallback options for a failed or blocked run (WP-4003)."""
    run_id = _resolve_run_id(run_id)
    settings = ThegentSettings()
    from thegent.agents.state_machine import FallbackStateMachine
    from thegent.execution import RunRegistry

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=100)
    run = next((r for r in runs if r.get("run_id") == run_id), None)

    if not run:
        console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    fsm = FallbackStateMachine(providers=["cursor", "headless_agent", "interactive_agent"], run_id=run_id)
    fsm.state.policy_issues = ["Dummy violation"] if run.get("status") == "failed" else []
    fsm.state.model = run.get("model")

    suggestions = fsm.suggest_fallbacks()

    if not suggestions:
        console.print("[yellow]No specific fallback suggestions available for this run state.[/yellow]")
        return

    table = Table(title=f"Safe Fallback Options for {run_id}")
    table.add_column("Type", style="bold")
    table.add_column("Suggestion")
    table.add_column("Command (one-click copy)", style="dim")

    for s in suggestions:
        table.add_row(s["type"], s["reason"], s["command"])

    console.print(table)


__all__ = [
    "explain_cmd",
    "fallbacks_cmd",
]
