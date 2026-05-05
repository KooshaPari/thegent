"""phench_sync CLI app module."""

from __future__ import annotations

from typing import Any, Callable

import typer


def register_sync_commands(
    app: typer.Typer,
    **kwargs: Any,
) -> None:
    """Register sync commands with the given app."""
    pass


__all__ = ["register_sync_commands"]
