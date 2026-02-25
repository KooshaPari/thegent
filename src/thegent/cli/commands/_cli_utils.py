"""Common CLI utilities for thegent.

Shared utilities to reduce code duplication across CLI commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def create_table(title: str, *columns: str) -> Table:
    """Create a Rich table with common styling."""
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    return table


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]Success:[/green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """Ask user to confirm an action."""
    from rich.prompt import Confirm
    return Confirm.ask(prompt, default=default)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
