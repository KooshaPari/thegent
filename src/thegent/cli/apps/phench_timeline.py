"""Phench timeline command."""

from __future__ import annotations

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_timeline_commands(
    app: typer.Typer,
    target_timeline_fn,
) -> None:
    """Register timeline commands on the phench app."""

    @app.command("timeline", help="Show git-first timeline for a target repo.")
    def timeline_cmd(
        name: str = typer.Argument(..., help="Target name."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target lock."),
        limit: int = typer.Option(30, "--limit", help="Number of recent commits."),
        branch: str | None = typer.Option(
            None,
            "--branch",
            help="Optional branch name to constrain timeline.",
        ),
    ) -> None:
        data = target_timeline_fn(name, repo_id=repo_id, limit=limit, branch=branch)
        console.print_json(json.dumps(data).decode())
