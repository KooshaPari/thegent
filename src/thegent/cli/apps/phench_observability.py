"""Phench diagnostics and observability commands."""

from __future__ import annotations

from typing import Any, Callable

import typer
from rich.console import Console
from rich.prompt import IntPrompt

console = Console()

TargetResolver = Callable[[], list[str]]
TargetTimelineLoader = Callable[..., dict[str, Any]]
TargetStatusLoader = Callable[[str], Any]
RunAction = Callable[..., int]
AuditAction = Callable[[str], dict[str, Any]]


def _ensure_timeline_target(
    *,
    list_targets_fn: TargetResolver,
) -> str:
    targets = list_targets_fn()
    if not targets:
        raise typer.BadParameter(
            "No targets found under Phenotype/projects. Initialize one with `phench target init`."
        )
    if len(targets) == 1:
        return targets[0]
    console.print("Select target:")
    for idx, value in enumerate(targets, start=1):
        console.print(f"{idx}. {value}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    return targets[target_index - 1]


def _extract_repo_id_options(target_status: dict[str, Any]) -> list[str]:
    repos = target_status.get("repos")
    if not isinstance(repos, list):
        raise typer.BadParameter("target status missing repo list")

    repo_ids: list[str] = []
    for raw in repos:
        if not isinstance(raw, dict):
            continue
        repo_id = raw.get("repo_id")
        if isinstance(repo_id, str) and repo_id:
            repo_ids.append(repo_id)
    if not repo_ids:
        raise typer.BadParameter("target status has no repos")
    return repo_ids


def _ensure_tui_repo_id(
    target_status: dict[str, Any],
    *,
    repo_id: str | None,
    no_interactive: bool,
) -> str | None:
    repo_ids = _extract_repo_id_options(target_status)
    if len(repo_ids) == 1 and repo_id is None:
        return repo_ids[0]

    if repo_id is not None:
        if repo_id not in repo_ids:
            raise typer.BadParameter(f"repo-id not found in target status: {repo_id}")
        return repo_id

    if no_interactive:
        raise typer.BadParameter("--repo-id is required when --no-interactive is set")

    console.print("Select repo:")
    for idx, value in enumerate(repo_ids, start=1):
        console.print(f"{idx}. {value}")
    repo_index = IntPrompt.ask("Repository number", default=1)
    if repo_index < 1 or repo_index > len(repo_ids):
        raise typer.BadParameter("Repository selection out of range.")
    return repo_ids[repo_index - 1]


def _ensure_tui_selected_ref(
    target: str,
    repo_id: str | None,
    *,
    ref: str | None,
    branch: str | None,
    no_interactive: bool,
    timeline_limit: int,
    target_timeline_fn: TargetTimelineLoader,
) -> str | None:
    if ref is not None:
        return ref
    if branch is not None:
        return branch

    if no_interactive or repo_id is None:
        return None

    timeline = target_timeline_fn(target, repo_id=repo_id, limit=timeline_limit)
    options: list[tuple[str, str]] = [("HEAD", "HEAD")]
    for branch_name in timeline.get("branches", []):
        if branch_name:
            options.append((branch_name, f"branch: {branch_name}"))
    for tag_name in timeline.get("tags", []):
        if tag_name:
            options.append((tag_name, f"tag: {tag_name}"))
    for line in timeline.get("recent", []):
        if len(options) >= 18:
            break
        head = line.split(maxsplit=1)[0] if isinstance(line, str) else ""
        if not head or head.startswith("("):
            continue
        options.append((head, f"recent commit: {line}"))

    console.print("Select ref:")
    for idx, (_, label) in enumerate(options, start=1):
        console.print(f"{idx}. {label}")
    selected_ref_index = IntPrompt.ask("Ref number", default=1)
    if selected_ref_index < 1 or selected_ref_index > len(options):
        raise typer.BadParameter("Ref selection out of range.")
    return options[selected_ref_index - 1][0]


def register_observability_commands(
    app: typer.Typer,
    *,
    list_targets_fn: TargetResolver,
    target_timeline_fn: TargetTimelineLoader,
    target_status_fn: TargetStatusLoader,
    run_target_fn: RunAction,
    audit_shared_modules_fn: AuditAction,
) -> None:
    @app.command("tui", help="Interactive selector: target/repo/ref -> run.")
    def tui_cmd(
        target: str | None = typer.Option(None, "--target", help="Target name to run."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target status."),
        runner: str | None = typer.Option(None, "--runner", help="Explicit runner override (task|just|make|pnpm|npm|bun)."),
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
        execution_mode: str = typer.Option("serial", "--mode", help="Execution mode for --all-repos: serial|parallel."),
        env_profile: str | None = typer.Option(None, "--env-profile", help="Optional env profile name."),
        no_interactive: bool = typer.Option(
            False,
            "--no-interactive",
            help="Fail if command selection would be interactive.",
        ),
        timeline_limit: int = typer.Option(20, "--timeline-limit", help="Number of refs to show for interactive timeline selection."),
    ) -> None:
        if ref is not None and branch is not None:
            raise typer.BadParameter("--ref and --branch are mutually exclusive")
        if all_repos and (runner is None or command is None):
            raise typer.BadParameter("--all-repos requires --runner and --command")
        if no_interactive and (runner is None or command is None):
            raise typer.BadParameter("--no-interactive requires --runner and --command")

        selected_target = (
            target if target else _ensure_timeline_target(list_targets_fn=list_targets_fn)
        )
        state = target_status_fn(selected_target)
        selected_repo = (
            None
            if all_repos
            else _ensure_tui_repo_id(state, repo_id=repo_id, no_interactive=no_interactive)
        )
        selected_ref = _ensure_tui_selected_ref(
            selected_target,
            selected_repo,
            ref=ref,
            branch=branch,
            no_interactive=no_interactive,
            timeline_limit=timeline_limit,
            target_timeline_fn=target_timeline_fn,
        )
        console.print(f"Timeline for [bold]{selected_target}[/bold]:")
        timeline = target_timeline_fn(selected_target, repo_id=selected_repo, limit=timeline_limit)
        if selected_repo:
            console.print(f"Selected repo: [bold]{selected_repo}[/bold]")
        if not isinstance(timeline.get("recent"), list):
            raise typer.BadParameter("timeline command did not return commit data")
        for line in timeline.get("recent", []):
            console.print(f"  {line}")
        exit_code = run_target_fn(
            selected_target,
            repo_id=selected_repo,
            runner=runner,
            command_name=command,
            selected_ref=selected_ref,
            all_repos=all_repos,
            execution_mode=execution_mode,
            env_profile=env_profile,
            non_interactive=no_interactive,
        )
        raise typer.Exit(exit_code)

    @app.command("status", help="Show lock/runtime/env status for a target.")
    def status_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
        state = target_status_fn(name)
        import orjson as json

        console.print_json(json.dumps(state).decode())

    @app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
    def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
        state = audit_shared_modules_fn(name)
        import orjson as json

        console.print_json(json.dumps(state).decode())
