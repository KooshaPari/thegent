"""CLI implementation for terminal management."""

import sys
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .tools.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes, send_to_tmux_pane

console = Console()
app = typer.Typer(help="Manage terminal sessions and agent interactions")


@app.command("list")
def list_terminals(all: bool = typer.Option(False, "--all", "-a", help="Show all panes, not just Claude Code")):
    """List active terminal panes (tmux)."""
    panes = list_tmux_panes()
    if not panes:
        console.print("[yellow]No tmux panes found.[/yellow]")
        return

    table = Table(title="Active Terminal Panes")
    table.add_column("ID", style="cyan")
    table.add_column("Session:Window.Pane", style="green")
    table.add_column("Path", style="blue")
    table.add_column("Command", style="magenta")
    table.add_column("Type", style="yellow")

    for p in panes:
        is_cc = is_claude_code_pane(p)
        if not all and not is_cc:
            continue

        pane_loc = f"{p.session_name}:{p.window_index}.{p.pane_index}"
        pane_type = "Claude Code" if is_cc else "Generic"
        table.add_row(p.pane_id, pane_loc, p.path, p.command, pane_type)

    console.print(table)


@app.command("inspect")
def inspect_terminal(pane_id: str):
    """View the last few lines of a terminal pane."""
    content = capture_tmux_pane(pane_id)
    if content:
        console.print(f"--- [bold cyan]Pane {pane_id} Content[/bold cyan] ---")
        console.print(content)
    else:
        console.print(f"[red]Could not capture pane {pane_id}[/red]")


@app.command("send")
def send_to_terminal(pane_id: str, text: str):
    """Send a command to a terminal pane."""
    if send_to_tmux_pane(pane_id, text):
        console.print(f"[green]Sent command to {pane_id}[/green]")
    else:
        console.print(f"[red]Failed to send command to {pane_id}[/red]")


@app.command("attach")
def attach_terminal(
    pane_id: str | None = typer.Argument(
        None, help="Pane ID or session:window.pane. If omitted, shows interactive menu."
    ),
):
    """Attach to a terminal session."""
    import os
    import subprocess

    from rich.prompt import Prompt

    panes = list_tmux_panes()
    if not panes:
        console.print("[yellow]No tmux panes found.[/yellow]")
        return

    target_pane = None
    if not pane_id:
        # Interactive selector
        table = Table(title="Select Terminal to Attach")
        table.add_column("#", style="cyan")
        table.add_column("ID", style="green")
        table.add_column("Path", style="blue")
        table.add_column("Command", style="magenta")

        selectable_panes = []
        for i, p in enumerate(panes):
            selectable_panes.append(p)
            table.add_row(str(i + 1), p.pane_id, p.path, p.command)

        console.print(table)
        choice = Prompt.ask("Enter number to attach", choices=[str(i + 1) for i in range(len(panes))])
        target_pane = selectable_panes[int(choice) - 1]
        pane_id = target_pane.pane_id
    else:
        target_pane = next(
            (p for p in panes if pane_id in (p.pane_id, f"{p.session_name}:{p.window_index}.{p.pane_index}")), None
        )

    if not target_pane:
        console.print(f"[red]Pane {pane_id} not found.[/red]")
        return

    session_name = target_pane.session_name
    console.print(f"[bold green]Attaching to tmux session: {session_name}[/bold green]")

    try:
        if "TMUX" in os.environ:
            subprocess.run(["tmux", "switch-client", "-t", pane_id], check=False)
        else:
            subprocess.run(["tmux", "attach-session", "-t", session_name], check=False)
    except Exception as e:
        console.print(f"[red]Error attaching: {e}[/red]")


if __name__ == "__main__":
    app()
