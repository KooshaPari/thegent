"""Phench snapshot commands."""

from __future__ import annotations

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_snapshot_commands(
    snapshot_app: typer.Typer,
    create_target_snapshot_fn,
    list_target_snapshots_fn,
    show_target_snapshot_fn,
) -> None:
    """Register snapshot commands on the phench snapshot sub-app."""

    @snapshot_app.command("create", help="Create a snapshot for a target.")
    def snapshot_create_cmd(
        target: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        snapshot_id: str | None = typer.Option(
            None,
            "--snapshot-id",
            help="Optional snapshot identifier.",
        ),
    ) -> None:
        result = create_target_snapshot_fn(target, family=family, snapshot_id=snapshot_id)
        console.print_json(json.dumps(result).decode())

    @snapshot_app.command("list", help="List snapshots for a target.")
    def snapshot_list_cmd(
        target: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        snapshots = list_target_snapshots_fn(target, family=family)
        console.print_json(json.dumps(snapshots).decode())

    @snapshot_app.command("show", help="Show a target snapshot payload.")
    def snapshot_show_cmd(
        target: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        snapshot_id: str = typer.Argument(..., help="Snapshot ID."),
    ) -> None:
        payload = show_target_snapshot_fn(target, snapshot_id, family=family)
        console.print_json(json.dumps(payload).decode())
