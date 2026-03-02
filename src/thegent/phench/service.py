from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from datetime import UTC, datetime
import hashlib
import json
import secrets
from typing import Any

from .env_doctor import run_env_doctor
from .discovery import RepoCandidate, discover_local_git_repos
from .git_ops import (
    detect_head_branch,
    list_timeline,
    materialize_repo_checkout,
    resolve_ref_to_sha,
    sanitize_repo_id,
)
from .models import RepoSelection, RuntimeRepo, RuntimeState, RunnerCatalog, TargetLock, TargetMode
from .paths import mirror_target_state_root, projects_root, target_repos_root, target_root, phenotype_repos_root, target_state_root
from .runner import build_runner_catalog, pick_command_interactive, run_command
from .store import dual_write, read_dual, sync_dual, utc_now_iso

LOCK_FILE = "target.lock.json"
RUNTIME_FILE = "runtime.json"
ENV_FILE = "env.snapshot.json"
RUNNER_FILE = "runner.catalog.json"
PROFILE_FILE = "env.profile.json"
SNAPSHOT_DIR = "snapshots"


def _snapshot_id() -> str:
    return f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"


def import_repos(
    target: str,
    source_root: Path | None = None,
    selected_ref: str = "HEAD",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    repo_ids: list[str] | None = None,
    auto_lock: bool = True,
) -> TargetLock:
    """Import discovered repositories into an existing target."""
    repo_root = source_root or phenotype_repos_root()
    candidates = discover_local_git_repos(root=repo_root, include=include, exclude=exclude)
    if not candidates:
        raise ValueError(f"no repos discovered under: {repo_root}")

    by_id = {item.repo_id: item.path for item in candidates}
    if repo_ids:
        selected = []
        for repo_id in repo_ids:
            path = by_id.get(repo_id)
            if not path:
                raise ValueError(f"repo_id not discovered: {repo_id}")
            selected.append(RepoCandidate(repo_id=repo_id, path=path))
    else:
        selected = candidates

    for item in selected:
        add_repo(target, repo_path=str(item.path), selected_ref=selected_ref, repo_id=item.repo_id)

    if auto_lock:
        return lock_target(target)
    return load_target_lock(target)


def create_target_snapshot(target: str, snapshot_id: str | None = None) -> dict[str, Any]:
    lock = load_target_lock(target)
    snapshot_id = snapshot_id or _snapshot_id()
    filename = f"{SNAPSHOT_DIR}/{snapshot_id}.json"

    runtime_payload: dict[str, Any] | None = None
    env_payload: dict[str, Any] | None = None
    runner_payload: dict[str, Any] | None = None

    try:
        runtime_payload = read_dual(target, RUNTIME_FILE)
    except FileNotFoundError:
        runtime_payload = None
    try:
        env_payload = read_dual(target, ENV_FILE)
    except FileNotFoundError:
        env_payload = None
    try:
        runner_payload = read_dual(target, RUNNER_FILE)
    except FileNotFoundError:
        runner_payload = None

    snapshot = {
        "snapshot_id": snapshot_id,
        "created_at_utc": utc_now_iso(),
        "target_name": target,
        "lock": asdict(lock),
        "runtime": runtime_payload,
        "env": env_payload,
        "runner_catalog": runner_payload,
    }
    result = dual_write(target, filename, snapshot)
    return {
        "snapshot_id": snapshot_id,
        "filename": filename,
        "target": target,
        "written_at_utc": snapshot["created_at_utc"],
        **result,
    }


def list_target_snapshots(target: str) -> list[dict[str, Any]]:
    directories = [
        target_state_root(target) / SNAPSHOT_DIR,
        mirror_target_state_root(target) / SNAPSHOT_DIR,
    ]
    snapshots: list[dict[str, Any]] = []
    files: dict[str, Path] = {}
    for directory in directories:
        if not directory.exists():
            continue
        for path in directory.glob("*.json"):
            filename = path.name
            files.setdefault(filename, path)

    for filename in sorted(files):
        rel_filename = f"{SNAPSHOT_DIR}/{filename}"
        try:
            payload = read_dual(target, rel_filename)
        except FileNotFoundError:
            continue
        if not isinstance(payload, dict):
            continue
        snapshots.append(
            {
                "snapshot_id": str(payload.get("snapshot_id", Path(filename).stem)),
                "filename": filename,
                "created_at_utc": str(payload.get("created_at_utc", "")),
                "target_name": str(payload.get("target_name", "")),
                "lock_hash": str((payload.get("lock") or {}).get("lock_hash", "")),
            }
        )
    return snapshots


def show_target_snapshot(target: str, snapshot_id: str) -> dict[str, Any]:
    filename = f"{SNAPSHOT_DIR}/{snapshot_id}.json"
    return read_dual(target, filename)


def discover_repos(
    root: Path | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[RepoCandidate]:
    """Discover available local repositories for bootstrap workflows."""
    return discover_local_git_repos(root=root, include=include, exclude=exclude)


def bootstrap_target(
    target: str,
    mode: TargetMode,
    source_root: Path | None = None,
    selected_ref: str = "HEAD",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    repo_ids: list[str] | None = None,
    auto_lock: bool = True,
) -> TargetLock:
    """Create a target and add discovered repositories from a workspace."""
    if mode not in {"repo", "stack"}:
        raise ValueError("mode must be one of: repo, stack")

    repo_root = source_root or phenotype_repos_root()
    candidates = discover_local_git_repos(root=repo_root, include=include, exclude=exclude)
    if not candidates:
        raise ValueError(f"no repos discovered under: {repo_root}")

    by_id = {item.repo_id: item.path for item in candidates}
    if repo_ids:
        selected = []
        for repo_id in repo_ids:
            path = by_id.get(repo_id)
            if not path:
                raise ValueError(f"repo_id not discovered: {repo_id}")
            selected.append(RepoCandidate(repo_id=repo_id, path=path))
    else:
        selected = candidates

    lock = init_target(target, mode=mode)
    for item in selected:
        add_repo(target, repo_path=str(item.path), selected_ref=selected_ref, repo_id=item.repo_id)
    if auto_lock:
        lock = lock_target(target)
    return lock


def set_repo_ref(target: str, repo_id: str, selected_ref: str) -> TargetLock:
    """Update a single repo selection ref in a target and relock the target."""
    lock = load_target_lock(target)
    updated = False
    for repo in lock.repos:
        if repo.repo_id == repo_id:
            repo.selected_ref = selected_ref
            repo.resolved_sha = None
            updated = True
            break
    if not updated:
        raise ValueError(f"repo_id not in target: {repo_id}")
    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock)
    return lock_target(target)


def _parse_lock(payload: dict[str, Any]) -> TargetLock:
    repos = [RepoSelection(**repo) for repo in payload.get("repos", [])]
    return TargetLock(
        schema_version=int(payload.get("schema_version", 1)),
        target_name=str(payload.get("target_name", "")),
        mode=payload.get("mode", "repo"),
        repos=repos,
        lock_hash=str(payload.get("lock_hash", "")),
        created_at_utc=str(payload.get("created_at_utc", "")),
    )


def _lock_hash(lock: TargetLock) -> str:
    payload = asdict(lock)
    payload["lock_hash"] = ""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def init_target(target: str, mode: TargetMode) -> TargetLock:
    root = target_root(target)
    root.mkdir(parents=True, exist_ok=True)
    (root / "repos").mkdir(parents=True, exist_ok=True)

    lock = TargetLock(
        schema_version=1,
        target_name=target,
        mode=mode,
        repos=[],
        lock_hash="",
        created_at_utc=utc_now_iso(),
    )
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock)
    return lock


def load_target_lock(target: str) -> TargetLock:
    payload = read_dual(target, LOCK_FILE)
    return _parse_lock(payload)


def add_repo(target: str, repo_path: str, selected_ref: str, repo_id: str | None = None, worktree_path: str | None = None) -> TargetLock:
    lock = load_target_lock(target)
    repo = Path(repo_path).expanduser().resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        raise ValueError(f"repo is not a git checkout: {repo}")

    rid = repo_id or sanitize_repo_id(repo.name)
    lock.repos = [entry for entry in lock.repos if entry.repo_id != rid]
    lock.repos.append(
        RepoSelection(
            repo_id=rid,
            repo_path=str(repo),
            selected_ref=selected_ref,
            source_worktree_path=worktree_path,
            resolved_sha=None,
        )
    )
    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock)
    return lock


def lock_target(target: str) -> TargetLock:
    lock = load_target_lock(target)
    if not lock.repos:
        raise ValueError("target has no repos; add at least one repo before lock")

    for repo in lock.repos:
        resolved = resolve_ref_to_sha(Path(repo.repo_path), repo.selected_ref)
        repo.resolved_sha = resolved

    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock)
    return lock


def materialize_target(target: str) -> RuntimeState:
    lock = load_target_lock(target)
    if not lock.repos:
        raise ValueError("target has no repos")

    runtime_repos: list[RuntimeRepo] = []
    repos_root = target_repos_root(target)
    repos_root.mkdir(parents=True, exist_ok=True)

    for repo in lock.repos:
        if not repo.resolved_sha:
            raise ValueError(f"repo {repo.repo_id} is not locked; run target lock first")
        checkout_path = repos_root / repo.repo_id
        materialize_repo_checkout(Path(repo.repo_path), checkout_path, repo.resolved_sha)
        runtime_repos.append(
            RuntimeRepo(
                repo_id=repo.repo_id,
                checkout_path=str(checkout_path),
                resolved_sha=repo.resolved_sha,
                head_branch=detect_head_branch(checkout_path),
            )
        )

    runtime = RuntimeState(
        target_name=target,
        materialized_root=str(target_root(target)),
        repo_materializations=runtime_repos,
        materialized_at_utc=utc_now_iso(),
    )
    dual_write(target, RUNTIME_FILE, runtime)

    report = run_env_doctor(target, [Path(r.checkout_path) for r in runtime_repos])
    dual_write(target, ENV_FILE, report)

    return runtime


def target_status(target: str) -> dict[str, Any]:
    lock = load_target_lock(target)
    runtime_payload: dict[str, Any] | None = None
    env_payload: dict[str, Any] | None = None
    try:
        runtime_payload = read_dual(target, RUNTIME_FILE)
    except FileNotFoundError:
        runtime_payload = None
    try:
        env_payload = read_dual(target, ENV_FILE)
    except FileNotFoundError:
        env_payload = None

    return {
        "target": target,
        "mode": lock.mode,
        "repos": [asdict(r) for r in lock.repos],
        "lock_hash": lock.lock_hash,
        "created_at_utc": lock.created_at_utc,
        "runtime": runtime_payload,
        "env": env_payload,
    }


def target_timeline(
    target: str,
    repo_id: str | None = None,
    limit: int = 30,
    branch: str | None = None,
) -> dict[str, Any]:
    lock = load_target_lock(target)
    if not lock.repos:
        raise ValueError("target has no repos")

    if repo_id:
        chosen = next((repo for repo in lock.repos if repo.repo_id == repo_id), None)
        if not chosen:
            raise ValueError(f"repo_id not found in target: {repo_id}")
    else:
        chosen = lock.repos[0]

    timeline = list_timeline(Path(chosen.repo_path), limit=limit, branch=branch)
    return {
        "target": target,
        "repo_id": chosen.repo_id,
        "repo_path": chosen.repo_path,
        "selected_ref": timeline["selected_ref"],
        "resolved_sha": chosen.resolved_sha,
        **timeline,
    }


def audit_shared_modules(target: str) -> dict[str, Any]:
    lock = load_target_lock(target)
    module_map: dict[str, list[str]] = {}
    for repo in lock.repos:
        src_root = Path(repo.repo_path) / "src"
        if not src_root.exists() or not src_root.is_dir():
            continue
        for child in src_root.iterdir():
            if not child.is_dir():
                continue
            if not (child / "__init__.py").exists():
                continue
            owners = module_map.setdefault(child.name, [])
            owners.append(repo.repo_id)

    shared = {
        module: sorted(set(owners))
        for module, owners in module_map.items()
        if len(set(owners)) >= 2
    }
    return {
        "target": target,
        "shared_modules": shared,
        "repo_count": len(lock.repos),
        "module_count": len(module_map),
    }


def build_catalog(target: str, repo_id: str | None = None) -> RunnerCatalog:
    runtime = read_dual(target, RUNTIME_FILE)
    materializations = runtime.get("repo_materializations")
    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    selected = materializations[0]
    if repo_id:
        selected = next((item for item in materializations if item.get("repo_id") == repo_id), None)
        if not selected:
            raise ValueError(f"repo_id not materialized: {repo_id}")
    checkout = Path(str(selected.get("checkout_path", ""))).resolve()
    catalog = build_runner_catalog(target, checkout)
    dual_write(target, RUNNER_FILE, catalog)
    return catalog


def list_targets() -> list[str]:
    root = projects_root()
    if not root.exists():
        return []
    targets: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if (entry / ".phench" / LOCK_FILE).exists():
            targets.append(entry.name)
    return sorted(targets)


def set_env_profile(target: str, profile: str, values: dict[str, str]) -> dict[str, Any]:
    if not profile.strip():
        raise ValueError("profile name cannot be empty")
    normalized = {str(k): str(v) for k, v in values.items()}
    try:
        state = read_dual(target, PROFILE_FILE)
    except FileNotFoundError:
        state = {"active_profile": profile, "profiles": {}}
    profiles = state.get("profiles")
    if not isinstance(profiles, dict):
        profiles = {}
    profiles[profile] = normalized
    state = {"active_profile": profile, "profiles": profiles}
    dual_write(target, PROFILE_FILE, state)
    return state


def get_env_profile(target: str, profile: str | None = None) -> dict[str, str]:
    try:
        state = read_dual(target, PROFILE_FILE)
    except FileNotFoundError:
        return {}
    profiles = state.get("profiles")
    if not isinstance(profiles, dict):
        return {}
    selected = profile or str(state.get("active_profile", ""))
    payload = profiles.get(selected)
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items()}


def _run_single_repo_target(
    checkout_path: Path,
    catalog: RunnerCatalog,
    runner: str | None,
    command_name: str | None,
    non_interactive: bool = False,
    env_overrides: dict[str, str] | None = None,
) -> int:
    if command_name and not runner:
        raise ValueError("--command requires --runner")
    if non_interactive and (runner is None or command_name is None):
        raise ValueError("--no-interactive requires --runner and --command")
    if runner and command_name:
        return run_command(checkout_path, runner, command_name, env_overrides=env_overrides)

    if runner and not command_name:
        options = [command for command in catalog.commands if command.runner == runner]
        if not options:
            raise ValueError(f"runner has no discovered commands: {runner}")
        return run_command(checkout_path, runner, options[0].name, env_overrides=env_overrides)

    selected = pick_command_interactive(catalog)
    return run_command(checkout_path, selected.runner, selected.name, env_overrides=env_overrides)


def _materialization_entry(item: dict[str, Any]) -> tuple[str, Path]:
    repo_id = item.get("repo_id")
    checkout_path = item.get("checkout_path")
    if not isinstance(repo_id, str) or not repo_id.strip():
        raise ValueError("invalid runtime materialization entry: missing repo_id")
    if not isinstance(checkout_path, str) or not checkout_path.strip():
        raise ValueError(f"invalid runtime materialization entry for {repo_id}: missing checkout_path")
    return repo_id, Path(checkout_path).resolve()


def _materialization_lookup(
    repo_id: str | None,
    materializations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    if repo_id is not None:
        selected = next((item for item in materializations if item.get("repo_id") == repo_id), None)
        if selected is None:
            raise ValueError(f"repo_id not materialized: {repo_id}")
        return [dict(selected)]

    return [dict(item) for item in materializations[:1]]


def run_target(
    target: str,
    repo_id: str | None = None,
    runner: str | None = None,
    command_name: str | None = None,
    selected_ref: str | None = None,
    all_repos: bool = False,
    execution_mode: str = "serial",
    env_profile: str | None = None,
    non_interactive: bool = False,
) -> int:
    report = run_env_doctor_for_target(target)
    if report["doctor_status"] != "pass":
        missing = ", ".join(report["missing_requirements"])
        raise RuntimeError(f"env doctor failed, missing requirements: {missing}")

    if execution_mode not in {"serial", "parallel"}:
        raise ValueError("execution_mode must be one of: serial, parallel")
    if all_repos and (runner is None or command_name is None):
        raise ValueError("--all-repos requires --runner and --command to avoid interactive contention")
    if non_interactive and (runner is None or command_name is None):
        raise ValueError("--no-interactive requires --runner and --command")

    runtime = read_dual(target, RUNTIME_FILE)
    materializations = runtime.get("repo_materializations")
    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    if all_repos:
        selected_items = [dict(item) for item in materializations]
    else:
        selected_items = _materialization_lookup(repo_id, materializations)

    if selected_ref is not None:
        lock = load_target_lock(target)
        lock_index = {repo.repo_id: repo for repo in lock.repos}
        for item in selected_items:
            item_repo_id, item_checkout = _materialization_entry(item)
            lock_repo = lock_index.get(item_repo_id)
            if lock_repo is None:
                raise ValueError(f"repo_id not in target lock: {item_repo_id}")
            resolved = resolve_ref_to_sha(Path(lock_repo.repo_path), selected_ref)
            materialize_repo_checkout(Path(lock_repo.repo_path), item_checkout, resolved)
            item["resolved_sha"] = resolved

    runs: list[tuple[Path, RunnerCatalog]] = []
    env_overrides = get_env_profile(target, profile=env_profile)
    for item in selected_items:
        item_repo_id, item_checkout = _materialization_entry(item)
        catalog = build_runner_catalog(target, item_checkout)
        runs.append((item_checkout, catalog))

    if execution_mode == "parallel" and len(runs) > 1:
        with ThreadPoolExecutor(max_workers=len(runs)) as pool:
            futures = [
                pool.submit(
                    _run_single_repo_target,
                    checkout,
                    catalog,
                    runner,
                    command_name,
                    non_interactive,
                    env_overrides,
                )
                for checkout, catalog in runs
            ]
            results = [future.result() for future in futures]
        nonzero = [code for code in results if code != 0]
        return nonzero[0] if nonzero else 0

    for checkout, catalog in runs:
        code = _run_single_repo_target(
            checkout,
            catalog,
            runner,
            command_name,
            non_interactive,
            env_overrides,
        )
        if code != 0:
            return code
    return 0


def run_env_doctor_for_target(target: str) -> dict[str, Any]:
    runtime = read_dual(target, RUNTIME_FILE)
    materializations = runtime.get("repo_materializations")
    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")
    checkouts = [Path(str(item.get("checkout_path", ""))).resolve() for item in materializations]
    report = run_env_doctor(target, checkouts)
    dual_write(target, ENV_FILE, report)
    return asdict(report)


def sync_target(target: str, prefer: str | None = None) -> dict[str, Any]:
    results = {}
    for filename in (LOCK_FILE, RUNTIME_FILE, ENV_FILE, RUNNER_FILE, PROFILE_FILE):
        try:
            results[filename] = sync_dual(target, filename, prefer=prefer)
        except FileNotFoundError:
            continue
    if not results:
        raise FileNotFoundError("No state files to sync")
    return results
