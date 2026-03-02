"""Project-oriented phench orchestration commands."""

from __future__ import annotations

from typing import Any, Callable

import typer
from rich.console import Console
from rich.prompt import IntPrompt

from thegent.phench import load_target_lock

console = Console()

TargetResolver = Callable[[], list[str]]
TargetLockLoader = Callable[[str], Any]
TargetTimelineLoader = Callable[..., dict[str, Any]]
TargetAction = Callable[[str], Any]
RunAction = Callable[..., int]


def _ensure_target_name(
    target: str | None,
    *,
    non_interactive: bool,
    list_targets_fn: TargetResolver,
) -> str:
    targets = list_targets_fn()
    if not targets:
        raise typer.BadParameter("No targets found under Phenotype/projects. Initialize one with `phench target init`.")

    if target is not None:
        if target not in targets:
            raise typer.BadParameter(f"Unknown target: {target}")
        return target

    if non_interactive:
        raise typer.BadParameter("--target is required when --no-interactive is set")

    if len(targets) == 1:
        return targets[0]

    console.print("Select target:")
    for idx, value in enumerate(targets, start=1):
        console.print(f"{idx}. {value}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    return targets[target_index - 1]


def _ensure_repo_id(
    selected_target: str,
    lock_repos: list,
    *,
    repo_id: str | None,
    all_repos: bool,
    non_interactive: bool,
) -> str | None:
    if all_repos:
        return None

    repo_ids = [repo.repo_id for repo in lock_repos]
    if not repo_ids:
        raise typer.BadParameter(f"target {selected_target} has no repos")

    if repo_id is not None:
        if repo_id not in repo_ids:
            raise typer.BadParameter(f"repo-id not found in target lock: {repo_id}")
        return repo_id

    if len(repo_ids) == 1:
        return repo_ids[0]

    if non_interactive:
        raise typer.BadParameter("--repo-id is required when --all-repos is false in non-interactive mode")

    console.print("Select repo:")
    for idx, value in enumerate(repo_ids, start=1):
        console.print(f"{idx}. {value}")
    repo_index = IntPrompt.ask("Repository number", default=1)
    if repo_index < 1 or repo_index > len(repo_ids):
        raise typer.BadParameter("Repository selection out of range.")
    return repo_ids[repo_index - 1]


def _ensure_selected_ref(
    selected_target: str,
    selected_repo_id: str,
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

    if no_interactive:
        return None

    timeline = target_timeline_fn(selected_target, repo_id=selected_repo_id, limit=timeline_limit)
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


def _projects_run_impl(
    *,
    target: str | None,
    repo_id: str | None,
    runner: str | None,
    command: str | None,
    ref: str | None,
    branch: str | None,
    all_repos: bool,
    execution_mode: str,
    env_profile: str | None,
    no_interactive: bool,
    no_prepare: bool,
    timeline_limit: int,
    list_targets_fn: TargetResolver,
    load_target_lock_fn: TargetLockLoader,
    target_timeline_fn: TargetTimelineLoader,
    lock_target_fn: TargetAction,
    materialize_target_fn: TargetAction,
    run_target_fn: RunAction,
) -> None:
    if ref is not None and branch is not None:
        raise typer.BadParameter("--ref and --branch are mutually exclusive")

    selected_target = _ensure_target_name(target, non_interactive=no_interactive, list_targets_fn=list_targets_fn)
    lock = load_target_lock_fn(selected_target)
    selected_repo_id = _ensure_repo_id(
        selected_target,
        lock.repos,
        repo_id=repo_id,
        all_repos=all_repos,
        non_interactive=no_interactive,
    )

    selected_ref: str | None = None
    if selected_repo_id is not None:
        selected_ref = _ensure_selected_ref(
            selected_target,
            selected_repo_id,
            ref=ref,
            branch=branch,
            no_interactive=no_interactive,
            timeline_limit=timeline_limit,
            target_timeline_fn=target_timeline_fn,
        )

    if not no_prepare:
        lock_target_fn(selected_target)
        materialize_target_fn(selected_target)

    exit_code = run_target_fn(
        selected_target,
        repo_id=selected_repo_id,
        runner=runner,
        command_name=command,
        selected_ref=selected_ref,
        all_repos=all_repos,
        execution_mode=execution_mode,
        env_profile=env_profile,
        non_interactive=no_interactive,
    )
    raise typer.Exit(exit_code)


def register_projects_run(
    projects_app: typer.Typer,
    *,
    list_targets_fn: TargetResolver,
    load_target_lock_fn: TargetLockLoader | None = None,
    target_timeline_fn: TargetTimelineLoader,
    lock_target_fn: TargetAction,
    materialize_target_fn: TargetAction,
    run_target_fn: RunAction,
) -> None:
    if load_target_lock_fn is None:
        load_target_lock_fn = load_target_lock

    @projects_app.command("run", help="Run through guided target/repo/ref selection.")
    def projects_run_cmd(
        target: str | None = typer.Option(None, "--target", help="Target name to run."),
        repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target lock."),
        runner: str | None = typer.Option(None, "--runner", help="Explicit runner override (task|just|make|pnpm|npm|bun)."),
        command: str | None = typer.Option(None, "--command", help="Explicit command/target name for runner."),
        ref: str | None = typer.Option(None, "--ref", help="Ref to resolve for this execution (branch/tag/sha)."),
        branch: str | None = typer.Option(None, "--branch", help="Alias for --ref."),
        all_repos: bool = typer.Option(False, "--all-repos", help="Run command selection on all repos in target."),
        execution_mode: str = typer.Option("serial", "--mode", help="Execution mode for --all-repos: serial|parallel."),
        env_profile: str | None = typer.Option(None, "--env-profile", help="Optional env profile name."),
        no_interactive: bool = typer.Option(False, "--no-interactive", help="Fail if command selection would be interactive."),
        no_prepare: bool = typer.Option(False, "--no-prepare", help="Skip lock+materialize before run."),
        timeline_limit: int = typer.Option(20, "--timeline-limit", help="Number of refs to show for interactive timeline selection."),
    ) -> None:
        _projects_run_impl(
            target=target,
            repo_id=repo_id,
            runner=runner,
            command=command,
            ref=ref,
            branch=branch,
            all_repos=all_repos,
            execution_mode=execution_mode,
            env_profile=env_profile,
            no_interactive=no_interactive,
            no_prepare=no_prepare,
            timeline_limit=timeline_limit,
            list_targets_fn=list_targets_fn,
            load_target_lock_fn=load_target_lock_fn,
            target_timeline_fn=target_timeline_fn,
            lock_target_fn=lock_target_fn,
            materialize_target_fn=materialize_target_fn,
            run_target_fn=run_target_fn,
        )
