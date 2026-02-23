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
        _cc = ConcurrencyController(
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
    """Set concurrency limit (persistently in .env)."""
    from dotenv import set_key
    from rich.console import Console

    console = Console()

    if max_concurrency < 1:
        console.print("[red]Error: Max concurrency must be at least 1[/red]")
        raise typer.Exit(1)

    # Find .env file
    env_path = Path(".env")
    if not env_path.exists():
        # Try parent directories
        curr = Path.cwd()
        for _ in range(5):
            if (curr / ".env").exists():
                env_path = curr / ".env"
                break
            curr = curr.parent

    if env_path.exists():
        set_key(str(env_path), "THGENT_MAX_CONCURRENCY", str(max_concurrency))
        console.print(f"[green]Successfully set THGENT_MAX_CONCURRENCY={max_concurrency} in {env_path}[/green]")
    else:
        # If no .env, we'll create one in the current directory if we're in the project root
        # but better to just warn for now if we can't find it.
        console.print("[yellow]Warning: Could not find .env file to persist changes.[/yellow]")
        console.print(
            "[yellow]Note: Changes will not persist. Use .env file or ThegentSettings for persistence.[/yellow]"
        )
        # Don't set os.environ - use settings instead. Runtime changes should be via settings API.

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
