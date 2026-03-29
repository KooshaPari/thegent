"""Typer command-surface inspection helpers for E2E tests."""

from __future__ import annotations

from collections.abc import Sequence

import click
import typer
from typer.main import get_command

__all__ = ["command_path_exists"]


def command_path_exists(app: typer.Typer, path: Sequence[str]) -> bool:
    """Return whether a command path exists on a Typer app."""
    if not path:
        return True

    current: click.Command = get_command(app)
    for segment in path:
        if not isinstance(current, click.Group):
            return False
        next_command = current.commands.get(segment)
        if next_command is None:
            return False
        current = next_command

    return True
