from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from fnmatch import fnmatch
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
from .paths import (
    mirror_target_state_root,
    projects_root,
    projects_modules_root,
    phenotype_root,
    module_manifest_path,
    target_repos_root,
    target_root,
    validate_family_name,
    phenotype_repos_root,
    target_state_root,
)
from .runner import build_runner_catalog, pick_command_interactive, run_command
from .store import dual_write, read_dual, sync_dual, utc_now_iso

LOCK_FILE = "target.lock.json"
RUNTIME_FILE = "runtime.json"
ENV_FILE = "env.snapshot.json"
RUNNER_FILE = "runner.catalog.json"
PROFILE_FILE = "env.profile.json"
SNAPSHOT_DIR = "snapshots"
SUPPORTED_MODULE_MANIFEST_SCHEMA_VERSIONS = {1}


def _resolve_module_manifest_path(module: str) -> Path:
    normalized_module = module.strip()
    if not normalized_module:
        raise ValueError("module manifest not found: <empty>")

    is_path_like = ("/" in normalized_module) or ("\\" in normalized_module)
    candidates: list[Path] = []

    def _add(path: Path) -> None:
        manifest_path = path if path.name == "manifest.json" else path / "manifest.json"
        if manifest_path not in candidates:
            candidates.append(manifest_path)

    if is_path_like:
        explicit_path = Path(normalized_module).expanduser()
        _add(explicit_path)
        if not explicit_path.is_absolute():
            _add(phenotype_root() / explicit_path)

        if explicit_path.is_absolute() and explicit_path.exists():
            if explicit_path.is_file() and explicit_path.name == "manifest.json":
                return explicit_path
            if explicit_path.is_dir() and (explicit_path / "manifest.json").exists():
                return explicit_path / "manifest.json"

        normalized_parts = [part.lower() for part in explicit_path.as_posix().split("/")]
        if "modules" in normalized_parts:
            modules_index = normalized_parts.index("modules")
            if modules_index + 1 < len(normalized_parts):
                _add(projects_modules_root() / normalized_parts[modules_index + 1])
        else:
            _add(projects_modules_root() / explicit_path.name)

        for candidate in candidates:
            if candidate.exists():
                return candidate
    else:
        module_name = validate_family_name(normalized_module)
        module_path = module_manifest_path(module_name)
        _add(module_path)
        if module_path.exists():
            return module_path

    raise ValueError(f"module manifest not found: {module}")


def _snapshot_id() -> str:
    return f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"


def _stable_payload_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def import_repos(
    target: str,
    family: str | None = None,
    source_root: Path | None = None,
    selected_ref: str = "HEAD",
    preferred_runner: str | None = None,
    preferred_command: str | None = None,
    preferred_ref: str | None = None,
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
        add_repo(
            target,
            family=family,
            repo_path=str(item.path),
            selected_ref=selected_ref,
            repo_id=item.repo_id,
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
        )

    if auto_lock:
        return lock_target(target, family=family)
    return load_target_lock(target, family=family)


def create_target_snapshot(
    target: str,
    family: str | None = None,
    snapshot_id: str | None = None,
) -> dict[str, Any]:
    lock = load_target_lock(target, family=family)
    snapshot_id = snapshot_id or _snapshot_id()
    filename = f"{SNAPSHOT_DIR}/{snapshot_id}.json"

    runtime_payload: dict[str, Any] | None = None
    env_payload: dict[str, Any] | None = None
    runner_payload: dict[str, Any] | None = None

    try:
        runtime_payload = read_dual(target, RUNTIME_FILE, family=family)
    except FileNotFoundError:
        runtime_payload = None
    try:
        env_payload = read_dual(target, ENV_FILE, family=family)
    except FileNotFoundError:
        env_payload = None
    try:
        runner_payload = read_dual(target, RUNNER_FILE, family=family)
    except FileNotFoundError:
        runner_payload = None

    snapshot = {
        "snapshot_id": snapshot_id,
        "created_at_utc": utc_now_iso(),
        "target_name": target,
        "lock": asdict(lock),
        "lock_hash": lock.lock_hash,
        "runtime": runtime_payload,
        "env": env_payload,
        "runner_catalog": runner_payload,
    }
    snapshot["runtime_hash"] = _stable_payload_hash(runtime_payload) if isinstance(runtime_payload, dict) else ""
    snapshot["env_hash"] = _stable_payload_hash(env_payload) if isinstance(env_payload, dict) else ""
    snapshot["runner_catalog_hash"] = (
        _stable_payload_hash(runner_payload) if isinstance(runner_payload, dict) else ""
    )
    snapshot["snapshot_hash"] = _stable_payload_hash({k: snapshot[k] for k in snapshot if k != "snapshot_hash"})
    result = dual_write(target, filename, snapshot, family=family)
    return {
        "snapshot_id": snapshot_id,
        "filename": filename,
        "target": target,
        "written_at_utc": snapshot["created_at_utc"],
        **result,
    }


def list_target_snapshots(target: str, family: str | None = None) -> list[dict[str, Any]]:
    directories = [
        target_state_root(target, family=family) / SNAPSHOT_DIR,
        mirror_target_state_root(target, family=family) / SNAPSHOT_DIR,
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
            payload = read_dual(target, rel_filename, family=family)
        except FileNotFoundError:
            continue
        if not isinstance(payload, dict):
            continue
        snapshots.append(
            {
                "snapshot_id": str(payload.get("snapshot_id", Path(filename).stem)),
                "filename": rel_filename,
                "created_at_utc": str(payload.get("created_at_utc", "")),
                "target_name": str(payload.get("target_name", "")),
                "lock_hash": str((payload.get("lock") or {}).get("lock_hash", "")),
                "runtime_hash": str(payload.get("runtime_hash", "")),
                "snapshot_hash": str(payload.get("snapshot_hash", "")),
            }
        )
    return snapshots


def show_target_snapshot(target: str, snapshot_id: str, family: str | None = None) -> dict[str, Any]:
    filename = f"{SNAPSHOT_DIR}/{snapshot_id}.json"
    return read_dual(target, filename, family=family)


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
    family: str | None = None,
    source_root: Path | None = None,
    selected_ref: str = "HEAD",
    preferred_runner: str | None = None,
    preferred_command: str | None = None,
    preferred_ref: str | None = None,
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

    lock = init_target(target, mode=mode, family=family)
    for item in selected:
        add_repo(
            target,
            family=family,
            repo_path=str(item.path),
            selected_ref=selected_ref,
            repo_id=item.repo_id,
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
        )
    if auto_lock:
        lock = lock_target(target, family=family)
    return lock


def set_repo_ref(
    target: str,
    repo_id: str,
    selected_ref: str,
    family: str | None = None,
) -> TargetLock:
    """Update a single repo selection ref in a target and relock the target."""
    lock = load_target_lock(target, family=family)
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
    dual_write(target, LOCK_FILE, lock, family=family)
    return lock_target(target, family=family)


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


def init_target(target: str, mode: TargetMode, family: str | None = None) -> TargetLock:
    root = target_root(target, family=family)
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
    dual_write(target, LOCK_FILE, lock, family=family)
    return lock


def load_target_lock(target: str, family: str | None = None) -> TargetLock:
    payload = read_dual(target, LOCK_FILE, family=family)
    return _parse_lock(payload)


def add_repo(
    target: str,
    repo_path: str,
    selected_ref: str,
    family: str | None = None,
    repo_id: str | None = None,
    worktree_path: str | None = None,
    preferred_runner: str | None = None,
    preferred_command: str | None = None,
    preferred_ref: str | None = None,
) -> TargetLock:
    lock = load_target_lock(target, family=family)
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
            preferred_runner=preferred_runner,
            preferred_command=preferred_command,
            preferred_ref=preferred_ref,
        )
    )
    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock, family=family)
    return lock


def lock_target(target: str, family: str | None = None) -> TargetLock:
    lock = load_target_lock(target, family=family)
    if not lock.repos:
        raise ValueError("target has no repos; add at least one repo before lock")

    for repo in lock.repos:
        resolved = resolve_ref_to_sha(Path(repo.repo_path), repo.selected_ref)
        repo.resolved_sha = resolved

    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock, family=family)
    return lock


def materialize_target(target: str, family: str | None = None) -> RuntimeState:
    lock = load_target_lock(target, family=family)
    if not lock.repos:
        raise ValueError("target has no repos")

    runtime_repos: list[RuntimeRepo] = []
    repos_root = target_repos_root(target, family=family)
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
        materialized_root=str(target_root(target, family=family)),
        repo_materializations=runtime_repos,
        materialized_at_utc=utc_now_iso(),
    )
    dual_write(target, RUNTIME_FILE, runtime, family=family)

    report = run_env_doctor(target, [Path(r.checkout_path) for r in runtime_repos])
    dual_write(target, ENV_FILE, report, family=family)

    return runtime


def target_status(target: str, family: str | None = None) -> dict[str, Any]:
    lock = load_target_lock(target, family=family)
    runtime_payload: dict[str, Any] | None = None
    env_payload: dict[str, Any] | None = None
    try:
        runtime_payload = read_dual(target, RUNTIME_FILE, family=family)
    except FileNotFoundError:
        runtime_payload = None
    try:
        env_payload = read_dual(target, ENV_FILE, family=family)
    except FileNotFoundError:
        env_payload = None

    snapshots = list_target_snapshots(target, family=family)
    latest_snapshot = snapshots[0] if snapshots else None

    if latest_snapshot is not None:
        latest_snapshot = dict(latest_snapshot)
        latest_snapshot = {
            "snapshot_id": latest_snapshot.get("snapshot_id"),
            "filename": latest_snapshot.get("filename"),
            "created_at_utc": latest_snapshot.get("created_at_utc"),
            "lock_hash": latest_snapshot.get("lock_hash"),
            "runtime_hash": latest_snapshot.get("runtime_hash"),
            "snapshot_hash": latest_snapshot.get("snapshot_hash"),
        }

    return {
        "target": target,
        "mode": lock.mode,
        "repos": [asdict(r) for r in lock.repos],
        "lock_hash": lock.lock_hash,
        "created_at_utc": lock.created_at_utc,
        "runtime": runtime_payload,
        "env": env_payload,
        "latest_snapshot": latest_snapshot,
        "snapshot": latest_snapshot,
    }


def target_timeline(
    target: str,
    family: str | None = None,
    repo_id: str | None = None,
    limit: int = 30,
    branch: str | None = None,
) -> dict[str, Any]:
    lock = load_target_lock(target, family=family)
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


def audit_shared_modules(target: str, family: str | None = None) -> dict[str, Any]:
    lock = load_target_lock(target, family=family)
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

    shared = {module: sorted(set(owners)) for module, owners in module_map.items() if len(set(owners)) >= 2}
    return {
        "target": target,
        "shared_modules": shared,
        "repo_count": len(lock.repos),
        "module_count": len(module_map),
    }


def build_catalog(target: str, repo_id: str | None = None, family: str | None = None) -> RunnerCatalog:
    runtime = read_dual(target, RUNTIME_FILE, family=family)
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
    dual_write(target, RUNNER_FILE, catalog, family=family)
    return catalog


def list_targets(family: str | None = None) -> list[str]:
    if family is not None:
        root = projects_root() / validate_family_name(family)
        if not root.exists():
            return []
        return sorted(
            entry.name
            for entry in root.iterdir()
            if entry.is_dir() and (entry / ".phench" / LOCK_FILE).exists()
        )

    root = projects_root()
    if not root.exists():
        return []
    targets: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if (entry / ".phench" / LOCK_FILE).exists():
            targets.append(entry.name)
        else:
            targets.extend(_list_targets_in_root(entry, family_prefix=entry.name))
    unique: list[str] = sorted(set(targets), key=lambda value: ("/" in value, value))
    return unique


def list_modules() -> list[str]:
    root = projects_modules_root()
    if not root.exists():
        return []

    return sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and (entry / "manifest.json").is_file()
    )


def _list_targets_in_root(root: Path, family_prefix: str | None) -> list[str]:
    found: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if (entry / ".phench" / LOCK_FILE).exists():
            if family_prefix is None:
                found.append(entry.name)
            else:
                found.append(f"{family_prefix}/{entry.name}")
    return sorted(found)


def set_env_profile(target: str, profile: str, values: dict[str, str], family: str | None = None) -> dict[str, Any]:
    if not profile.strip():
        raise ValueError("profile name cannot be empty")
    normalized = {str(k): str(v) for k, v in values.items()}
    try:
        state = read_dual(target, PROFILE_FILE, family=family)
    except FileNotFoundError:
        state = {"active_profile": profile, "profiles": {}}
    profiles = state.get("profiles")
    if not isinstance(profiles, dict):
        profiles = {}
    profiles[profile] = normalized
    state = {"active_profile": profile, "profiles": profiles}
    dual_write(target, PROFILE_FILE, state, family=family)
    return state


def get_env_profile(target: str, profile: str | None = None, family: str | None = None) -> dict[str, str]:
    try:
        state = read_dual(target, PROFILE_FILE, family=family)
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
    if runner and command_name:
        return run_command(checkout_path, runner, command_name, env_overrides=env_overrides)

    if runner and not command_name:
        options = [command for command in catalog.commands if command.runner == runner]
        if not options:
            raise ValueError(f"runner has no discovered commands: {runner}")
        return run_command(checkout_path, runner, options[0].name, env_overrides=env_overrides)

    if non_interactive:
        raise ValueError(
            "runner policy is required for non-interactive execution; pass --runner or configure preferred_runner"
        )

    selected = pick_command_interactive(catalog)
    return run_command(checkout_path, selected.runner, selected.name, env_overrides=env_overrides)


def _resolve_repo_runner_and_command(
    repo_id: str,
    repo: RepoSelection,
    catalog: RunnerCatalog,
    cli_runner: str | None,
    cli_command: str | None,
    repo_runner_override: str | None = None,
    repo_command_override: str | None = None,
    enforce_no_interactive: bool = False,
) -> tuple[str | None, str | None]:
    runner = repo_runner_override or cli_runner or repo.preferred_runner
    command_name = repo_command_override or cli_command or repo.preferred_command

    if command_name and not runner:
        raise ValueError(f"repo '{repo_id}' requires a runner for command '{command_name}'")

    if not runner:
        if enforce_no_interactive:
            raise ValueError(
                f"repo '{repo_id}' requires runner policy (--runner or preferred_runner) "
                "for non-interactive/all-repos execution."
            )
        return None, command_name

    if command_name:
        return runner, command_name

    available = [command for command in catalog.commands if command.runner == runner]
    if not available:
        raise ValueError(f"runner '{runner}' has no discovered commands in repo '{repo_id}'")
    if enforce_no_interactive and len(available) > 1:
        raise ValueError(
            f"repo '{repo_id}' with runner '{runner}' requires explicit command "
            "for non-interactive/all-repos execution."
        )
    return runner, available[0].name


def _materialization_entry(item: dict[str, Any]) -> tuple[str, Path]:
    repo_id = item.get("repo_id")
    checkout_path = item.get("checkout_path")
    if not isinstance(repo_id, str) or not repo_id.strip():
        raise ValueError("invalid runtime materialization entry: missing repo_id")
    if not isinstance(checkout_path, str) or not checkout_path.strip():
        raise ValueError(f"invalid runtime materialization entry for {repo_id}: missing checkout_path")
    return repo_id, Path(checkout_path).resolve()


def _materialization_checkouts(
    materializations: list[dict[str, Any]],
) -> list[Path]:
    return [checkout for _, checkout in (_materialization_entry(item) for item in materializations)]


def _run_env_doctor_for_materializations(
    target: str,
    materializations: list[dict[str, Any]],
    family: str | None = None,
) -> dict[str, Any]:
    report = run_env_doctor(target, _materialization_checkouts(materializations))
    dual_write(target, ENV_FILE, report, family=family)
    return asdict(report)


def _materialization_lookup(
    repo_id: str | None,
    repo_ids: list[str] | None,
    all_repos: bool,
    materializations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    if all_repos:
        return [dict(item) for item in materializations]

    if repo_id is not None:
        selected = next((item for item in materializations if item.get("repo_id") == repo_id), None)
        if selected is None:
            raise ValueError(f"repo_id not materialized: {repo_id}")
        return [dict(selected)]

    if repo_ids is not None:
        index = {repo_id: item for item in materializations for repo_id in [item.get("repo_id")] if isinstance(repo_id, str)}
        if not index:
            raise ValueError("target has no runtime materialization; run target materialize")
        requested: list[str] = []
        seen: set[str] = set()
        for requested_repo_id in repo_ids:
            if requested_repo_id in seen:
                continue
            seen.add(requested_repo_id)
            if requested_repo_id not in index:
                raise ValueError(f"repo_id not materialized: {requested_repo_id}")
            requested.append(requested_repo_id)
        return [dict(index[rid]) for rid in requested]

    return [dict(item) for item in materializations[:1]]


def build_project_execution_matrix(
    target: str,
    family: str | None = None,
    snapshot_id: str | None = None,
    repo_id: str | None = None,
    repo_ids: list[str] | None = None,
    repo_ref_overrides: dict[str, str] | None = None,
    repo_runner_overrides: dict[str, str] | None = None,
    repo_command_overrides: dict[str, str] | None = None,
    repo_env_profile_overrides: dict[str, str] | None = None,
    runner: str | None = None,
    command_name: str | None = None,
    selected_ref: str | None = None,
    all_repos: bool = False,
    env_profile: str | None = None,
    non_interactive: bool = False,
    validate_commands: bool = False,
    sort_repos: bool = False,
) -> dict[str, Any]:
    lock_hash = None
    snapshot_hash = None
    runtime_hash = None

    if snapshot_id is not None:
        snapshot = show_target_snapshot(target, snapshot_id, family=family)
        runtime = snapshot.get("runtime")
        if not isinstance(runtime, dict):
            raise ValueError(f"snapshot '{snapshot_id}' has no runtime payload")
        materializations = runtime.get("repo_materializations")
        if not isinstance(materializations, list) or not materializations:
            raise ValueError(
                f"snapshot '{snapshot_id}' has no runtime materialization; create snapshot after materialize"
            )
        snapshot_lock = snapshot.get("lock")
        if not isinstance(snapshot_lock, dict):
            raise ValueError(f"snapshot '{snapshot_id}' has invalid lock payload")
        lock = _parse_lock(snapshot_lock)
        report = _run_env_doctor_for_materializations(target, materializations, family=family)
        lock_hash = str((snapshot_lock or {}).get("lock_hash", ""))
        snapshot_hash = str(snapshot.get("snapshot_hash", ""))
        runtime_hash = str(snapshot.get("runtime_hash", ""))
        if not runtime_hash:
            runtime_hash = _stable_payload_hash(runtime)
    else:
        report = run_env_doctor_for_target(target, family=family)
        runtime = read_dual(target, RUNTIME_FILE, family=family)
        materializations = runtime.get("repo_materializations")
        lock = load_target_lock(target, family=family)
        lock_hash = lock.lock_hash

    if report["doctor_status"] != "pass":
        missing = ", ".join(report["missing_requirements"])
        raise RuntimeError(f"env doctor failed, missing requirements: {missing}")

    if repo_id is not None and repo_ids is not None:
        raise ValueError("repo_id and repo_ids are mutually exclusive")
    if repo_ids is not None:
        repo_ids = [repo for repo in repo_ids if repo]
        if not repo_ids:
            raise ValueError("repo_ids cannot be empty")

    if repo_ref_overrides is None:
        repo_ref_overrides_normalized = {}
    else:
        repo_ref_overrides_normalized = _normalize_repo_map(repo_ref_overrides, label="repo_ref_overrides")

    repo_runner_overrides_normalized = _normalize_repo_map(
        repo_runner_overrides,
        label="repo_runner_overrides",
    )
    repo_command_overrides_normalized = _normalize_repo_map(
        repo_command_overrides,
        label="repo_command_overrides",
    )
    repo_env_profile_overrides_normalized = _normalize_repo_map(
        repo_env_profile_overrides,
        label="repo_env_profile_overrides",
    )

    if all_repos and repo_ids is not None:
        raise ValueError("repo_ids is not compatible with --all-repos")

    if repo_id is not None and not repo_id.strip():
        raise ValueError("repo_id cannot be empty")

    if repo_ids is not None:
        repo_index = {item.strip(): item.strip() for item in repo_ids}
        repo_ids = list(repo_index.values())
        unknown_override = [item for item in repo_ref_overrides_normalized if item not in repo_index]
        if unknown_override:
            raise ValueError(f"repo_id not materialized: {unknown_override[0]}")
        unknown_runner_override = [item for item in repo_runner_overrides_normalized if item not in repo_index]
        if unknown_runner_override:
            raise ValueError(f"repo_id not materialized: {unknown_runner_override[0]}")
        unknown_command_override = [item for item in repo_command_overrides_normalized if item not in repo_index]
        if unknown_command_override:
            raise ValueError(f"repo_id not materialized: {unknown_command_override[0]}")
        unknown_env_profile_override = [
            item
            for item in repo_env_profile_overrides_normalized
            if item not in repo_index
        ]
        if unknown_env_profile_override:
            raise ValueError(f"repo_id not materialized: {unknown_env_profile_override[0]}")

    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    if all_repos:
        selected_items = [dict(item) for item in materializations]
    else:
        selected_items = _materialization_lookup(
            repo_id,
            repo_ids=repo_ids,
            all_repos=False,
            materializations=materializations,
        )

    if repo_id is not None:
        repo_ids = [repo_id]

    lock_index = {entry.repo_id: entry for entry in lock.repos}
    enforce_no_interactive = non_interactive or all_repos

    plans: list[dict[str, Any]] = []
    for item in selected_items:
        item_repo_id, item_checkout = _materialization_entry(item)
        lock_repo = lock_index.get(item_repo_id)
        if lock_repo is None:
            raise ValueError(f"repo_id not in target lock: {item_repo_id}")

        if (repo_ref := repo_ref_overrides_normalized.get(item_repo_id)) is not None:
            ref_source = "repo_override"
        elif selected_ref is not None:
            repo_ref = selected_ref
            ref_source = "cli_ref"
        elif lock_repo.preferred_ref is not None:
            repo_ref = lock_repo.preferred_ref
            ref_source = "preferred_ref"
        elif lock_repo.selected_ref is not None:
            repo_ref = lock_repo.selected_ref
            ref_source = "selected_ref"
        else:
            repo_ref = None
            ref_source = "materialized_ref"

        if repo_ref is not None:
            resolved = resolve_ref_to_sha(Path(lock_repo.repo_path), repo_ref)
            materialize_repo_checkout(Path(lock_repo.repo_path), item_checkout, resolved)
            item["resolved_sha"] = resolved
        else:
            resolved = item.get("resolved_sha")

        repo_runner_override = repo_runner_overrides_normalized.get(item_repo_id)
        repo_command_override = repo_command_overrides_normalized.get(item_repo_id)
        repo_env_profile = repo_env_profile_overrides_normalized.get(item_repo_id, env_profile)
        env_overrides = get_env_profile(target, profile=repo_env_profile, family=family)

        if validate_commands:
            catalog = build_runner_catalog(target, item_checkout)
            repo_runner, repo_command = _resolve_repo_runner_and_command(
                item_repo_id,
                lock_repo,
                catalog,
                cli_runner=runner,
                cli_command=command_name,
                repo_runner_override=repo_runner_override,
                repo_command_override=repo_command_override,
                enforce_no_interactive=enforce_no_interactive,
            )
        else:
            repo_runner = repo_runner_override or runner or lock_repo.preferred_runner
            repo_command = repo_command_override or command_name or lock_repo.preferred_command
            if repo_command and not repo_runner:
                raise ValueError(f"repo '{item_repo_id}' requires a runner for command '{repo_command}'")

        plans.append(
            {
                "repo_id": item_repo_id,
                "repo_path": lock_repo.repo_path,
                "checkout_path": item["checkout_path"],
                "lock_selected_ref": lock_repo.selected_ref,
                "lock_preferred_ref": lock_repo.preferred_ref,
                "effective_ref": repo_ref,
                "effective_ref_source": ref_source,
                "resolved_sha": resolved,
                "effective_runner": repo_runner,
                "effective_command": repo_command,
                "effective_env_profile": repo_env_profile,
                "env_overrides": env_overrides,
                "preferred_runner": lock_repo.preferred_runner,
                "preferred_command": lock_repo.preferred_command,
            }
        )

    if sort_repos:
        plans.sort(key=lambda item: str(item["repo_id"]))

    return {
        "target": target,
        "family": family,
        "lock_hash": lock_hash,
        "snapshot_hash": snapshot_hash,
        "runtime_hash": runtime_hash,
        "snapshot_id": snapshot_id,
        "all_repos": all_repos,
        "non_interactive": non_interactive,
        "repo_count": len(plans),
        "repos": plans,
    }


def _validate_module_repos_payload_field(
    payload: dict[str, Any],
    *,
    field: str,
) -> list[str]:
    raw = payload.get(field)
    if raw is None:
        return []

    if not isinstance(raw, list):
        raise ValueError(f"module manifest field '{field}' must be a list")

    values: list[str] = []
    for value in raw:
        if not isinstance(value, str):
            raise ValueError(f"module manifest field '{field}' contains non-string entry")
        repo_id = value.strip()
        if not repo_id:
            continue
        values.append(repo_id)
    return values


def _validate_module_repos_payload_map(
    payload: dict[str, Any],
    *,
    field: str,
) -> dict[str, str]:
    raw = payload.get(field)
    if raw is None:
        return {}

    if not isinstance(raw, dict):
        raise ValueError(f"module manifest field '{field}' must be an object")

    items: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise ValueError(f"module manifest field '{field}' contains non-string key")

        repo_id = key.strip()
        if not repo_id:
            raise ValueError(f"module manifest field '{field}' contains empty repo id")

        if not isinstance(value, str):
            raise ValueError(f"module manifest field '{field}' requires string values")
        item = value.strip()
        if not item:
            raise ValueError(
                f"module manifest field '{field}' for repo '{repo_id}' must not be empty"
            )

        items[repo_id] = item

    return items


def _validate_module_manifest_schema_version(
    module: str,
    payload: dict[str, Any],
) -> int:
    if "schema_version" not in payload:
        raise ValueError(f"module manifest '{module}' must define 'schema_version'")

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        raise ValueError(
            f"module manifest '{module}' schema_version must be an integer"
        )

    if schema_version not in SUPPORTED_MODULE_MANIFEST_SCHEMA_VERSIONS:
        raise ValueError(
            f"module manifest '{module}' has unsupported schema_version: {schema_version}"
        )

    return schema_version


def _normalize_repo_id_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        repo_id = value.strip()
        if not repo_id:
            continue
        if repo_id in seen:
            continue
        seen.add(repo_id)
        normalized.append(repo_id)
    return normalized


def _normalize_repo_map(values: dict[str, str] | None, *, label: str) -> dict[str, str]:
    if values is None:
        return {}
    normalized: dict[str, str] = {}
    for repo_id, value in values.items():
        if not isinstance(repo_id, str):
            raise ValueError(f"{label} keys must be strings")
        normalized_key = repo_id.strip()
        if not normalized_key:
            raise ValueError(f"{label} contains empty key")

        if not isinstance(value, str):
            raise ValueError(f"{label} values must be strings")
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError(f"{label} value for repo '{normalized_key}' cannot be empty")
        normalized[normalized_key] = normalized_value
    return normalized


def load_module_manifest(
    module: str,
    *,
    available_repo_ids: list[str] | None = None,
) -> dict[str, Any]:
    manifest_path = _resolve_module_manifest_path(module)

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid module manifest for {module}: malformed json") from error

    if not isinstance(payload, dict):
        raise ValueError(f"invalid module manifest for {module}: payload must be an object")

    schema_version = _validate_module_manifest_schema_version(module=module, payload=payload)
    explicit_repos = (
        _validate_module_repos_payload_field(payload, field="repo_ids")
        or _validate_module_repos_payload_field(payload, field="repos")
    )
    explicit_repos = _normalize_repo_id_list(explicit_repos)
    raw_patterns = _validate_module_repos_payload_field(payload, field="repo_patterns")
    available = _normalize_repo_id_list(available_repo_ids or [])
    expanded: list[str] = []
    for pattern in raw_patterns:
        matched = sorted([repo_id for repo_id in available if fnmatch(repo_id, pattern)])
        expanded.extend(matched)

    if not explicit_repos and not raw_patterns and not available:
        raise ValueError(
            f"module manifest '{module}' must define 'repo_ids', 'repos', or 'repo_patterns'"
        )

    combined = _normalize_repo_id_list(explicit_repos + expanded)
    combined = sorted(set(combined))
    if available:
        unavailable = [repo_id for repo_id in combined if repo_id not in available]
        if unavailable:
            raise ValueError(
                f"module manifest '{module}' references unknown repos: {', '.join(unavailable)}"
            )

    module_overrides: dict[str, Any] = {
        "schema_version": schema_version,
        "repo_ref_overrides": _validate_module_repos_payload_map(
            payload,
            field="repo_ref_overrides",
        ),
        "repo_runner_overrides": _validate_module_repos_payload_map(
            payload,
            field="repo_runner_overrides",
        ),
        "repo_command_overrides": _validate_module_repos_payload_map(
            payload,
            field="repo_command_overrides",
        ),
        "repo_env_profile_overrides": _validate_module_repos_payload_map(
            payload,
            field="repo_env_profile_overrides",
        ),
    }

    if available:
        for key in (
            "repo_ref_overrides",
            "repo_runner_overrides",
            "repo_command_overrides",
            "repo_env_profile_overrides",
        ):
            value = module_overrides[key]
            unknown = [repo_id for repo_id in value if repo_id not in available]
            if unknown:
                raise ValueError(f"module manifest '{module}' has unknown {key} key(s): {', '.join(unknown)}")

    if not combined:
        raise ValueError(f"module manifest '{module}' matched no repos")

    module_overrides["repo_ids"] = combined
    return module_overrides


def load_module_repos(
    module: str,
    *,
    available_repo_ids: list[str] | None = None,
) -> list[str]:
    return load_module_manifest(module, available_repo_ids=available_repo_ids)["repo_ids"]


def run_target(
    target: str,
    family: str | None = None,
    snapshot_id: str | None = None,
    repo_id: str | None = None,
    repo_ids: list[str] | None = None,
    repo_ref_overrides: dict[str, str] | None = None,
    repo_runner_overrides: dict[str, str] | None = None,
    repo_command_overrides: dict[str, str] | None = None,
    repo_env_profile_overrides: dict[str, str] | None = None,
    runner: str | None = None,
    command_name: str | None = None,
    selected_ref: str | None = None,
    all_repos: bool = False,
    execution_mode: str = "serial",
    env_profile: str | None = None,
    non_interactive: bool = False,
) -> int:
    matrix = build_project_execution_matrix(
        target=target,
        family=family,
        snapshot_id=snapshot_id,
        repo_id=repo_id,
        repo_ids=repo_ids,
        repo_ref_overrides=repo_ref_overrides,
        repo_runner_overrides=repo_runner_overrides,
        repo_command_overrides=repo_command_overrides,
        repo_env_profile_overrides=repo_env_profile_overrides,
        runner=runner,
        command_name=command_name,
        selected_ref=selected_ref,
        all_repos=all_repos,
        env_profile=env_profile,
        non_interactive=non_interactive,
        validate_commands=True,
        sort_repos=False,
    )

    if execution_mode not in {"serial", "parallel"}:
        raise ValueError("execution_mode must be one of: serial, parallel")

    runs: list[tuple[Path, RunnerCatalog, str | None, str | None, dict[str, str] | None]] = []
    for item in matrix["repos"]:
        checkout_path = Path(item["checkout_path"])
        catalog = build_runner_catalog(target, checkout_path)
        runs.append(
            (
                checkout_path,
                catalog,
                item["effective_runner"],
                item["effective_command"],
                item.get("env_overrides"),
            )
        )

    if execution_mode == "parallel" and len(runs) > 1:
        with ThreadPoolExecutor(max_workers=len(runs)) as pool:
            futures = [
                pool.submit(
                    _run_single_repo_target,
                    checkout_path,
                    effective_catalog,
                    effective_runner,
                    effective_command,
                    non_interactive,
                    env_overrides,
                )
                for checkout_path, effective_catalog, effective_runner, effective_command, env_overrides in runs
            ]
            results = [future.result() for future in futures]
        nonzero = [code for code in results if code != 0]
        return nonzero[0] if nonzero else 0

    for checkout, effective_catalog, effective_runner, effective_command, env_overrides in runs:
        code = _run_single_repo_target(
            checkout,
            effective_catalog,
            effective_runner,
            effective_command,
            non_interactive,
            env_overrides,
        )
        if code != 0:
            return code
    return 0


def run_env_doctor_for_target(target: str, family: str | None = None) -> dict[str, Any]:
    runtime = read_dual(target, RUNTIME_FILE, family=family)
    materializations = runtime.get("repo_materializations")
    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")
    checkouts = [Path(str(item.get("checkout_path", ""))).resolve() for item in materializations]
    report = run_env_doctor(target, checkouts)
    dual_write(target, ENV_FILE, report, family=family)
    return asdict(report)


def sync_target(target: str, prefer: str | None = None, family: str | None = None) -> dict[str, Any]:
    results = {}
    for filename in (LOCK_FILE, RUNTIME_FILE, ENV_FILE, RUNNER_FILE, PROFILE_FILE):
        try:
            results[filename] = sync_dual(target, filename, prefer=prefer, family=family)
        except FileNotFoundError:
            continue
    if not results:
        raise FileNotFoundError("No state files to sync")
    return results
