"""Phench: stable project-state runtime control plane for Phenotype/projects."""

from __future__ import annotations

from typing import Any

import typer

from thegent.phench import (
    add_repo,
    audit_shared_modules,
    bootstrap_target,
    create_target_snapshot,
    build_project_execution_matrix,
    discover_repos,
    get_env_profile,
    init_target,
    import_repos,
    list_target_snapshots,
    list_targets,
    load_target_lock,
    lock_target,
    materialize_target,
    run_env_doctor_for_target,
    run_target,
    set_env_profile,
    set_repo_ref,
    show_target_snapshot,
    sync_target,
    target_status,
    target_timeline,
)
from thegent.cli.apps.phench_env import register_env_commands
from thegent.cli.apps.phench_observability import register_observability_commands
from thegent.cli.apps.phench_projects import register_projects_run
from thegent.cli.apps.phench_repos import register_repos_commands
from thegent.cli.apps.phench_run import register_run_commands
from thegent.cli.apps.phench_snapshot import register_snapshot_commands
from thegent.cli.apps.phench_sync import register_sync_commands
from thegent.cli.apps.phench_target import register_target_commands
from thegent.cli.apps.phench_timeline import register_timeline_commands

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


def _timeline_dispatch(name: str, **kwargs: Any) -> dict[str, Any]:
    return target_timeline(name, **kwargs)


def _run_dispatch(name: str, **kwargs: Any) -> int:
    return run_target(name, **kwargs)


def _run_env_doctor_dispatch(name: str, family: str | None = None) -> dict[str, Any]:
    return run_env_doctor_for_target(name, family=family)


def _build_matrix_dispatch(
    name: str,
    **kwargs: Any,
) -> dict[str, Any]:
    return build_project_execution_matrix(name, **kwargs)


def _set_env_profile_dispatch(name: str, profile: str, vars: dict[str, str], family: str | None = None) -> dict[str, Any]:
    return set_env_profile(name, profile, vars, family=family)


def _get_env_profile_dispatch(
    name: str,
    profile: str | None = None,
    family: str | None = None,
) -> dict[str, str]:
    return get_env_profile(name, profile=profile, family=family)


def _sync_target_dispatch(name: str, **kwargs: Any) -> dict[str, Any]:
    return sync_target(name, **kwargs)


def _discover_repos_dispatch(
    root: Any = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Any]:
    return discover_repos(root=root, include=include, exclude=exclude)


def _snapshot_create_dispatch(
    target: str,
    family: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return create_target_snapshot(target, family=family, **kwargs)


def _snapshot_list_dispatch(target: str, family: str | None = None) -> list[dict[str, Any]]:
    return list_target_snapshots(target, family=family)


def _snapshot_show_dispatch(
    target: str, snapshot_id: str, family: str | None = None
) -> dict[str, Any]:
    return show_target_snapshot(target, snapshot_id, family=family)


register_target_commands(
    target_app,
    init_target_fn=lambda name, mode="repo", family=None: init_target(name, mode=mode, family=family),
    bootstrap_target_fn=lambda **kwargs: bootstrap_target(**kwargs),
    import_repos_fn=lambda **kwargs: import_repos(**kwargs),
    add_repo_fn=lambda name, repo, ref, family=None, **kwargs: add_repo(
        name,
        family=family,
        repo_path=repo,
        selected_ref=ref,
        **kwargs,
    ),
    set_repo_ref_fn=lambda name, repo_id, selected_ref, family=None: set_repo_ref(
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

register_projects_run(
    projects_app,
    list_targets_fn=lambda family=None: list_targets(family=family),
    load_target_lock_fn=lambda target_name, family=None: load_target_lock(
        target_name,
        family=family,
    ),
    target_timeline_fn=lambda name, **kwargs: target_timeline(name, **kwargs),
    target_status_fn=lambda name, family=None: target_status(name, family=family),
    lock_target_fn=lambda target_name, family=None: lock_target(target_name, family=family),
    materialize_target_fn=lambda target_name, family=None: materialize_target(target_name, family=family),
    run_target_fn=lambda name, **kwargs: run_target(name, **kwargs),
    build_matrix_fn=_build_matrix_dispatch,
)

register_observability_commands(
    app,
    list_targets_fn=lambda family=None: list_targets(family=family),
    target_timeline_fn=lambda name, **kwargs: target_timeline(name, **kwargs),
    target_status_fn=lambda name, family=None: target_status(name, family=family),
    run_target_fn=lambda name, **kwargs: run_target(name, **kwargs),
    audit_shared_modules_fn=lambda name, family=None: audit_shared_modules(name, family=family),
)
