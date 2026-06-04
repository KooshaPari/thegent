"""STUB MODULE - thegent.shell_cli

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def shell_doctor(fix: bool = False) -> None:
    """Run a small shell diagnostic used by compatibility tests."""
    _ = fix
    home = Path.home()
    if not (home / ".zshenv").exists() and not (home / ".zsh_bundle.zsh").exists():
        return
    try:
        result = subprocess.run(["zsh", "-lc", "alias ls"], capture_output=True, text=True, timeout=2, check=False)
    except subprocess.TimeoutExpired:
        console.print("Alias probe timed out: timeout")
        return
    except subprocess.SubprocessError as exc:
        console.print(f"Alias probe unavailable: subprocess error: {exc}")
        return
    except OSError as exc:
        console.print(f"Alias probe unavailable: OS error: {exc}")
        return
    if "tree" in (result.stdout or ""):
        console.print("ls is aliased to tree/recursive output")


def shell_platform() -> None:
    """Print shell platform diagnostics."""
    table = Table(title="Platform Information")
    table.add_column("Key")
    table.add_column("Value")
    try:
        result = subprocess.run(["zsh", "--version"], capture_output=True, text=True, timeout=2, check=False)
        version = (result.stdout or "").strip().split()
        table.add_row("Zsh Version", version[1] if len(version) > 1 else "unknown")
        table.add_row("Zsh Status", "Available")
    except subprocess.TimeoutExpired:
        table.add_row("Zsh Status", "Probe timed out")
    except FileNotFoundError:
        table.add_row("Zsh Status", "Not installed")
    except subprocess.SubprocessError as exc:
        table.add_row("Zsh Status", f"Probe failed ({type(exc).__name__})")
    except OSError as exc:
        table.add_row("Zsh Status", f"Probe failed ({type(exc).__name__})")
    console.print(table)


class ShellApp:
    """Stub shell app."""

    def __init__(self) -> None:
        self._app = typer.Typer()

    def run(self) -> None:
        """Run the shell app."""
        self._app()


shell_app = ShellApp()

__all__ = ["Path", "ShellApp", "Table", "console", "shell_app", "shell_doctor", "shell_platform", "subprocess"]
