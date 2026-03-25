"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations

from dataclasses import asdict
from importlib import import_module
from pathlib import Path
from typing import Any

import typer

app = typer.Typer(help="Phench: deterministic project runtime targets and execution.")
target_app = typer.Typer(help="Manage project runtime targets.")
repos_app = typer.Typer(help="Discover and preview sibling repository candidates.")
env_app = typer.Typer(help="Environment preflight commands for targets.")
snapshot_app = typer.Typer(help="Capture and inspect target snapshots.")
modules_app = typer.Typer(help="Manage cross-repo module manifests and shared-module discovery.")
projects_app = typer.Typer(help="Guided target selection and execution workflows.")
app.add_typer(target_app, name="target")
app.add_typer(repos_app, name="repos")
app.add_typer(env_app, name="env")
app.add_typer(snapshot_app, name="snapshot")
app.add_typer(modules_app, name="modules")
app.add_typer(projects_app, name="projects")


def _phench_attr(name: str) -> Any:
    return getattr(import_module("thegent.phench"), name)


@target_app.command("init", help="Create a new target in Phenotype/projects.")
def target_init_cmd(
    name: str = typer.Argument(..., help="Target name."),
    mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
) -> None:
    if mode not in {"repo", "stack"}:
        raise typer.BadParameter("mode must be one of: repo, stack")
    lock = _phench_attr("init_target")(name, mode=mode)
    console.print_json(
        json.dumps({"target": lock.target_name, "mode": lock.mode, "lock_hash": lock.lock_hash}).decode()
    )


@target_app.command("add-repo", help="Add repo+ref selection to a target.")
def target_add_repo_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo: str = typer.Option(..., "--repo", help="Absolute path to repo checkout."),
    ref: str = typer.Option(..., "--ref", help="Selected git ref (branch/tag/sha)."),
    repo_id: str | None = typer.Option(None, "--repo-id", help="Optional stable repo identifier."),
    worktree: str | None = typer.Option(None, "--worktree", help="Optional source worktree path hint."),
) -> None:
    lock = _phench_attr("add_repo")(name, repo, ref, repo_id=repo_id, worktree_path=worktree)
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "repos": [repo.repo_id for repo in lock.repos],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("add-module", help="Add module-selected repos to a target.")
def target_add_module_cmd(
    name: str = typer.Argument(..., help="Target name."),
    module: str = typer.Option(..., "--module", "--mod", help="Module name under Phenotype/projects/modules."),
    selected_ref: str | None = typer.Option(None, "--ref", help="Override selected ref for all module repos."),
    exclude: list[str] = typer.Option([], "--exclude", help="Exact repo IDs to exclude (no glob patterns)."),
) -> None:
    lock = _phench_attr("add_module_to_target")(
        name,
        module_name=module,
        selected_ref=selected_ref,
        exclude_repos={value.strip() for value in exclude if value.strip()},
    )
    console.print_json(
        json.dumps(
            {
                "target": lock.target_name,
                "module": module,
                "repos": [entry.repo_id for entry in lock.repos if entry.module_name == module],
                "lock_hash": lock.lock_hash,
            }
        ).decode()
    )


@target_app.command("lock", help="Resolve selected refs to immutable SHAs.")
def target_lock_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    lock = _phench_attr("lock_target")(name)
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
    runtime = _phench_attr("materialize_target")(name)
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
    data = _phench_attr("target_timeline")(name, repo_id=repo_id, limit=limit)
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
    exit_code = _phench_attr("run_target")(
        name,
        repo_id=repo_id,
        selected_ref=selected_ref,
        family=family,
    ),
    lock_target_fn=lambda name, family=None: lock_target(name, family=family),
    materialize_target_fn=lambda name, family=None: materialize_target(name, family=family),
)

register_timeline_commands(app, target_timeline_fn=_timeline_dispatch)
register_run_commands(app, run_target_fn=_run_dispatch)
register_env_commands(
    env_app,
    run_env_doctor_for_target_fn=_run_env_doctor_dispatch,
    set_env_profile_fn=_set_env_profile_dispatch,
    get_env_profile_fn=_get_env_profile_dispatch,
)
register_sync_commands(app, sync_target_fn=_sync_target_dispatch)
register_snapshot_commands(
    snapshot_app,
    create_target_snapshot_fn=_snapshot_create_dispatch,
    list_target_snapshots_fn=_snapshot_list_dispatch,
    show_target_snapshot_fn=_snapshot_show_dispatch,
)
register_repos_commands(repos_app, discover_repos_fn=_discover_repos_dispatch)
register_modules_commands(
    modules_app,
    sync_project_modules_from_repos_fn=_sync_project_modules_from_repos_dispatch,
    audit_shared_modules_across_repos_fn=_audit_shared_modules_across_repos_dispatch,
)

@env_app.command("doctor", help="Run fail-fast environment doctor for a materialized target.")
def env_doctor_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    report = _phench_attr("run_env_doctor_for_target")(name)
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
    state = _phench_attr("set_env_profile")(name, profile, values)
    console.print_json(json.dumps(state).decode())


@env_app.command("profile-show", help="Show active or named env profile for target run commands.")
def env_profile_show_cmd(
    name: str = typer.Argument(..., help="Target name."),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile name."),
) -> None:
    payload = {
        "target": name,
        "profile": profile or "active",
        "env": _phench_attr("get_env_profile")(name, profile=profile),
    }
    console.print_json(json.dumps(payload).decode())


@app.command("sync", help="Verify and repair dual .phench mirror drift.")
def sync_cmd(
    name: str = typer.Argument(..., help="Target name."),
    prefer: str | None = typer.Option(None, "--prefer", help="Drift resolution source: projects|home."),
) -> None:
    result = _phench_attr("sync_target")(name, prefer=prefer)
    console.print_json(json.dumps(result).decode())


@app.command("status", help="Show lock/runtime/env status for a target.")
def status_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = _phench_attr("target_status")(name)
    console.print_json(json.dumps(state).decode())


@app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = _phench_attr("audit_shared_modules")(name)
    console.print_json(json.dumps(state).decode())


@app.command("scan-shared-repos", help="Audit shared modules across repos in a phenotype workspace.")
def scan_shared_repos_cmd(
    repos_root: str | None = typer.Option(
        None,
        "--repos-root",
        help="Path to the repos workspace. Defaults to $THGENT_PHENOTYPE_ROOT/repos.",
    ),
    repos_root_mode: str = typer.Option(
        "repos",
        "--repos-root-mode",
        help="Select repository selection mode: repos (default) or worktrees.",
    ),
    exclude: list[str] = typer.Option(
        [],
        "--exclude",
        help="Exact repo IDs to exclude from scan (can be repeated).",
    ),
    min_repo_count: int = typer.Option(
        2,
        "--min-repos",
        help="Report modules seen in at least this many repos.",
    ),
    candidate_name_regex: str | None = typer.Option(
        None,
        "--candidate-name-regex",
        help="Optional regex filter for module candidates (applies when candidates are included).",
    ),
    omit_candidates: bool = typer.Option(
        False,
        "--omit-candidates",
        help="Omit module_candidates for faster scans when only recommendations are needed.",
    ),
) -> None:
    if min_repo_count < 2:
        raise typer.BadParameter("min-repos must be >= 2")
    if repos_root_mode not in {"repos", "worktrees"}:
        raise typer.BadParameter("repos-root-mode must be one of: repos, worktrees")

    try:
        state = _phench_attr("scan_shared_modules_across_repos")(
            repos_root=None if repos_root is None else Path(repos_root),
            exclude_repos={value.strip() for value in exclude},
            min_repo_count=min_repo_count,
            repos_root_mode=repos_root_mode,
            candidate_name_regex=candidate_name_regex,
            omit_candidates=omit_candidates,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc))
    console.print_json(json.dumps(state).decode())


@app.command("materialize-module-manifest", help="Materialize a shared-module manifest candidate from scan output.")
def materialize_module_manifest_cmd(
    module: str = typer.Option(..., "--module", help="Shared module name from scan results."),
    repos_root: str | None = typer.Option(
        None,
        "--repos-root",
        help="Path to the repos workspace. Defaults to $THGENT_PHENOTYPE_ROOT/repos.",
    ),
    repos_root_mode: str = typer.Option(
        "repos",
        "--repos-root-mode",
        help="Select repository selection mode: repos (default) or worktrees.",
    ),
    repos: list[str] = typer.Option(
        [],
        "--repo",
        help="Optional explicit repo IDs to pin candidate generation.",
    ),
    min_count: int = typer.Option(
        2,
        "--min-count",
        help="Minimum overlap threshold for shared-module candidates.",
    ),
    output_dir: str | None = typer.Option(
        None,
        "--output-dir",
        help="Directory to persist generated manifest. Defaults to $THGENT_PHENOTYPE_ROOT/projects/modules.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print candidate manifest without writing files."),
    print_snippets: bool = typer.Option(
        False,
        "--print-snippets",
        "--print-target-snippets",
        help="Include shell snippets for creating a module target.",
    ),
) -> None:
    if min_count < 2:
        raise typer.BadParameter("min-count must be >= 2")
    if repos_root_mode not in {"repos", "worktrees"}:
        raise typer.BadParameter("repos-root-mode must be one of: repos, worktrees")

    try:
        payload = _phench_attr("materialize_module_candidate_manifest")(
            module,
            repos_root=None if repos_root is None else Path(repos_root),
            repos_root_mode=repos_root_mode,
            repos=[value.strip() for value in repos if value.strip()],
            min_repo_count=min_count,
            output_dir=None if output_dir is None else Path(output_dir),
            dry_run=dry_run,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc))

    if print_snippets:
        payload["shell_snippets"] = [
            f"thegent phench target init {payload['module_name']} --mode stack",
            f"thegent phench target add-module {payload['module_name']} --module {payload['module_name']}",
        ]
    console.print_json(json.dumps(payload).decode())


@app.command("tui", help="Interactive selector: target -> timeline -> run.")
def tui_cmd() -> None:
    targets = _phench_attr("list_targets")()
    if not targets:
        raise typer.BadParameter("No targets found under Phenotype/projects. Initialize one with `phench target init`.")

    console.print("Select target:")
    for idx, target in enumerate(targets, start=1):
        console.print(f"{idx}. {target}")
    target_index = IntPrompt.ask("Target number", default=1)
    if target_index < 1 or target_index > len(targets):
        raise typer.BadParameter("Target selection out of range.")
    selected_target = targets[target_index - 1]

    timeline = _phench_attr("target_timeline")(selected_target, limit=20)
    console.print(f"Timeline for [bold]{selected_target}[/bold] ({timeline['repo_id']}):")
    for line in timeline.get("recent", []):
        console.print(f"  {line}")

    code = _phench_attr("run_target")(selected_target)
    raise typer.Exit(code)
