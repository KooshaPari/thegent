"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import orjson as json
import typer
from rich.console import Console
from rich.prompt import IntPrompt

from thegent.phench import (
    add_repo,
    bootstrap_target,
    audit_shared_modules,
    create_target_snapshot,
    discover_repos,
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

console = Console()
app = typer.Typer(help="Phench: deterministic project runtime targets and execution.")
target_app = typer.Typer(help="Manage project runtime targets.")
repos_app = typer.Typer(help="Discover and preview sibling repository candidates.")
env_app = typer.Typer(help="Environment preflight commands for targets.")
snapshot_app = typer.Typer(help="Capture and inspect target snapshots.")
app.add_typer(target_app, name="target")
app.add_typer(repos_app, name="repos")
app.add_typer(env_app, name="env")
app.add_typer(snapshot_app, name="snapshot")


@target_app.command("init", help="Create a new target in Phenotype/projects.")
def target_init_cmd(
    name: str = typer.Argument(..., help="Target name."),
    mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
) -> None:
    if mode not in {"repo", "stack"}:
        raise typer.BadParameter("mode must be one of: repo, stack")
    lock = init_target(name, mode=mode)  # type: ignore[arg-type]
    console.print_json(json.dumps({"target": lock.target_name, "mode": lock.mode, "lock_hash": lock.lock_hash}).decode())


@target_app.command("bootstrap", help="Create target and bulk add discovered repos.")
def target_bootstrap_cmd(
    name: str = typer.Argument(..., help="Target name."),
    mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
    source_root: Path | None = typer.Option(
        None,
        "--source-root",
        help="Workspace root containing sibling git checkouts (defaults to sibling repos root).",
    ),
    ref: str = typer.Option("HEAD", "--ref", help="Ref to select for discovered repos."),
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
    repo_ids: list[str] = typer.Option(
        [],
        "--repo-id",
        help="Optional explicit repo IDs to include. Repeat as needed.",
    ),
    auto_lock: bool = typer.Option(True, "--auto-lock/--no-auto-lock", help="Auto-lock after bootstrap."),
) -> None:
    if mode not in {"repo", "stack"}:
        raise typer.BadParameter("mode must be one of: repo, stack")
    lock = bootstrap_target(
        target=name,
        mode=mode,  # type: ignore[arg-type]
        source_root=source_root,
        selected_ref=ref,
        include=include or None,
        exclude=exclude or None,
        repo_ids=repo_ids or None,
        auto_lock=auto_lock,
    )
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "mode": lock.mode,
                "repos": [repo.repo_id for repo in lock.repos],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("import-repos", help="Import discovered repos into an existing target.")
def target_import_repos_cmd(
    name: str = typer.Argument(..., help="Target name."),
    source_root: Path | None = typer.Option(
        None,
        "--source-root",
        help="Workspace root containing sibling git checkouts (defaults to sibling repos root).",
    ),
    ref: str = typer.Option("HEAD", "--ref", help="Ref to select for discovered repos."),
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
    repo_ids: list[str] = typer.Option(
        [],
        "--repo-id",
        help="Optional explicit repo IDs to include. Repeat as needed.",
    ),
    auto_lock: bool = typer.Option(True, "--auto-lock/--no-auto-lock", help="Auto-lock after import."),
) -> None:
    lock = import_repos(
        target=name,
        source_root=source_root,
        selected_ref=ref,
        include=include or None,
        exclude=exclude or None,
        repo_ids=repo_ids or None,
        auto_lock=auto_lock,
    )
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "repos": [repo.repo_id for repo in lock.repos],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("add-repo", help="Add repo+ref selection to a target.")
def target_add_repo_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo: str = typer.Option(..., "--repo", help="Absolute path to repo checkout."),
    ref: str = typer.Option(..., "--ref", help="Selected git ref (branch/tag/sha)."),
    repo_id: str | None = typer.Option(None, "--repo-id", help="Optional stable repo identifier."),
    worktree: str | None = typer.Option(None, "--worktree", help="Optional source worktree path hint."),
) -> None:
    lock = add_repo(name, repo, ref, repo_id=repo_id, worktree_path=worktree)
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "repos": [repo.repo_id for repo in lock.repos],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("set-ref", help="Set selected ref for one repo and relock target.")
def target_set_ref_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo_id: str = typer.Option(..., "--repo-id", help="Repo ID in target lock."),
    ref: str = typer.Option(..., "--ref", help="Git ref (branch/tag/sha)."),
) -> None:
    lock = set_repo_ref(name, repo_id=repo_id, selected_ref=ref)
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "repos": [repo.repo_id for repo in lock.repos],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("lock", help="Resolve selected refs to immutable SHAs.")
def target_lock_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    lock = lock_target(name)
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "lock_hash": lock.lock_hash,
                "repos": [
                    {
                        "repo_id": repo.repo_id,
                        "selected_ref": repo.selected_ref,
                        "resolved_sha": repo.resolved_sha,
                    }
                    for repo in lock.repos
                ],
            }
        ).decode()
    )


@target_app.command("materialize", help="Materialize deterministic checkouts under Phenotype/projects/<target>/repos.")
def target_materialize_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    runtime = materialize_target(name)
    console.print_json(
        json.dumps(
            {
                "target": runtime.target_name,
                "materialized_root": runtime.materialized_root,
                "repos": [asdict(repo) for repo in runtime.repo_materializations],
            }
        ).decode()
    )


@app.command("timeline", help="Show git-first timeline for a target repo.")
def timeline_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target lock."),
    limit: int = typer.Option(30, "--limit", help="Number of recent commits."),
    branch: str | None = typer.Option(None, "--branch", help="Optional branch name to constrain timeline."),
) -> None:
    data = target_timeline(name, repo_id=repo_id, limit=limit, branch=branch)
    console.print_json(json.dumps(data).decode())


@app.command("run", help="Run a task command in a materialized target repo checkout.")
def run_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo_id: str | None = typer.Option(None, "--repo-id", help="Repo ID in target runtime."),
    runner: str | None = typer.Option(None, "--runner", help="Explicit runner override (task|just|make|pnpm|npm|bun)."),
    command: str | None = typer.Option(None, "--command", help="Explicit command/target name for runner."),
    all_repos: bool = typer.Option(False, "--all-repos", help="Run command selection on all repos in target."),
    execution_mode: str = typer.Option("serial", "--mode", help="Execution mode for --all-repos: serial|parallel."),
    env_profile: str | None = typer.Option(None, "--env-profile", help="Optional env profile name."),
) -> None:
    exit_code = run_target(
        name,
        repo_id=repo_id,
        runner=runner,
        command_name=command,
        all_repos=all_repos,
        execution_mode=execution_mode,
        env_profile=env_profile,
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
    payload = {"target": name, "profile": profile or "active", "env": get_env_profile(name, profile=profile)}
    console.print_json(json.dumps(payload).decode())


@app.command("sync", help="Verify and repair dual .phench mirror drift.")
def sync_cmd(
    name: str = typer.Argument(..., help="Target name."),
    prefer: str | None = typer.Option(None, "--prefer", help="Drift resolution source: projects|home."),
) -> None:
    result = sync_target(name, prefer=prefer)
    console.print_json(json.dumps(result).decode())


@snapshot_app.command("create", help="Create a snapshot for a target.")
def snapshot_create_cmd(
    target: str = typer.Argument(..., help="Target name."),
    snapshot_id: str | None = typer.Option(None, "--snapshot-id", help="Optional snapshot identifier."),
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


@app.command("status", help="Show lock/runtime/env status for a target.")
def status_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = target_status(name)
    console.print_json(json.dumps(state).decode())


@app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = audit_shared_modules(name)
    console.print_json(json.dumps(state).decode())


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


@app.command("tui", help="Interactive selector: target -> timeline -> run.")
def tui_cmd() -> None:
    targets = list_targets()
    if not targets:
        raise typer.BadParameter("No targets found under Phenotype/projects. Initialize one with `phench target init`.")

    console.print("Select target:")
    for idx, target in enumerate(targets, start=1):
        console.print(f"{idx}. {target}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    selected_target = targets[target_index - 1]

    timeline = target_timeline(selected_target, limit=20)
    console.print(f"Timeline for [bold]{selected_target}[/bold] ({timeline['repo_id']}):")
    for line in timeline.get("recent", []):
        console.print(f"  {line}")

    code = run_target(selected_target)
    raise typer.Exit(code)
