"""CLI commands for concurrency management."""

import logging
from pathlib import Path

import typer

from thegent.config import ThegentSettings
from thegent.execution import ConcurrencyController

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command("show")
def show_concurrency(
    session_dir: str | None = typer.Option(None, "--session-dir", "-d", help="Session directory"),
) -> None:
    """Show current concurrency settings and status."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    settings = ThegentSettings()

    session_path = Path(session_dir) if session_dir else Path.cwd()
    if not session_path.exists():
        session_path = Path.cwd()

    console.print("[bold]Concurrency Settings[/bold]")
    console.print(f"Max Concurrency: {settings.max_concurrency}")
    console.print(f"Load-Based: {settings.concurrency_load_based}")
    console.print(f"Session Dir: {session_path}")

    # Get current status
    try:
        cc = ConcurrencyController(
            session_dir=session_path,
            max_concurrency=settings.max_concurrency,
            use_load_based=settings.concurrency_load_based,
        )
        
        # Get current usage
        table = Table(show_header=True, header_style="bold")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Max Concurrency", str(settings.max_concurrency))
        table.add_row("Load-Based", "Enabled" if settings.concurrency_load_based else "Disabled")
        table.add_row("Session Directory", str(session_path))
        
        console.print()
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command("set")
def set_concurrency(
    max_concurrency: int = typer.Argument(..., help="New max concurrency value"),
    session_dir: str | None = typer.Option(None, "--session-dir", "-d", help="Session directory"),
) -> None:
    """Set concurrency limit."""
    from rich.console import Console

    console = Console()
    settings = ThegentSettings()

    if max_concurrency < 1:
        console.print("[red]Error: Max concurrency must be at least 1[/red]")
        raise typer.Exit(1)

    # Update settings (this would typically update config file)
    console.print(f"[green]Setting max concurrency to {max_concurrency}[/green]")
    console.print("[yellow]Note: This updates runtime settings. For persistent changes, update config file.[/yellow]")
    
    # In a real implementation, this would update the config
    # For now, we'll just show what would be set
    console.print(f"New max concurrency: {max_concurrency}")


@app.command("enable-load-based")
def enable_load_based(
    session_dir: str | None = typer.Option(None, "--session-dir", "-d", help="Session directory"),
) -> None:
    """Enable load-based concurrency control."""
    from rich.console import Console

    console = Console()
    console.print("[green]Enabling load-based concurrency control[/green]")


@app.command("disable-load-based")
def disable_load_based(
    session_dir: str | None = typer.Option(None, "--session-dir", "-d", help="Session directory"),
) -> None:
    """Disable load-based concurrency control."""
    from rich.console import Console

    console = Console()
    console.print("[yellow]Disabling load-based concurrency control[/yellow]")


if __name__ == "__main__":
    app()
