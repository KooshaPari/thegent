"""Phench repository discovery commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_repos_commands(
    repos_app: typer.Typer,
    discover_repos_fn,
) -> None:
    """Register repository discovery commands."""

    @repos_app.command("discover", help="Discover git checkouts in sibling workspace roots.")
    def repos_discover_cmd(
        repo_root: Path | None = typer.Option(
            None,
            "--repo-root",
            help="Workspace root to scan. Defaults to THGENT_PHENOTYPE_REPOS_ROOT if unset.",
        ),
        include: list[str] = typer.Option(
            [],
            "--include",
            help="Glob include pattern; repeat for multiple values.",
        ),
        exclude: list[str] = typer.Option(
            [],
            "--exclude",
            help="Glob exclude pattern; repeat for multiple values.",
        ),
    ) -> None:
        repos = discover_repos_fn(root=repo_root, include=include or None, exclude=exclude or None)
        payload = [{"repo_id": item.repo_id, "path": str(item.path)} for item in repos]
        console.print_json(json.dumps(payload).decode())
