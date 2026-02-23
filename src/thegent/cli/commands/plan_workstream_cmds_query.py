"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, cast

import typer

from rich.table import Table

from thegent.cli.commands.plan_output_helpers import (
    render_plan_next_items,
    resolve_output_format,
)

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _default_owner_tag,
    _parse_dag_full,
    _resolve_cwd,
    console,
)


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



def workstream_query_cmd(query: str) -> None:
    """Execute SQL query on workstream database."""
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        results = db.execute_query(query)

        if not results:
            console.print("[yellow]No results[/yellow]")
            return

        # Display as table
        table = Table(title="Query Results")
        if results:
            # Use first row keys as columns
            for key in results[0]:
                table.add_column(key, style="cyan")

            for row in results[:100]:  # Limit to 100 rows
                table.add_row(*[str(row.get(k, "")) for k in results[0]])

        console.print(table)
        if len(results) > 100:
            console.print(f"[dim]... and {len(results) - 100} more rows[/dim]")
    except Exception as e:
        console.print(f"[red]Error executing query: {e}[/red]")




