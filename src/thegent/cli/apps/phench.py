"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import IntPrompt

from thegent.phench import (
    add_module_to_target,
    add_repo,
    audit_shared_modules,
    audit_shared_modules_across_repos,
    build_module_manifest_payload,
    build_project_execution_matrix,
    create_target_snapshot,
    discover_repos,
    get_env_profile,
    init_target,
    list_modules,
    list_target_snapshots,
    list_targets,
    lock_target,
    materialize_module_candidate_manifest,
    materialize_target,
    run_env_doctor_for_target,
    run_target,
    set_env_profile,
    set_repo_ref,
    show_target_snapshot,
    sync_project_modules_from_repos,
    sync_target,
    target_status,
    target_timeline,
)
from .phench_env import register_env_commands
from .phench_modules import register_modules_commands
from .phench_projects import register_projects_run
from .phench_repos import register_repos_commands
from .phench_run import register_run_commands
from .phench_snapshot import register_snapshot_commands
from .phench_sync import register_sync_commands
from .phench_timeline import register_timeline_commands

console = Console()

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


def _display_lock(lock) -> None:
    payload = {
        "target": lock.target_name,
        "mode": lock.mode,
        "repos": [repo.repo_id for repo in lock.repos],
        "lock_hash": lock.lock_hash,
    }
    console.print_json(data=payload)


@target_app.command("init", help="Create a new target in Phenotype/projects.")
def target_init_cmd(
    name: str = typer.Argument(..., help="Target name."),
    mode: str = typer.Option("repo", "--mode", help="Target mode: repo|stack."),
) -> None:
    if mode not in {"repo", "stack"}:
        raise typer.BadParameter("mode must be one of: repo, stack")
    lock = init_target(name, mode=mode)
    _display_lock(lock)


@target_app.command("add-repo", help="Add repo+ref selection to a target.")
def target_add_repo_cmd(
    name: str = typer.Argument(..., help="Target name."),
    repo: Path = typer.Option(..., "--repo", help="Absolute path to repo checkout."),
    ref: str = typer.Option(..., "--ref", help="Selected git ref (branch/tag/sha)."),
    repo_id: str | None = typer.Option(None, "--repo-id", help="Optional stable repo identifier."),
    worktree: Path | None = typer.Option(None, "--worktree", help="Optional source worktree path hint."),
) -> None:
    lock = add_repo(
        name,
        repo_path=str(repo),
        selected_ref=ref,
        repo_id=repo_id,
        worktree_path=str(worktree) if worktree else None,
    )
    _display_lock(lock)


@target_app.command("add-module", help="Add module-selected repos to a target.")
def target_add_module_cmd(
    name: str = typer.Argument(..., help="Target name."),
    module: str = typer.Option(..., "--module", "--mod", help="Module name under Phenotype/projects/modules."),
    selected_ref: str | None = typer.Option(None, "--ref", help="Override selected ref for all module repos."),
    exclude: list[str] = typer.Option([], "--exclude", help="Exact repo IDs to exclude (no glob patterns)."),
) -> None:
    lock = add_module_to_target(
        name,
        module_name=module,
        selected_ref=selected_ref,
        exclude_repos={value.strip() for value in exclude if value.strip()},
    )
    _display_lock(lock)


@target_app.command("lock", help="Resolve selected refs to immutable SHAs.")
def target_lock_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    lock = lock_target(name)
    _display_lock(lock)


@target_app.command("materialize", help="Materialize deterministic checkouts for a target.")
def target_materialize_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    runtime = materialize_target(name)
    payload = {
        "target": runtime.target_name,
        "materialized_root": runtime.materialized_root,
        "repos": [repo.repo_id for repo in runtime.repo_materializations],
    }
    console.print_json(data=payload)


@app.command("sync", help="Verify and repair dual .phench mirror drift.")
def sync_cmd(
    name: str = typer.Argument(..., help="Target name."),
    prefer: str | None = typer.Option(None, "--prefer", help="Drift resolution source: projects|home."),
) -> None:
    result = sync_target(name, prefer=prefer)
    console.print_json(data=result)


@app.command("status", help="Show lock/runtime/env status for a target.")
def status_cmd(
    name: str = typer.Argument(..., help="Target name."),
) -> None:
    state = target_status(name)
    console.print_json(data=state)


@app.command("audit-shared", help="Audit shared Python modules across repos in a target lock.")
def audit_shared_cmd(name: str = typer.Argument(..., help="Target name.")) -> None:
    state = audit_shared_modules(name)
    console.print_json(data=state)


@app.command("scan-shared-repos", help="Audit shared modules across repos in a phenotype workspace.")
def scan_shared_repos_cmd(
    repos_root: Path | None = typer.Option(
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
    candidates: bool = typer.Option(
        False,
        "--candidates",
        help="Include module_candidates in output (alias to enable explicit candidate materialization suggestions).",
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
    if candidates and omit_candidates:
        raise typer.BadParameter("cannot set both --candidates and --omit-candidates")

    try:
        state = scan_shared_modules_across_repos(
            repos_root=None if repos_root is None else Path(repos_root),
            exclude_repos={value.strip() for value in exclude},
            min_repo_count=min_repo_count,
            repos_root_mode=repos_root_mode,
            candidate_name_regex=candidate_name_regex,
            candidates=candidates,
            omit_candidates=omit_candidates,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc))
    console.print_json(data=state)


@app.command("materialize-module-manifest", help="Materialize a shared-module manifest candidate from scan output.")
def materialize_module_manifest_cmd(
    module: str = typer.Option(..., "--module", help="Shared module name from scan results."),
    repos_root: Path | None = typer.Option(
        None,
        "--repos-root",
        help="Path to the repos workspace. Defaults to $THGENT_PHENOTYPE_ROOT/repos.",
    ),
    repos_root_mode: str = typer.Option(
        "repos",
        "--repos-root-mode",
        help="Select repository selection mode: repos (default) or worktrees.",
    ),
    repos: list[str] = typer.Option([], "--repo", help="Optional explicit repo IDs to pin candidate generation."),
    min_count: int = typer.Option(
        2,
        "--min-count",
        help="Minimum overlap threshold for shared-module candidates.",
    ),
    output_dir: Path | None = typer.Option(
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
        payload = materialize_module_candidate_manifest(
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
        module_name = payload.get("module_name", module)
        payload["shell_snippets"] = [
            f"thegent phench target init {module_name} --mode stack",
            f"thegent phench target add-module {module_name} --module {module_name}",
        ]
    console.print_json(data=payload)


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


register_timeline_commands(app, target_timeline_fn=target_timeline)
register_run_commands(app, run_target_fn=run_target)
register_env_commands(
    env_app,
    run_env_doctor_for_target_fn=run_env_doctor_for_target,
    set_env_profile_fn=set_env_profile,
    get_env_profile_fn=get_env_profile,
)
register_sync_commands(app, sync_target_fn=sync_target)
register_snapshot_commands(
    snapshot_app,
    create_target_snapshot_fn=create_target_snapshot,
    list_target_snapshots_fn=list_target_snapshots,
    show_target_snapshot_fn=show_target_snapshot,
)
register_repos_commands(repos_app, discover_repos_fn=discover_repos)
register_modules_commands(
    modules_app,
    sync_project_modules_from_repos_fn=sync_project_modules_from_repos,
    audit_shared_modules_across_repos_fn=audit_shared_modules_across_repos,
)
register_projects_run(
    projects_app,
    list_targets_fn=list_targets,
    list_modules_fn=list_modules,
    target_timeline_fn=target_timeline,
    target_status_fn=target_status,
    lock_target_fn=lock_target,
    materialize_target_fn=materialize_target,
    run_target_fn=run_target,
    build_matrix_fn=build_project_execution_matrix,
)
