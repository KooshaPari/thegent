"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations

from pathlib import Path

import orjson as json
import typer
from rich.console import Console

from thegent.phench import (
    add_repo,
    bootstrap_target,
    audit_shared_modules,
    create_target_snapshot,
    discover_repos,
    load_target_lock,
    import_repos,
    list_target_snapshots,
    set_repo_ref,
    get_env_profile,
    init_target,
    list_targets,
    show_target_snapshot,
    lock_target,
    materialize_target,
    run_env_doctor_for_target,
    run_target,
    set_env_profile,
    sync_target,
    target_status,
    target_timeline,
)
from thegent.cli.apps.phench_projects import register_projects_run
from thegent.cli.apps.phench_observability import register_observability_commands
from thegent.cli.apps.phench_target import register_target_commands

console = Console()
app = typer.Typer(help="Phench: deterministic project runtime targets and execution.")
target_app = typer.Typer(help="Manage project runtime targets.")
repos_app = typer.Typer(help="Discover and preview sibling repository candidates.")
env_app = typer.Typer(help="Environment preflight commands for targets.")
snapshot_app = typer.Typer(help="Capture and inspect target snapshots.")
projects_app = typer.Typer(help="Guided target selection and execution workflows.")
app.add_typer(target_app, name="target")
app.add_typer(repos_app, name="repos")
app.add_typer(env_app, name="env")
app.add_typer(snapshot_app, name="snapshot")
app.add_typer(projects_app, name="projects")


register_target_commands(
    target_app,
    init_target_fn=lambda name, mode="repo": init_target(name, mode=mode),
    bootstrap_target_fn=lambda **kwargs: bootstrap_target(**kwargs),
    import_repos_fn=lambda **kwargs: import_repos(**kwargs),
    add_repo_fn=lambda name, repo, ref, repo_id=None, worktree_path=None: add_repo(
        name, repo, ref, repo_id=repo_id, worktree_path=worktree_path
    ),
    set_repo_ref_fn=lambda name, repo_id, selected_ref: set_repo_ref(
        name, repo_id=repo_id, selected_ref=selected_ref
    ),
    lock_target_fn=lambda name: lock_target(name),
    materialize_target_fn=lambda name: materialize_target(name),
)


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
    data = target_timeline(name, repo_id=repo_id, limit=limit, branch=branch)
    console.print_json(json.dumps(data).decode())


@app.command("run", help="Run a task command in a materialized target repo checkout.")
def run_cmd(
    name: str = typer.Argument(..., help="Target name."),
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

    exit_code = run_target(
        name,
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


@env_app.command("doctor", help="Run fail-fast environment doctor for a materialized target.")
def env_doctor_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    report = run_env_doctor_for_target(name)
    console.print_json(json.dumps(report).decode())
    if report["doctor_status"] != "pass":
        raise typer.Exit(2)


@env_app.command("profile-set", help="Set or replace a named env profile for target run commands.")
def env_profile_set_cmd(
    name: str = typer.Argument(..., help="Target name."),
    profile: str = typer.Option(..., "--profile", help="Profile name."),
    vars: list[str] = typer.Option([], "--var", help="KEY=VALUE pairs; may be repeated."),
) -> None:
    values: dict[str, str] = {}
    for pair in vars:
        if "=" not in pair:
            raise typer.BadParameter("Each --var must be KEY=VALUE")
        key, value = pair.split("=", 1)
        if not key:
            raise typer.BadParameter("Environment variable key cannot be empty")
        values[key] = value
    state = set_env_profile(name, profile, values)
    console.print_json(json.dumps(state).decode())


@env_app.command("profile-show", help="Show active or named env profile for target run commands.")
def env_profile_show_cmd(
    name: str = typer.Argument(..., help="Target name."),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile name."),
) -> None:
    payload = {
        "target": name,
        "profile": profile or "active",
        "env": get_env_profile(name, profile=profile),
    }
    console.print_json(json.dumps(payload).decode())


@app.command("sync", help="Verify and repair dual .phench mirror drift.")
def sync_cmd(
    name: str = typer.Argument(..., help="Target name."),
    prefer: str | None = typer.Option(
        None,
        "--prefer",
        help="Drift resolution source: projects|home.",
    ),
) -> None:
    result = sync_target(name, prefer=prefer)
    console.print_json(json.dumps(result).decode())


@snapshot_app.command("create", help="Create a snapshot for a target.")
def snapshot_create_cmd(
    target: str = typer.Argument(..., help="Target name."),
    snapshot_id: str | None = typer.Option(
        None,
        "--snapshot-id",
        help="Optional snapshot identifier.",
    ),
) -> None:
    result = create_target_snapshot(target, snapshot_id=snapshot_id)
    console.print_json(json.dumps(result).decode())


@snapshot_app.command("list", help="List snapshots for a target.")
def snapshot_list_cmd(target: str = typer.Argument(..., help="Target name.")) -> None:
    snapshots = list_target_snapshots(target)
    console.print_json(json.dumps(snapshots).decode())


@snapshot_app.command("show", help="Show a target snapshot payload.")
def snapshot_show_cmd(
    target: str = typer.Argument(..., help="Target name."),
    snapshot_id: str = typer.Argument(..., help="Snapshot ID."),
) -> None:
    payload = show_target_snapshot(target, snapshot_id)
    console.print_json(json.dumps(payload).decode())


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
    repos = discover_repos(root=repo_root, include=include or None, exclude=exclude or None)
    payload = [{"repo_id": item.repo_id, "path": str(item.path)} for item in repos]
    console.print_json(json.dumps(payload).decode())


register_projects_run(
    projects_app,
    list_targets_fn=lambda: list_targets(),
    load_target_lock_fn=lambda target_name: load_target_lock(target_name),
    target_timeline_fn=lambda name, **kwargs: target_timeline(name, **kwargs),
    lock_target_fn=lambda target_name: lock_target(target_name),
    materialize_target_fn=lambda target_name: materialize_target(target_name),
    run_target_fn=lambda name, **kwargs: run_target(name, **kwargs),
)

register_observability_commands(
    app,
    list_targets_fn=lambda: list_targets(),
    target_timeline_fn=lambda name, **kwargs: target_timeline(name, **kwargs),
    target_status_fn=lambda name: target_status(name),
    run_target_fn=lambda name, **kwargs: run_target(name, **kwargs),
    audit_shared_modules_fn=lambda name: audit_shared_modules(name),
)
