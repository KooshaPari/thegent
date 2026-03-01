"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations

from dataclasses import asdict

import orjson as json
import typer
from rich.console import Console
from rich.prompt import IntPrompt

from thegent.phench import (
    add_repo,
    audit_shared_modules,
    get_env_profile,
    init_target,
    list_targets,
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
env_app = typer.Typer(help="Environment preflight commands for targets.")
app.add_typer(target_app, name="target")
app.add_typer(env_app, name="env")


@target_app.command("init", help="Create a new target in Phenotype/projects.")
def target_init_cmd(
    name: str = typer.Argument(..., help="Target name."),
    mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
) -> None:
    if mode not in {"repo", "stack"}:
        raise typer.BadParameter("mode must be one of: repo, stack")
    lock = init_target(name, mode=mode)  # type: ignore[arg-type]
    console.print_json(json.dumps({"target": lock.target_name, "mode": lock.mode, "lock_hash": lock.lock_hash}).decode())


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
) -> None:
    data = target_timeline(name, repo_id=repo_id, limit=limit)
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


@app.command("status", help="Show lock/runtime/env status for a target.")
def status_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = target_status(name)
    console.print_json(json.dumps(state).decode())


@app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = audit_shared_modules(name)
    console.print_json(json.dumps(state).decode())


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
