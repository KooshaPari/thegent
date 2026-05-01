"""STUB MODULE - thegent.shell_cli

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

import typer


class ShellApp:
    """Stub shell app."""

    def __init__(self) -> None:
        self._app = typer.Typer()

    def run(self) -> None:
        """Run the shell app."""
        self._app()


shell_app = ShellApp()

__all__ = ["ShellApp", "shell_app"]
