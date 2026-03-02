"""Phench direct run command."""

from __future__ import annotations

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_run_commands(
    app: typer.Typer,
    run_target_fn,
) -> None:
    """Register direct run command on the phench app."""

    @app.command("run", help="Run a task command in a materialized target repo checkout.")
    def run_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target runtime."),
        runner: str | None = typer.Option(
            None,
            "--runner",
            help="Explicit runner override (task|just|make|pnpm|npm|bun).",
        ),
        command: str | None = typer.Option(
            None,
            "--command",
            help="Explicit command/target name for runner.",
        ),
        ref: str | None = typer.Option(
            None,
            "--ref",
            help="Ref to resolve for this execution (branch/tag/sha).",
        ),
        branch: str | None = typer.Option(None, "--branch", help="Alias for --ref."),
        all_repos: bool = typer.Option(
            False,
            "--all-repos",
            help="Run command selection on all repos in target.",
        ),
        execution_mode: str = typer.Option(
            "serial",
            "--mode",
            help="Execution mode for --all-repos: serial|parallel.",
        ),
        env_profile: str | None = typer.Option(
            None,
            "--env-profile",
            help="Optional env profile name.",
        ),
        no_interactive: bool = typer.Option(
            False,
            "--no-interactive",
            help="Fail if command selection would be interactive.",
        ),
    ) -> None:
        if ref is not None and branch is not None:
            raise typer.BadParameter("--ref and --branch are mutually exclusive")

        exit_code = run_target_fn(
            name,
            family=family,
            repo_id=repo_id,
            runner=runner,
            command_name=command,
            selected_ref=ref or branch,
            all_repos=all_repos,
            execution_mode=execution_mode,
            env_profile=env_profile,
            non_interactive=no_interactive,
        )
        raise typer.Exit(exit_code)
