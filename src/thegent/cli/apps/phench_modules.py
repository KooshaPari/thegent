"""Phench module governance commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_modules_commands(
    modules_app: typer.Typer,
    *,
    sync_project_modules_from_repos_fn,
    audit_shared_modules_across_repos_fn,
) -> None:
    """Register module-level orchestration commands for phench."""

    @modules_app.command("sync", help="Sync module manifests from repository-local module roots.")
    def sync_modules_cmd(
        source_root: Path | None = typer.Option(
            None,
            "--source-root",
            help="Root directory containing repository checkouts (defaults to Phenotype repos root).",
        ),
        destination_root: Path | None = typer.Option(
            None,
            "--destination-root",
            help="Destination root for copied module manifests.",
        ),
        include_repos: list[str] | None = typer.Option(
            None,
            "--include-repo",
            help="Repository ID/glob to include (repeatable).",
        ),
        exclude_repos: list[str] | None = typer.Option(
            None,
            "--exclude-repo",
            help="Repository ID/glob to exclude (repeatable).",
        ),
        include_modules: list[str] | None = typer.Option(
            None,
            "--include-module",
            help="Module name to include (repeatable).",
        ),
        exclude_modules: list[str] | None = typer.Option(
            None,
            "--exclude-module",
            help="Module name to exclude (repeatable).",
        ),
        overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing module manifests."),
        dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without writing files."),
    ) -> None:
        state = sync_project_modules_from_repos_fn(
            source_root=source_root,
            destination_root=destination_root,
            include_repos=include_repos,
            exclude_repos=exclude_repos,
            include_modules=include_modules,
            exclude_modules=exclude_modules,
            overwrite=overwrite,
            dry_run=dry_run,
        )
        console.print_json(json.dumps(state).decode())

    @modules_app.command("audit", help="Audit shared modules across sibling repos.")
    def audit_modules_cmd(
        source_root: Path | None = typer.Option(
            None,
            "--source-root",
            help="Root directory containing repository checkouts (defaults to Phenotype repos root).",
        ),
        include_repos: list[str] | None = typer.Option(
            None,
            "--include-repo",
            help="Repository ID/glob to include in scan (repeatable).",
        ),
        exclude_repos: list[str] | None = typer.Option(
            None,
            "--exclude-repo",
            help="Repository ID/glob to exclude from scan (repeatable).",
        ),
        skip_repos: list[str] | None = typer.Option(
            None,
            "--skip-repo",
            help="Repository ID to skip explicitly (repeatable).",
        ),
        min_repo_count: int = typer.Option(2, "--min-repo-count", min=1, help="Minimum repo ownership count."),
        include_modules: list[str] | None = typer.Option(
            None,
            "--include-module",
            help="Module name to include (repeatable).",
        ),
        exclude_modules: list[str] | None = typer.Option(
            None,
            "--exclude-module",
            help="Module name to exclude (repeatable).",
        ),
        include_repo_modules_root: bool = typer.Option(
            True,
            "--include-repo-modules-root/--no-include-repo-modules-root",
            help="Whether to include <repo>/modules directories in scanning.",
        ),
    ) -> None:
        state = audit_shared_modules_across_repos_fn(
            source_root=source_root,
            include_repos=include_repos,
            exclude_repos=exclude_repos,
            skip_repos=skip_repos,
            min_repo_count=min_repo_count,
            include_modules=include_modules,
            exclude_modules=exclude_modules,
            include_repo_modules_root=include_repo_modules_root,
        )
        console.print_json(json.dumps(state).decode())

