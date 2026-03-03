from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from .env_doctor import run_env_doctor
from .git_ops import (
    detect_head_branch,
    list_timeline,
    materialize_repo_checkout,
    resolve_ref_to_sha,
    sanitize_repo_id,
)
from .models import ModuleManifest, RepoSelection, RuntimeRepo, RuntimeState, RunnerCatalog, TargetLock, TargetMode
from .paths import (
    module_manifest_path,
    projects_root,
    phenotype_root,
    repository_root_candidates,
    target_repos_root,
    target_root,
)
from .runner import build_runner_catalog, pick_command_interactive, run_command
from .store import dual_write, read_dual, sync_dual, utc_now_iso

LOCK_FILE = "target.lock.json"
RUNTIME_FILE = "runtime.json"
ENV_FILE = "env.snapshot.json"
RUNNER_FILE = "runner.catalog.json"
PROFILE_FILE = "env.profile.json"
DEFAULT_EXCLUDED_REPOS = frozenset({"4sgm", "parpour", "civ", "trace"})


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


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"manifest not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in manifest: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"manifest payload must be a JSON object: {path}")
    return payload


def _load_module_manifest(module_name: str) -> ModuleManifest:
    payload = _load_json_file(module_manifest_path(module_name))
    schema_version = int(payload.get("schema_version", 1))
    raw_patterns = payload.get("repo_patterns")
    if raw_patterns is None:
        repo_patterns = ["*"]
    elif isinstance(raw_patterns, list) and all(isinstance(item, str) for item in raw_patterns):
        repo_patterns = raw_patterns
    else:
        raise ValueError(f"invalid repo_patterns in manifest: {module_name}")

    def _load_str_dict(key: str) -> dict[str, str]:
        raw_value = payload.get(key)
        if raw_value is None:
            return {}
        if not isinstance(raw_value, dict):
            raise ValueError(f"invalid {key} in manifest: {module_name}")
        converted: dict[str, str] = {}
        for item_key, value in raw_value.items():
            if not isinstance(item_key, str) or not isinstance(value, str):
                raise ValueError(f"invalid {key} entry in manifest: {module_name}")
            converted[item_key] = value
        return converted

    return ModuleManifest(
        schema_version=schema_version,
        repo_patterns=repo_patterns,
        default_ref=str(payload.get("default_ref", "HEAD")),
        repo_ref_overrides=_load_str_dict("repo_ref_overrides"),
        repo_runner_overrides=_load_str_dict("repo_runner_overrides"),
        repo_command_overrides=_load_str_dict("repo_command_overrides"),
        repo_env_profile_overrides=_load_str_dict("repo_env_profile_overrides"),
    )


def _repo_id_from_path(repo_path: Path) -> str:
    return sanitize_repo_id(repo_path.name)


def _select_module_repos(
    manifest: ModuleManifest,
    exclude_repos: set[str] | None = None,
) -> list[Path]:
    excluded = {sanitize_repo_id(repo_name) for repo_name in (exclude_repos or set())}
    selected: list[Path] = []
    for repo_path in repository_root_candidates():
        repo_id = _repo_id_from_path(repo_path)
        if repo_id in DEFAULT_EXCLUDED_REPOS or repo_id in excluded:
            continue
        if not any(fnmatch(repo_id, pattern) for pattern in manifest.repo_patterns):
            continue
        selected.append(repo_path)
    return selected


def _find_repo_modules(repo_path: Path) -> set[str]:
    src_root = repo_path / "src"
    if not src_root.exists() or not src_root.is_dir():
        return set()

    modules: set[str] = set()
    for child in src_root.iterdir():
        if not child.is_dir():
            continue
        if not (child / "__init__.py").exists():
            continue
        modules.add(child.name)
    return modules


def _collect_shared_modules(
    repo_modules: dict[str, set[str]],
    *,
    min_repo_count: int = 2,
) -> dict[str, list[str]]:
    return {
        module_name: sorted(repos)
        for module_name, repos in repo_modules.items()
        if len(repos) >= min_repo_count
    }


def _append_repo_selection(
    lock: TargetLock,
    repo_path: Path,
    selected_ref: str,
    *,
    module_name: str | None = None,
    selected_runner: str | None = None,
    selected_command: str | None = None,
    selected_env_profile: str | None = None,
    repo_id: str | None = None,
    worktree_path: str | None = None,
) -> None:
    rid = repo_id or _repo_id_from_path(repo_path)
    lock.repos = [entry for entry in lock.repos if entry.repo_id != rid]
    lock.repos.append(
        RepoSelection(
            repo_id=rid,
            repo_path=str(repo_path.resolve()),
            selected_ref=selected_ref,
            module_name=module_name,
            selected_runner=selected_runner,
            selected_command=selected_command,
            selected_env_profile=selected_env_profile,
            source_worktree_path=worktree_path,
            resolved_sha=None,
        )
    )


def scan_shared_modules_across_repos(
    repos_root: Path | None = None,
    *,
    exclude_repos: set[str] | None = None,
    min_repo_count: int = 2,
) -> dict[str, Any]:
    if min_repo_count < 2:
        raise ValueError("min_repo_count must be at least 2")

    if repos_root is None:
        candidate_paths = repository_root_candidates()
        root = phenotype_root() / "repos"
    else:
        root = Path(repos_root).expanduser().resolve()
        if not root.exists():
            return {
                "repos_root": str(root),
                "shared_modules": {},
                "shared_count": 0,
                "module_count": 0,
                "repo_count": 0,
                "excluded_repos": [],
                "examined_repos": [],
                "min_repo_count": min_repo_count,
            }
        candidate_paths = sorted([entry for entry in root.iterdir() if entry.is_dir() and not entry.name.startswith(".")])

    excluded = {sanitize_repo_id(repo_name) for repo_name in (exclude_repos or set())}
    effective_excludes = sorted(DEFAULT_EXCLUDED_REPOS | excluded)
    repo_modules: dict[str, set[str]] = {}

    examined_repos: list[str] = []
    for repo_path in candidate_paths:
        repo_id = _repo_id_from_path(repo_path)
        if repo_id in effective_excludes:
            continue
        examined_repos.append(repo_id)
        modules = _find_repo_modules(repo_path)
        for module_name in modules:
            repo_modules.setdefault(module_name, set()).add(repo_id)

    shared_modules = _collect_shared_modules(repo_modules, min_repo_count=min_repo_count)

    return {
        "repos_root": str(root),
        "shared_modules": shared_modules,
        "shared_count": len(shared_modules),
        "module_count": len(repo_modules),
        "repo_count": len(examined_repos),
        "excluded_repos": effective_excludes,
        "examined_repos": examined_repos,
        "min_repo_count": min_repo_count,
    }


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


def add_repo(
    target: str,
    repo_path: str,
    selected_ref: str,
    repo_id: str | None = None,
    worktree_path: str | None = None,
    module_name: str | None = None,
    selected_runner: str | None = None,
    selected_command: str | None = None,
    selected_env_profile: str | None = None,
) -> TargetLock:
    lock = load_target_lock(target)
    repo = Path(repo_path).expanduser().resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        raise ValueError(f"repo is not a git checkout: {repo}")

    _append_repo_selection(
        lock,
        repo,
        selected_ref=selected_ref,
        module_name=module_name,
        selected_runner=selected_runner,
        selected_command=selected_command,
        selected_env_profile=selected_env_profile,
        repo_id=repo_id,
        worktree_path=worktree_path,
    )
    lock.created_at_utc = utc_now_iso()
    lock.lock_hash = _lock_hash(lock)
    dual_write(target, LOCK_FILE, lock)
    return lock


def add_module_to_target(
    target: str,
    module_name: str,
    selected_ref: str | None = None,
    exclude_repos: set[str] | None = None,
) -> TargetLock:
    if not module_name.strip():
        raise ValueError("module name cannot be empty")
    if "/" in module_name or "\\" in module_name or ".." in module_name:
        raise ValueError(f"invalid module name: {module_name}")

    manifest = _load_module_manifest(module_name)
    lock = load_target_lock(target)

    candidates = _select_module_repos(manifest, exclude_repos=exclude_repos)
    if not candidates:
        raise ValueError(f"module {module_name} selected no matching repos")

    fallback_ref = selected_ref or manifest.default_ref
    for candidate in candidates:
        repo_id = _repo_id_from_path(candidate)
        _append_repo_selection(
            lock,
            candidate,
            selected_ref=manifest.repo_ref_overrides.get(repo_id, fallback_ref),
            module_name=module_name,
            selected_runner=manifest.repo_runner_overrides.get(repo_id),
            selected_command=manifest.repo_command_overrides.get(repo_id),
            selected_env_profile=manifest.repo_env_profile_overrides.get(repo_id),
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


def target_timeline(target: str, repo_id: str | None = None, limit: int = 30) -> dict[str, Any]:
    lock = load_target_lock(target)
    if not lock.repos:
        raise ValueError("target has no repos")

    if repo_id:
        chosen = next((repo for repo in lock.repos if repo.repo_id == repo_id), None)
        if not chosen:
            raise ValueError(f"repo_id not found in target: {repo_id}")
    else:
        chosen = lock.repos[0]

    timeline = list_timeline(Path(chosen.repo_path), limit=limit)
    return {
        "target": target,
        "repo_id": chosen.repo_id,
        "repo_path": chosen.repo_path,
        "selected_ref": chosen.selected_ref,
        "resolved_sha": chosen.resolved_sha,
        **timeline,
    }


def audit_shared_modules(target: str) -> dict[str, Any]:
    lock = load_target_lock(target)
    repo_modules: dict[str, set[str]] = {}
    for repo in lock.repos:
        modules = _find_repo_modules(Path(repo.repo_path))
        for module_name in modules:
            repo_modules.setdefault(module_name, set()).add(repo.repo_id)

    shared = _collect_shared_modules(repo_modules)
    return {
        "target": target,
        "shared_modules": shared,
        "repo_count": len(lock.repos),
        "module_count": len(repo_modules),
        "min_repo_count": 2,
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


def _repo_run_overrides(
    runtime_item: dict[str, Any],
    lock: TargetLock,
    command_name: str | None,
    runner: str | None,
    env_profile: str | None,
) -> tuple[str | None, str | None, str | None]:
    repo_id = runtime_item.get("repo_id")
    if not isinstance(repo_id, str) or not repo_id.strip():
        raise ValueError("invalid runtime materialization entry: missing repo_id")

    selected = next((entry for entry in lock.repos if entry.repo_id == repo_id), None)
    if not selected:
        raise ValueError(f"repo_id not in target lock: {repo_id}")

    selected_runner = runner if runner is not None else selected.selected_runner
    selected_command = command_name if command_name is not None else selected.selected_command
    selected_profile = env_profile if env_profile is not None else selected.selected_env_profile
    if selected_profile is None:
        if env_profile is None:
            profile_env = get_env_profile(target=lock.target_name)
        else:
            profile_env = None
    elif not selected_profile.strip():
        profile_env = None
    else:
        profile_env = get_env_profile(target=lock.target_name, profile=selected_profile)

    return selected_runner, selected_command, profile_env


def run_target(
    target: str,
    repo_id: str | None = None,
    runner: str | None = None,
    command_name: str | None = None,
    all_repos: bool = False,
    execution_mode: str = "serial",
    env_profile: str | None = None,
) -> int:
    report = run_env_doctor_for_target(target)
    if report["doctor_status"] != "pass":
        missing = ", ".join(report["missing_requirements"])
        raise RuntimeError(f"env doctor failed, missing requirements: {missing}")

    if execution_mode not in {"serial", "parallel"}:
        raise ValueError("execution_mode must be one of: serial, parallel")

    runtime = read_dual(target, RUNTIME_FILE)
    materializations = runtime.get("repo_materializations")
    if not isinstance(materializations, list) or not materializations:
        raise ValueError("target has no runtime materialization; run target materialize")

    selected_items = materializations
    if repo_id is not None:
        selected = next((item for item in materializations if item.get("repo_id") == repo_id), None)
        if selected is None:
            raise ValueError(f"repo_id not materialized: {repo_id}")
        selected_items = [selected]
    elif not all_repos:
        selected_items = [materializations[0]]

    lock = load_target_lock(target)
    runs: list[tuple[Path, RunnerCatalog, str | None, str | None, dict[str, str] | None]] = []
    for item in selected_items:
        item_repo_id, item_checkout = _materialization_entry(item)
        selected_runner, selected_command, selected_env = _repo_run_overrides(
            item,
            lock=lock,
            command_name=command_name,
            runner=runner,
            env_profile=env_profile,
        )
        if all_repos and (selected_runner is None or selected_command is None):
            raise ValueError(
                "--all-repos requires --runner and --command or module-level overrides for each repo"
            )
        runs.append(
            (
                item_checkout,
                build_catalog(target, repo_id=item_repo_id),
                selected_runner,
                selected_command,
                selected_env,
            )
        )

    if execution_mode == "parallel" and len(runs) > 1:
        with ThreadPoolExecutor(max_workers=len(runs)) as pool:
            futures = [
                pool.submit(
                    _run_single_repo_target,
                    checkout,
                    catalog,
                    selected_runner,
                    selected_command,
                    repo_env,
                )
                for checkout, catalog, selected_runner, selected_command, repo_env in runs
            ]
            results = [future.result() for future in futures]
        nonzero = [code for code in results if code != 0]
        return nonzero[0] if nonzero else 0

    for checkout, catalog, selected_runner, selected_command, repo_env in runs:
        code = _run_single_repo_target(
            checkout,
            catalog,
            selected_runner,
            selected_command,
            repo_env,
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
