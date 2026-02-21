"""thegent queue: Unified Prompt Queue CLI commands (FR-HAX-001).

Subcommands:
  add "<prompt>"  -- enqueue a task
  list            -- show pending items
  next            -- claim and print next item
  done <id>       -- mark item complete
  tui             -- show TUI (list/claim/complete UI)

# @trace FR-HAX-001
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from thegent.core.prompt_queue import PromptQueueManager

console = Console()
app = typer.Typer(name="queue", help="Unified prompt queue (FR-HAX-001).")


def _get_manager(project: str | None = None) -> PromptQueueManager:
    """Resolve and return a PromptQueueManager for the current context."""
    from thegent.core.prompt_queue import PromptQueueManager

    return PromptQueueManager(project_path=project)


@app.command("add")
def queue_add(
    prompt: str = typer.Argument(..., help="Task prompt to enqueue"),
    project: str | None = typer.Option(None, "--project", "-p", help="Project path (defaults to cwd)"),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """Add a task prompt to the queue.

    # @trace FR-HAX-001
    """
    mgr = _get_manager(project)
    item = mgr.enqueue(prompt, project_path=project)

    if output_format == "json":
        console.print_json(data=item.to_dict())
    else:
        console.print(f"[green]Enqueued[/green] id=[cyan]{item.id}[/cyan] prompt=[dim]{prompt[:80]}[/dim]")


@app.command("list")
def queue_list(
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project path"),
    all_items: bool = typer.Option(False, "--all", "-a", help="Include claimed and done items"),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """List pending queue items.

    # @trace FR-HAX-001
    """
    mgr = _get_manager(project)
    items = mgr.list_all(include_done=all_items) if all_items else mgr.list_pending()

    if not items:
        console.print("[dim]No pending items in queue.[/dim]")
        return

    if output_format == "json":
        console.print_json(data=[i.to_dict() for i in items])
        return

    table = Table(title="Prompt Queue", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow")
    table.add_column("Timestamp", style="dim")
    table.add_column("Prompt")
    table.add_column("Project", style="dim")

    for item in items:
        status_style = {"pending": "green", "claimed": "yellow", "done": "dim"}.get(item.status, "white")
        table.add_row(
            item.id,
            f"[{status_style}]{item.status}[/{status_style}]",
            item.timestamp[:19],
            item.prompt[:60] + ("..." if len(item.prompt) > 60 else ""),
            str(Path(item.project_path).name) if item.project_path else "",
        )

    console.print(table)


@app.command("next")
def queue_next(
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project path"),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """Claim and print the next pending queue item.

    Exits with code 1 if the queue is empty.

    # @trace FR-HAX-001
    """
    mgr = _get_manager(project)
    item = mgr.claim()

    if item is None:
        console.print("[dim]Queue is empty — no items to claim.[/dim]")
        raise typer.Exit(1)

    if output_format == "json":
        console.print_json(data=item.to_dict())
    else:
        console.print(f"[bold cyan]Claimed[/bold cyan] id=[green]{item.id}[/green]")
        console.print(item.prompt)


@app.command("done")
def queue_done(
    item_id: str = typer.Argument(..., help="ID of the queue item to mark as complete"),
    output_format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """Mark a queue item as done.

    # @trace FR-HAX-001
    """
    mgr = _get_manager()
    updated = mgr.complete(item_id)

    if not updated:
        console.print(f"[red]Item id={item_id!r} not found in queue.[/red]")
        raise typer.Exit(1)

    if output_format == "json":
        console.print_json(data={"id": item_id, "status": "done"})
    else:
        console.print(f"[green]Done[/green] id=[cyan]{item_id}[/cyan]")


@app.command("tui")
def queue_tui(
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch the queue live"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Refresh interval in seconds for watch mode"),
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project path"),
) -> None:
    """Show the queue in a TUI (list/claim/complete UI).

    # @trace FR-HAX-001
    """
    from thegent.config import ThegentSettings
    from thegent.ux.queue_tui import QueueTUI

    settings = ThegentSettings()
    tui = QueueTUI(settings.session_dir)

    if watch:
        tui.watch(interval=interval)
    else:
        tui.show()
