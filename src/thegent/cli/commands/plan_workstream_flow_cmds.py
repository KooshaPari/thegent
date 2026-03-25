"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer

from thegent.cli.commands.plan_output_helpers import (
    render_plan_next_items,
    resolve_output_format,
)

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    console,
)

from thegent.cli.commands.run_cmds import bg_cmd
from thegent.cli.commands.session_cmds import history_cmd


"""Workstream and planning-related CLI commands.

Commands for work stream orchestration, planning, and analysis.
Extracted from plan_cmds.py to manage module size.
"""


def plan_wait_next_cmd(
    cd: Path | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    sources: str | None = None,
    format: str | None = None,
) -> None:
    """Block until next actionable work exists (DAG ready, do_next, escalation, inbox)."""
    from thegent.cli.commands.work_stream_impl import wait_next_impl

    src_tuple = tuple(s.strip() for s in (sources or "dag,do_next,escalation,inbox").split(",") if s.strip())
    result = wait_next_impl(cd=cd, poll_interval=poll, timeout=timeout, sources=src_tuple)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    settings = ThegentSettings()
    fmt = (format or settings.output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode() + "\n")
        return
    if result.get("action") is None:
        console.print("[dim]Timeout: no next action found.[/dim]")
        return
    from rich.panel import Panel

    prompt = result.get("prompt_suggestion", "")
    console.print(
        Panel(
            f"[bold]{result.get('id', '?')}[/bold] ({result.get('source', '')})\n"
            f"{result.get('description', '')}\n\n"
            f"[green]Prompt:[/green] {prompt[:120]}{'...' if len(prompt) > 120 else ''}",
            title=f"Next action ({result.get('elapsed_s', 0):.1f}s)",
            border_style="cyan",
        )
    )
    console.print('[dim]Use: thegent run "<prompt_suggestion>" or thegent free --do-next[/dim]')


def plan_do_next_cmd(cd: Path | None = None, limit: int = 5, format: str | None = None) -> None:
    """Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue."""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=limit)
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)
    if result.get("governance_blocked"):
        if fmt == "json":
            sys.stdout.write(json.dumps(result).decode() + "\n")
        else:
            console.print(f"[red]{result['error']}[/red]")
            if result.get("remediation"):
                console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode() + "\n")
        return
    items = result.get("next_items", [])
    if not items:
        console.print("[dim]No pending items found.[/dim]")
        if result.get("empty_reason"):
            console.print(f"[dim]{result['empty_reason']}[/dim]")
        return
    render_plan_next_items(items, console=console)


def plan_get_next_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)"""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=1)
    fmt = (format or "plain").lower()
    if result.get("governance_blocked"):
        if fmt == "json":
            sys.stdout.write(json.dumps(result).decode() + "\n")
        else:
            typer.echo(result["error"], err=True)
            if result.get("remediation"):
                typer.echo(result["remediation"], err=True)
        raise typer.Exit(1)
    if "error" in result:
        typer.echo(result["error"], err=True)
        raise typer.Exit(1)
    items = result.get("next_items", [])
    if not items:
        raise typer.Exit(1)
    item = items[0]
    if fmt == "json":
        sys.stdout.write(json.dumps(item).decode() + "\n")
    else:
        sys.stdout.write((item.get("prompt_suggestion") or "") + "\n")


def plan_loop_cmd(
    cd: Path | None = None,
    max_iterations: int = typer.Option(0, "--max", "-m", help="Max iterations (0=unbounded)"),
    sleep_seconds: float = typer.Option(5.0, "--sleep", "-s", help="Seconds between iterations"),
    agent: str = typer.Option("free", "--agent", "-a", help="Agent for bg runs (default: free)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print only, do not run"),
) -> None:
    """Loop: get next item -> run bg -> repeat until no items or --max reached."""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    iteration = 0
    while True:
        if max_iterations and iteration >= max_iterations:
            console.print(f"[dim]Reached --max {max_iterations}[/dim]")
            break
        result = do_next_impl(cd=cd, limit=1)
        if "error" in result:
            console.print(f"[red]{result['error']}[/red]")
            raise typer.Exit(1)
        items = result.get("next_items", [])
        if not items:
            console.print("[dim]No more work items.[/dim]")
            break
        prompt = items[0].get("prompt_suggestion", "")
        if not prompt:
            console.print("[yellow]Item has no prompt_suggestion, skipping.[/yellow]")
            iteration += 1
            continue
        item_id = items[0].get("id", "?")
        console.print(f"[cyan]Starting {item_id}:[/cyan] {(prompt[:50] + '...') if len(prompt) > 50 else prompt}")
        if dry_run:
            console.print("[dim](dry-run, not running)[/dim]")
        else:
            bg_cmd(
                prompt=prompt,
                agent=agent,
                cd=Path(cd) if cd else None,
                timeout=300 if agent == "free" else 90,
                model="gpt-5-mini" if agent == "free" else None,
            )
        iteration += 1
        if sleep_seconds > 0 and not dry_run:
            import time

            time.sleep(sleep_seconds)


def plan_progress_cmd(limit: int = 10, format: str | None = None) -> None:
    """Show recent runs (work-package progress). Alias for history --limit N."""
    history_cmd(limit=limit, format=format)


__all__ = [
    "plan_wait_next_cmd",
    "plan_do_next_cmd",
    "plan_get_next_cmd",
    "plan_loop_cmd",
    "plan_progress_cmd",
]
