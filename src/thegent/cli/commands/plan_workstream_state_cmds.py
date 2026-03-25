"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer

from thegent.cli.commands.plan_output_helpers import (
    resolve_output_format,
)

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _resolve_cwd,
    console,
)


"""Workstream and planning-related CLI commands.

Commands for work stream orchestration, planning, and analysis.
Extracted from plan_cmds.py to manage module size.
"""

def plan_incorporate_cmd(cd: Path | None = None, dry_run: bool = False) -> None:
    """Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED."""
    from thegent.cli.commands.work_stream_impl import incorporate_impl

    result = incorporate_impl(cd=cd, dry_run=dry_run)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    merged = result.get("merged", 0)
    if result.get("dry_run"):
        console.print(f"[dim]Dry run: would merge {merged} items from {result.get('sources', [])}[/dim]")
    else:
        console.print(f"[green]Merged {merged} items into docs/reference/WORK_STREAM.md[/green]")


def plan_claim_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Claim an item in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_claim_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_claim_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        if result.get("remediation"):
            console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    console.print(f"[green]Claimed {item_id} for {aid}[/green]")


def plan_complete_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Mark an item as complete in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_complete_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_complete_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Completed {item_id} (agent: {aid})[/green]")


def plan_lint_workstream_cmd(cd: Path | None = None) -> None:
    """Validate canonical WORK_STREAM schema structure."""
    from thegent.utils.workstream_ops import WorkStreamOps

    root = cd or Path.cwd()
    ops = WorkStreamOps(base_dir=root)
    errors = ops.lint_schema()
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print("[green]WORK_STREAM schema is valid.[/green]")


def plan_normalize_workstream_cmd(cd: Path | None = None) -> None:
    """Sort and normalize WL sections and status-line formatting."""
    from thegent.utils.workstream_ops import WorkStreamOps

    root = cd or Path.cwd()
    ops = WorkStreamOps(base_dir=root)
    ops.sort_and_normalize()
    console.print("[green]WORK_STREAM normalized successfully.[/green]")


def plan_verify_workstream_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Verify WORK_STREAM invariants for CLAIMED/COMPLETED overlap by exact ID match."""
    from thegent.planning.work_stream import WorkStreamManager

    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)

    manager = WorkStreamManager(ThegentSettings(), base_dir=cwd)
    result = manager.verify_work_stream_invariants()
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)

    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode() + "\n")
    else:
        counts = result.get("counts", {})
        console.print(
            "[cyan]WORK_STREAM counts:[/cyan] "
            f"CLAIMED={counts.get('claimed', 0)} "
            f"COMPLETED={counts.get('completed', 0)} "
            f"OVERLAP={counts.get('overlap', 0)}"
        )
        if result.get("errors"):
            for error in result["errors"]:
                console.print(f"[red]{error}[/red]")
        else:
            console.print("[green]WORK_STREAM invariants verified.[/green]")

    if not result.get("ok", False):
        raise typer.Exit(1)



__all__ = [
    "plan_incorporate_cmd",
    "plan_claim_cmd",
    "plan_complete_cmd",
    "plan_lint_workstream_cmd",
    "plan_normalize_workstream_cmd",
    "plan_verify_workstream_cmd",
]
