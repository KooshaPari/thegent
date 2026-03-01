"""Thegent CLI summary and teammates commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import logging
import sys
from pathlib import Path

import typer

from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from thegent_cli.cli.commands._cli_shared import (
    ThegentSettings,
    _normalize_output_format,
    console,
)

_log = logging.getLogger(__name__)


def summary_cmd(
    period: str = typer.Argument("today", help="Time period: today, yesterday, week, 7d, 30d, 1h etc."),
    project: Path | None = typer.Option(None, "--project", "-p", help="Project path (default: CWD)"),
    summarize: bool = typer.Option(True, "--summarize/--no-summarize", help="Generate agent summary"),
    agent: str = typer.Option("gemini", "--agent", "-a", help="Agent to use for summary"),
    full: bool = typer.Option(False, "--full", help="Show full audit log"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich, json, md"),
) -> None:
    """FR-X09: Unified summary and audit log across runs, chats, and commits."""
    from thegent_execution.orchestration.state.memory import MemoryCategory, MemorySystem
    from thegent_execution.orchestration.state.session_scraper import SessionScraper
    from thegent_agents.summary import summary_impl

    try:
        project_path = project or Path.cwd()
        scraper = SessionScraper(project_path)
        system = MemorySystem(project_path)
        snapshot_path = scraper.persist_snapshot(trigger="session_change")
        snapshot_index_path = scraper.persist_snapshot_index()
        snapshot_index_md_path = scraper.export_snapshot_index_markdown()

        prompts = scraper.collect_all_recent_prompts()
        recent = system.get_recent(limit=50, category=MemoryCategory.USER_PROMPT)
        recent_contents = {f.content for f in recent}

        for p in prompts:
            if p not in recent_contents:
                system.record(
                    p,
                    MemoryCategory.USER_PROMPT,
                    "auto-scrape",
                    metadata={
                        "scraped": True,
                        "snapshot_path": str(snapshot_path),
                        "snapshot_index_path": str(snapshot_index_path),
                        "snapshot_index_md_path": str(snapshot_index_md_path),
                    },
                )
    except Exception as exc:
        _log.warning("Auto-scrape summary import failed for %s: %s", project, exc)

    result = summary_impl(
        period=period,
        project_path=project,
        summarize=summarize,
        agent=agent,
    )

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode() + "\n")
        return

    if fmt == "md":
        output = result["audit_log"]
        if "summary" in result:
            output += "\n\n# Agent Summary\n\n" + result["summary"]
        sys.stdout.write(output + "\n")
        return

    console.print(f"[bold cyan]Summary for Project:[/bold cyan] {result['project']}")
    console.print(f"[bold cyan]Period:[/bold cyan] {result['period']} ({result['start_dt']} to {result['end_dt']})")

    counts = result["counts"]
    console.print(
        f"[dim]Stats: {counts['runs']} runs, {counts['chats']} chat messages, {counts['commits']} commits[/dim]"
    )
    console.print()

    if "summary" in result:
        console.print(Panel(Markdown(result["summary"]), title="Agent Summary", border_style="green"))
        console.print()

    if full:
        console.print(Markdown(result["audit_log"]))
    else:
        console.print("[dim]Use --full to see the detailed audit log.[/dim]")


def teammates_list_cmd() -> None:
    """WP-16001: List all discovered specialized agents available for delegation."""
    from thegent_audit.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")
    personas = mgr.list_personas()

    table = Table(title="Teammate Persona Registry")
    table.add_column("ID", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Capabilities", style="yellow")
    table.add_column("Priority", style="dim")
    table.add_column("ODD", style="blue")
    table.add_column("Default Model", style="magenta")

    for p in personas:
        table.add_row(p.id, p.role, ", ".join(p.capabilities), str(p.priority), p.odd or "-", p.default_model)

    console.print(table)


def teammates_delegate_cmd(
    teammate_id: str = typer.Argument(..., help="ID of the teammate to delegate to"),
    prompt: str = typer.Argument(..., help="Instruction for the teammate"),
    parent_run_id: str = typer.Option(None, "--parent-run", help="Parent run ID for tracking"),
) -> None:
    """WP-16002: Delegate a sub-task to a specialized teammate."""
    from thegent_audit.governance.handoff import HandoffIntegrity
    from thegent_audit.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")

    personas = mgr.list_personas()
    if not any(p.id == teammate_id for p in personas):
        console.print(f"[bold red]Error:[/bold red] Teammate '{teammate_id}' not found.")
        raise typer.Exit(1)

    handoff = HandoffIntegrity(Path.cwd())
    analysis = handoff.analyze_prompt(prompt)
    if not analysis["is_complete"]:
        console.print("[yellow]Warning: Handoff integrity check flagged potential issues:[/yellow]")
        for f in analysis["findings"]:
            console.print(f"  - {f}")
        if not analysis["referenced_files"]:
            console.print("  - No existing files referenced in prompt. Teammate may lack context.")

        if not typer.confirm("Do you want to proceed anyway?", default=True):
            raise typer.Abort()

    parent_id = parent_run_id or "CLI-USER"
    request = mgr.delegate(teammate_id, parent_id, prompt)

    console.print("[bold green]Delegation Successful![/bold green]")
    console.print(f"Request ID: [cyan]{request.id}[/cyan]")
    console.print(f"Teammate:   [yellow]{teammate_id}[/yellow]")
    console.print(f"Status:     [blue]{request.status}[/blue]")
    console.print("\nTeammate is now processing in the background (heliosShield Phase 11).")


def teammates_status_cmd(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
) -> None:
    """WP-16002: Monitor the status of the teammate swarm."""
    from thegent_audit.governance.teammates import TeammateManager

    settings = ThegentSettings()
    mgr = TeammateManager(settings.cache_dir / "teammates.json")
    delegations = mgr.get_delegations(run_id)

    if not delegations:
        console.print("No active delegations found.")
        return

    table = Table(title="Teammate Swarm Status")
    table.add_column("ID", style="cyan")
    table.add_column("Teammate", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Created At", style="dim")
    table.add_column("Summary", style="green")

    for d in delegations:
        status_style = (
            "bold green"
            if d.status == "completed"
            else "yellow"
            if d.status == "running"
            else "red"
            if d.status == "failed"
            else "white"
        )
        table.add_row(
            d.id, d.teammate_id, f"[{status_style}]{d.status}[/{status_style}]", d.created_at, d.result_summary or ""
        )

    console.print(table)


__all__ = [
    "summary_cmd",
    "teammates_delegate_cmd",
    "teammates_list_cmd",
    "teammates_status_cmd",
]
