"""CLI commands for Teammate delegation and swarm management (WP-16001/2)."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.governance.handoff import HandoffIntegrity
from thegent.governance.teammates import TeammateManager

app = typer.Typer(help="Manage specialized teammate agents and delegation (WP-16001)")
console = Console()
logger = logging.getLogger(__name__)


@app.command("list")
def list_teammates():
    """List all available teammate personas discovered from agents/ directory."""
    settings = ThegentSettings()
    manager = TeammateManager(settings.cache_dir / "teammates.json")
    teammates = manager.list_personas()

    if not teammates:
        console.print("[yellow]No teammates discovered in agents/ directory.[/yellow]")
        return

    table = Table(title="Teammate Persona Registry (WP-16001)")
    table.add_column("ID", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Capabilities", style="yellow")
    table.add_column("Default Model", style="magenta")

    for t in teammates:
        table.add_row(t.id, t.role, ", ".join(t.capabilities), t.default_model)

    console.print(table)


@app.command("delegate")
def delegate_task(
    teammate: str = typer.Argument(..., help="Teammate agent ID"),
    task: str = typer.Argument(..., help="Task description"),
    parent_run_id: str = typer.Option(None, "--parent-run", help="Parent run ID for tracking"),
):
    """Delegate a task to a teammate agent with handoff integrity verification (WP-16002)."""
    settings = ThegentSettings()
    manager = TeammateManager(settings.cache_dir / "teammates.json")

    # 1. WP-16005: Verify handoff integrity
    handoff = HandoffIntegrity(Path.cwd())
    analysis = handoff.analyze_prompt(task)

    if not analysis["is_complete"]:
        console.print("[yellow]Warning: Handoff integrity check flagged potential issues:[/yellow]")
        for f in analysis["findings"]:
            console.print(f"  - {f}")
        if not analysis["referenced_files"]:
            console.print("  - No existing files referenced in prompt. Teammate may lack context.")

        if not typer.confirm("Do you want to proceed anyway?", default=True):
            raise typer.Abort()

    console.print(f"[green]Delegating task to [bold]{teammate}[/bold]...[/green]")

    # 2. Record and trigger delegation
    try:
        parent_id = parent_run_id or "CLI-USER"
        request = manager.delegate(teammate, parent_id, task)

        console.print("[bold green]Delegation Successful![/bold green]")
        console.print(f"Request ID: [cyan]{request.id}[/cyan]")
        console.print(f"Teammate:   [yellow]{teammate}[/yellow]")
        console.print(f"Status:     [blue]{request.status}[/blue]")
        console.print("\nTeammate is now processing in the background (WP-16002).")
    except Exception as e:
        console.print(f"[red]Error during delegation: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def swarm_status(
    run_id: str = typer.Option(None, "--run-id", help="Filter by parent run ID"),
):
    """Monitor the status of the teammate swarm (WP-16002)."""
    settings = ThegentSettings()
    manager = TeammateManager(settings.cache_dir / "teammates.json")
    delegations = manager.get_delegations(run_id)

    if not delegations:
        console.print("[yellow]No active delegations found.[/yellow]")
        return

    table = Table(title="Teammate Swarm Status (WP-16002)")
    table.add_column("Request ID", style="cyan")
    table.add_column("Teammate", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Started", style="magenta")
    table.add_column("Summary", style="white")

    for d in delegations:
        summary = d.result_summary or ""
        if len(summary) > 50:
            summary = summary[:47] + "..."
        table.add_row(
            d.id,
            d.teammate_id,
            d.status,
            d.created_at[11:19], # Just time for compactness
            summary
        )

    console.print(table)


@app.command("show")
def show_delegation(
    req_id: str = typer.Argument(..., help="Request ID to show"),
):
    """Show detailed status and result for a specific delegation."""
    settings = ThegentSettings()
    manager = TeammateManager(settings.cache_dir / "teammates.json")

    delegations = manager.get_delegations()
    req = next((d for d in delegations if d.id == req_id), None)

    if not req:
        console.print(f"[red]Error: Delegation request '{req_id}' not found.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Delegation {req_id}[/bold cyan]")
    console.print(f"Teammate:   [yellow]{req.teammate_id}[/yellow]")
    console.print(f"Parent Run: [blue]{req.parent_run_id}[/blue]")
    console.print(f"Status:     [magenta]{req.status}[/magenta]")
    console.print(f"Created:    {req.created_at}")
    if req.completed_at:
        console.print(f"Completed:  {req.completed_at}")

    console.print("\n[bold]Prompt:[/bold]")
    console.print(req.prompt)

    if req.result_summary:
        console.print("\n[bold]Result Summary:[/bold]")
        console.print(req.result_summary)

    if req.artifact_path:
        console.print(f"\n[bold]Artifact:[/bold] {req.artifact_path}")
