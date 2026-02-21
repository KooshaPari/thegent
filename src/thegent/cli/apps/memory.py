"""Memory management CLI commands.

# @trace WL-060
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Memory: agent memory logs, synthesis, and gardening.")


@app.command("garden", help="Run the Gardener Agent: detect and update stale docs.")
def memory_garden(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Detect stale docs and synthesise updates without writing files.",
    ),
    max_age_days: int = typer.Option(
        7,
        "--max-age-days",
        help="Age threshold in days for stale doc detection.",
    ),
    project_root: str = typer.Option(
        ".",
        "--project-root",
        help="Project root directory (defaults to cwd).",
    ),
) -> None:
    """Run a full Gardener Agent cycle.

    Reads memory logs, conversation dumps, and governance events;
    detects stale documentation; synthesises rule-based updates; and
    writes patches back to the relevant docs (unless --dry-run).

    # @trace WL-060
    """
    from thegent.agents.gardener import GardenerAgent

    root = Path(project_root).resolve()
    agent = GardenerAgent(dry_run=dry_run, project_root=root)

    console.print(
        f"[bold cyan]Gardener Agent[/bold cyan] — "
        f"project_root=[dim]{root}[/dim]  "
        f"dry_run=[dim]{dry_run}[/dim]  "
        f"max_age_days=[dim]{max_age_days}[/dim]"
    )

    result = agent.run(max_age_days=max_age_days)

    table = Table(title="Garden Cycle Result")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Docs checked", str(result.docs_checked))
    table.add_row("Docs updated", str(result.docs_updated))
    table.add_row("Dry run", str(result.dry_run))
    console.print(table)

    if result.items_found:
        console.print("\n[bold]Items found:[/bold]")
        for item in result.items_found:
            console.print(f"  [yellow]{item}[/yellow]")
    else:
        console.print("\n[green]No stale documentation detected.[/green]")
