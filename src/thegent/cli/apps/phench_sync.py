"""Phench sync command."""

from __future__ import annotations

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_sync_commands(app: typer.Typer, sync_target_fn) -> None:
    """Register sync command on the phench app."""

    @app.command("sync", help="Verify and repair dual .phench mirror drift.")
    def sync_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        prefer: str | None = typer.Option(
            None,
            "--prefer",
            help="Drift resolution source: projects|home.",
        ),
    ) -> None:
        result = sync_target_fn(name, prefer=prefer, family=family)
        console.print_json(json.dumps(result).decode())
