from __future__ import annotations

import hashlib
import json
import re
import ast
from copy import deepcopy
from collections.abc import Iterable
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
<<<<<<< HEAD
    module_manifests_root,
    module_manifest_path,
    projects_root,
    phenotype_root,
=======
    module_manifest_path,
    projects_root,
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
<<<<<<< HEAD
SCAN_SHARED_REPOS_SCHEMA_VERSION = 1
SCAN_SHARED_REPOS_ROOT_MODE_REPOS = "repos"
SCAN_SHARED_REPOS_ROOT_MODE_WORKTREES = "worktrees"
SCAN_SHARED_REPOS_DEFAULT_MODULE_PREFIX = "shared-module"
SCAN_SHARED_REPOS_MAX_NAME_LENGTH = 60
SCAN_SHARED_REPOS_RECOMMENDED_MODULE_COUNT_LIMIT = 10
SCAN_SHARED_REPOS_MANIFEST_INDEX_FILENAME = "index.json"
SCAN_SHARED_REPOS_MANIFEST_INDEX_SUMMARY_FILENAME = "index-summary.json"
SCAN_SHARED_REPOS_MANIFEST_AUDIT_FILENAME = "manifest-audit.jsonl"

SCAN_SHARED_REPOS_OUTPUT_SCHEMA = {
    "scan_schema_version": SCAN_SHARED_REPOS_SCHEMA_VERSION,
    "repos_root": "string",
    "repos_root_mode": "repos|worktrees",
    "root_mode_hint": "string",
    "warnings": "array",
    "repo_paths": {"type": "object", "values": "string"},
    "shared_modules": {"type": "object", "values": "array"},
    "shared_count": "integer",
    "module_count": "integer",
    "repo_count": "integer",
    "excluded_repos": "array",
    "examined_repos": "array",
    "min_repo_count": "integer",
    "recommended_modules": "array",
    "module_candidates": "array",
}

SCAN_SHARED_REPOS_MODULE_CANDIDATE_TEMPLATE = {
    "module": "string",
    "repo_ids": "array",
    "repo_count": "integer",
    "depends_on_count": "integer",
    "depends_on": "array",
    "manifest_template": {
        "schema_version": SCAN_SHARED_REPOS_SCHEMA_VERSION,
        "repo_patterns": "array",
        "default_ref": "HEAD",
        "repo_ref_overrides": "object",
        "repo_runner_overrides": "object",
        "repo_command_overrides": "object",
        "repo_env_profile_overrides": "object",
        "matched_repos": "array",
    },
}
=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)


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


<<<<<<< HEAD
def _normalize_candidate_module_name(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")
    return slug or "module"


def _truncate_module_name(value: str, *, max_length: int = SCAN_SHARED_REPOS_MAX_NAME_LENGTH) -> str:
    return value[:max_length] if len(value) > max_length else value


def _candidate_conflict_suffix(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def _build_candidate_name(base: str, *, suffix: str | None = None) -> str:
    if suffix:
        suffix_fragment = f"-{suffix}"
        allowed = max(SCAN_SHARED_REPOS_MAX_NAME_LENGTH - len(suffix_fragment), 1)
        base_prefix = _truncate_module_name(base, max_length=allowed)
        return f"{base_prefix}{suffix_fragment}"
    return _truncate_module_name(base)


def _build_scannable_candidate_name(base: str, used_names: set[str], *, max_attempts: int = 25) -> str:
    attempt = 0
    candidate_name = _build_candidate_name(base)
    while candidate_name in used_names:
        attempt += 1
        if attempt > max_attempts:
            raise RuntimeError(f"unable to resolve unique candidate name for: {base}")
        candidate_name = _build_candidate_name(base, suffix=_candidate_conflict_suffix(f"{base}:{attempt}"))
    return candidate_name


def _build_recommended_modules(
    shared_modules: dict[str, list[str]],
    depends_on_by_module: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for module_name, repos in shared_modules.items():
        if not repos:
            continue
        depends_on = sorted(depends_on_by_module.get(module_name, set())) if depends_on_by_module else []
        recommendations.append(
            {
                "module": module_name,
                "repo_count": len(repos),
                "repo_ids": sorted(repos),
                "depends_on_count": len(depends_on),
                "depends_on": depends_on,
            }
        )

    return sorted(
        recommendations,
        key=lambda item: (-item["repo_count"], -item["depends_on_count"], item["module"]),
    )


def _append_warning(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def _sorted_repo_paths(repo_paths: dict[str, str]) -> dict[str, str]:
    return {repo_id: repo_paths[repo_id] for repo_id in sorted(repo_paths)}


def _read_index_payload(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    existing = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(existing, list):
        raise ValueError(f"invalid manifest index format: {path}")
    payload: list[dict[str, Any]] = []
    for item in existing:
        if not isinstance(item, dict):
            continue
        payload.append(item)
    return payload


def _write_json_lines(path: Path, payload: dict[str, Any]) -> None:
    _ensure_non_symlink_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload) + "\n")


def _build_candidate_manifest_index_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    module_names = sorted({str(item.get("module_name", "")) for item in entries if isinstance(item, dict)})
    module_manifest_paths = {
        item.get("module_name", ""): str(item.get("manifest_path", ""))
        for item in entries
        if isinstance(item, dict) and item.get("module_name")
    }
    return {
        "generated_at": utc_now_iso(),
        "module_count": len(module_names),
        "manifest_count": len(entries),
        "module_names": module_names,
        "module_manifest_paths": module_manifest_paths,
    }


def _validate_candidate_name_regex(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"invalid candidate-name regex: {pattern}") from exc


def _iter_repo_python_files(repo_path: Path) -> list[Path]:
    files: list[Path] = []
    src_root = repo_path / "src"
    if not src_root.exists():
        return files
    for file_path in src_root.rglob("*.py"):
        if file_path.is_file():
            files.append(file_path)
    return files


def _extract_imports_from_python(code: str) -> set[str]:
    imports: set[str] = set()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(str(exc)) from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports (indicated by node.level > 0)
            if node.level > 0:
                continue
            if node.module:
                imports.add(node.module)
    return imports


def _ensure_non_symlink_path(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.exists() and current.is_symlink():
            raise ValueError(f"path component is a symlink: {current}")
        current = current.parent


def _resolve_candidate_dependency(
    imported_name: str,
    known_modules: set[str],
    current_module: str,
) -> str | None:
    parts = imported_name.split(".")
    if not parts:
        return None
    candidate = parts[0]
    if candidate == current_module:
        return None
    if candidate in known_modules:
        return candidate
    return None


def _find_repo_module_dependencies(
    repo_path: Path,
) -> tuple[dict[str, set[str]], list[dict[str, str]]]:
    modules = _find_repo_modules(repo_path)
    if not modules:
        return {}, []

    dependencies: dict[str, set[str]] = {module: set() for module in modules}
    warnings: list[dict[str, str]] = []

    for py_file in _iter_repo_python_files(repo_path):
        try:
            imports = _extract_imports_from_python(py_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            warnings.append(
                {
                    "repo_file": str(py_file),
                    "reason": "python-parse-error",
                    "detail": str(exc),
                }
            )
            continue

        module_name = py_file.relative_to(repo_path).parts
        if len(module_name) < 2 or module_name[0] != "src":
            continue
        current_module = module_name[1]
        if current_module not in modules:
            continue
        for imported in imports:
            dep = _resolve_candidate_dependency(imported, modules, current_module)
            if dep is not None:
                dependencies[current_module].add(dep)

    return dependencies, warnings


def build_module_manifest_payload(module_name: str, repo_ids: list[str]) -> dict[str, Any]:
    sorted_repos = sorted(repo_ids)
    return {
        "schema_version": SCAN_SHARED_REPOS_SCHEMA_VERSION,
        "repo_patterns": sorted_repos,
        "default_ref": "HEAD",
        "repo_ref_overrides": {},
        "repo_runner_overrides": {},
        "repo_command_overrides": {},
        "repo_env_profile_overrides": {},
        "matched_repos": sorted_repos,
    }


def build_scan_candidates(
    shared_modules: dict[str, list[str]],
    *,
    module_prefix: str = SCAN_SHARED_REPOS_DEFAULT_MODULE_PREFIX,
    depends_on_by_module: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    used_names: set[str] = set()

    for module_name, repos in sorted(shared_modules.items(), key=lambda item: item[0]):
        if not repos:
            continue
        sorted_repos = sorted(repos)
        prefix = _normalize_candidate_module_name(module_prefix)
        base = _normalize_candidate_module_name(module_name)
        candidate_name = _build_scannable_candidate_name(f"{prefix}-{base}-{len(sorted_repos)}", used_names)
        used_names.add(candidate_name)

        depends_on = sorted(depends_on_by_module.get(module_name, set())) if depends_on_by_module else []

        manifest_template = build_module_manifest_payload(module_name, sorted_repos)
        candidates.append(
            {
                "module": module_name,
                "module_name": candidate_name,
                "repo_ids": sorted_repos,
                "repo_count": len(sorted_repos),
                "depends_on_count": len(depends_on),
                "depends_on": depends_on,
                "manifest_template": manifest_template,
            }
        )

    return sorted(
        candidates,
        key=lambda item: (
            -item["repo_count"],
            -item["depends_on_count"],
            item["module"],
            item["module_name"],
        ),
    )


def _candidate_manifest_path(output_dir: Path, module_name: str) -> Path:
    return output_dir / module_name / "manifest.json"


def _read_json_dict(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"manifest content must be a JSON object: {path}")
    return payload


def _write_manifest(path: Path, payload: dict[str, Any]) -> None:
    _ensure_non_symlink_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def materialize_scan_candidate_manifest(
    candidate: dict[str, Any],
    *,
    output_dir: Path,
    dry_run: bool = False,
    update_index: bool = True,
) -> dict[str, Any]:
    module_name = str(candidate.get("module_name", "")).strip()
    repo_ids = candidate.get("repo_ids", [])
    if not module_name:
        raise ValueError("candidate module_name cannot be empty")
    if not isinstance(repo_ids, list):
        raise ValueError("candidate repo_ids must be a list")
    if not isinstance(module_name, str) or "/" in module_name or "\\" in module_name or ".." in module_name:
        raise ValueError(f"invalid module_name: {module_name}")

    manifest_path = _candidate_manifest_path(output_dir, module_name)
    manifest_before: dict[str, Any] | None = None
    if manifest_path.exists():
        manifest_before = _read_json_dict(manifest_path)
    manifest_payload = candidate.get("manifest_template")
    if not isinstance(manifest_payload, dict):
        manifest_payload = build_module_manifest_payload(
            str(candidate.get("module", "")), [str(repo_id) for repo_id in repo_ids]
        )

    if not dry_run and manifest_before is not None:
        if manifest_before != manifest_payload:
            raise ValueError(f"manifest conflict for {module_name}; existing file differs: {manifest_path}")

    if not dry_run:
        _write_manifest(manifest_path, manifest_payload)

    index_path = output_dir / SCAN_SHARED_REPOS_MANIFEST_INDEX_FILENAME
    existing_index = _read_index_payload(index_path) if update_index else []
    index_entry = {
        "module_name": module_name,
        "manifest_path": str(manifest_path),
        "repo_count": len(repo_ids),
        "generated_at": utc_now_iso(),
    }
    next_index = deepcopy(existing_index)
    if update_index:
        updated = False
        for entry in next_index:
            if not isinstance(entry, dict):
                continue
            if entry.get("module_name") == module_name:
                entry.update(deepcopy(index_entry))
                updated = True
                break
        if not updated:
            next_index.append(index_entry)
        next_index = sorted(next_index, key=lambda item: str(item.get("module_name")))

    index_summary_path = output_dir / SCAN_SHARED_REPOS_MANIFEST_INDEX_SUMMARY_FILENAME
    index_summary_payload = _build_candidate_manifest_index_summary(next_index if update_index else existing_index)

    audit_path = output_dir / SCAN_SHARED_REPOS_MANIFEST_AUDIT_FILENAME
    _ensure_non_symlink_path(manifest_path)
    _ensure_non_symlink_path(index_path)
    _ensure_non_symlink_path(index_summary_path)
    _ensure_non_symlink_path(audit_path)
    audit_entry = {
        "event": "manifest-materialization",
        "timestamp": utc_now_iso(),
        "module": str(candidate.get("module", "")),
        "module_name": module_name,
        "manifest_path": str(manifest_path),
        "repo_ids": sorted([str(repo_id) for repo_id in repo_ids]),
        "dry_run": dry_run,
        "index_updated": bool(update_index),
    }

    if not dry_run and update_index:
        index_path.write_text(json.dumps(next_index, indent=2) + "\n", encoding="utf-8")
        index_summary_path.write_text(json.dumps(index_summary_payload, indent=2) + "\n", encoding="utf-8")
        _write_json_lines(audit_path, audit_entry)

    result = {
        "module": str(candidate.get("module", "")),
        "module_name": module_name,
        "manifest_path": str(manifest_path),
        "repos": sorted([str(repo_id) for repo_id in repo_ids]),
        "manifest_payload": manifest_payload,
        "manifest_after": manifest_payload,
        "dry_run": dry_run,
        "manifest_before": manifest_before,
        "index_before": existing_index if update_index else None,
        "index_after": next_index if update_index else None,
        "index_summary": index_summary_payload,
        "index_summary_path": str(index_summary_path),
    }

    return result


def _resolve_candidate_inclusion(
    *,
    candidates: bool,
    omit_candidates: bool,
) -> bool:
    if candidates and omit_candidates:
        raise ValueError("cannot set both --candidates and --omit-candidates")
    return bool(candidates) and not omit_candidates


=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
def _repo_id_from_path(repo_path: Path) -> str:
    return sanitize_repo_id(repo_path.name)


<<<<<<< HEAD
def _validate_excluded_repo_ids(exclude_repos: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for repo_name in exclude_repos:
        candidate = repo_name.strip()
        if not candidate:
            raise ValueError("exclude repo id cannot be blank")
        sanitized = sanitize_repo_id(candidate)
        if sanitized != candidate:
            raise ValueError(f"invalid repo id: {candidate}")
        normalized.add(sanitized)
    return normalized


def _collect_candidate_repos(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if not root.is_dir():
        return []
    return sorted([entry for entry in root.iterdir() if entry.is_dir() and not entry.name.startswith(".")])


def _resolve_worktree_roots() -> list[Path]:
    base_root = phenotype_root()
    return sorted([entry for entry in base_root.iterdir() if entry.is_dir() and entry.name.endswith("-wtrees")])


def _collect_worktree_repos(root: Path) -> list[Path]:
    if root.name == "src":
        return [root.parent]
    if root.name.endswith("-wtrees"):
        return _collect_candidate_repos(root)
    if (root / "src").exists():
        return [root]
    return _collect_candidate_repos(root)


def _repos_root_metadata(
    repos_root: Path | None,
    root_mode: str,
) -> tuple[Path, list[Path], str, list[str]]:
    if root_mode not in {SCAN_SHARED_REPOS_ROOT_MODE_REPOS, SCAN_SHARED_REPOS_ROOT_MODE_WORKTREES}:
        raise ValueError(
            f"repos_root_mode must be one of: {SCAN_SHARED_REPOS_ROOT_MODE_REPOS}, {SCAN_SHARED_REPOS_ROOT_MODE_WORKTREES}"
        )

    warnings: list[str] = []
    phenotype = phenotype_root()
    base_root = repos_root if repos_root is not None else None
    if base_root is None:
        if root_mode == SCAN_SHARED_REPOS_ROOT_MODE_REPOS:
            base_root = phenotype / "repos"
            hint = (
                f"defaulted repos_root to {base_root} using repos_root_mode={root_mode}; pass --repos-root to override"
            )
            return base_root, _collect_candidate_repos(base_root), hint, []

        worktree_roots = _resolve_worktree_roots()
        candidate_paths: list[Path] = []
        for worktree_root in worktree_roots:
            candidate_paths.extend(_collect_worktree_repos(worktree_root))
        hint = "resolved worktree scan roots from phenotype_root/*-wtrees"
        if not candidate_paths:
            _append_warning(warnings, "no worktree roots found under phenotype_root; verify -wtrees directories exist")
        return phenotype, sorted(candidate_paths), hint, warnings

    explicit_root = base_root.expanduser().resolve()
    if not explicit_root.exists():
        _append_warning(warnings, f"repos_root does not exist: {explicit_root}")
        return explicit_root, [], f"explicit repos_root provided but path missing: {explicit_root}", warnings
    if root_mode == SCAN_SHARED_REPOS_ROOT_MODE_REPOS:
        hint = f"scanning repos mode from explicit root: {explicit_root}"
        if phenotype not in explicit_root.parents and explicit_root != phenotype:
            _append_warning(
                warnings,
                "scan configured outside THGENT_PHENOTYPE_ROOT; explicit repo path provenance retained in result",
            )
        return explicit_root, _collect_candidate_repos(explicit_root), hint, warnings

    hint = f"scanning worktrees from explicit root: {explicit_root}"
    if explicit_root.name.endswith("-wtrees"):
        _append_warning(warnings, "scanning nested worktree directory with -wtrees suffix")
    if (explicit_root / "src").exists() and explicit_root.name != "src":
        hint = f"explicit worktree-style repo root provided: {explicit_root}"
    return explicit_root, _collect_worktree_repos(explicit_root), hint, warnings


=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
<<<<<<< HEAD
        # Verify directory is a git checkout
        if not (repo_path / ".git").exists():
            continue
=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
        selected.append(repo_path)
    return selected


<<<<<<< HEAD
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
    return {module_name: sorted(repos) for module_name, repos in repo_modules.items() if len(repos) >= min_repo_count}


=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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


<<<<<<< HEAD
def scan_shared_modules_across_repos(
    repos_root: Path | None = None,
    *,
    exclude_repos: set[str] | None = None,
    min_repo_count: int = 2,
    repos_root_mode: str | None = None,
    candidate_name_regex: str | None = None,
    candidates: bool = False,
    omit_candidates: bool = False,
) -> dict[str, Any]:
    if min_repo_count < 2:
        raise ValueError("min_repo_count must be at least 2")

    root_mode = repos_root_mode or SCAN_SHARED_REPOS_ROOT_MODE_REPOS
    root, candidate_paths, root_mode_hint, warnings = _repos_root_metadata(repos_root, root_mode)
    if not candidate_paths:
        return {
            "scan_schema_version": SCAN_SHARED_REPOS_SCHEMA_VERSION,
            "repos_root": str(root),
            "repos_root_mode": root_mode,
            "root_mode_hint": root_mode_hint,
            "warnings": warnings,
            "repo_paths": {},
            "shared_modules": {},
            "shared_count": 0,
            "module_count": 0,
            "repo_count": 0,
            "excluded_repos": sorted(DEFAULT_EXCLUDED_REPOS),
            "examined_repos": [],
            "min_repo_count": min_repo_count,
            "module_candidates": [],
            "recommended_modules": [],
        }

    excluded = _validate_excluded_repo_ids(exclude_repos or set())
    effective_excludes = sorted(DEFAULT_EXCLUDED_REPOS | excluded)
    repo_modules: dict[str, set[str]] = {}
    repo_dependencies: dict[str, set[str]] = {}
    warnings = list(warnings)

    if candidate_name_regex is not None:
        compiled_name_regex = _validate_candidate_name_regex(candidate_name_regex)
    else:
        compiled_name_regex = None

    examined_repos: list[str] = []
    repo_paths: dict[str, str] = {}
    for repo_path in candidate_paths:
        repo_id = _repo_id_from_path(repo_path)
        if repo_id in effective_excludes:
            continue
        examined_repos.append(repo_id)
        repo_paths[repo_id] = str(repo_path)
        modules = _find_repo_modules(repo_path)
        for module_name in modules:
            repo_modules.setdefault(module_name, set()).add(repo_id)

        module_dependencies, dep_warnings = _find_repo_module_dependencies(repo_path)
        for dep_module, deps in module_dependencies.items():
            repo_dependencies.setdefault(dep_module, set()).update(deps)
        for dep_warning in dep_warnings:
            _append_warning(warnings, f"{dep_warning['repo_file']}: {dep_warning['reason']}")

    shared_modules = _collect_shared_modules(repo_modules, min_repo_count=min_repo_count)
    include_candidates = _resolve_candidate_inclusion(
        candidates=candidates,
        omit_candidates=omit_candidates,
    )
    candidates = (
        [] if not include_candidates else build_scan_candidates(shared_modules, depends_on_by_module=repo_dependencies)
    )
    if compiled_name_regex is not None:
        if not include_candidates:
            _append_warning(warnings, "candidate-name-regex ignored when candidates are omitted")
        else:
            candidates = [item for item in candidates if compiled_name_regex.search(str(item.get("module", "")))]

    recommendations = _build_recommended_modules(shared_modules, depends_on_by_module=repo_dependencies)[
        :SCAN_SHARED_REPOS_RECOMMENDED_MODULE_COUNT_LIMIT
    ]

    return {
        "scan_schema_version": SCAN_SHARED_REPOS_SCHEMA_VERSION,
        "repos_root": str(root),
        "repos_root_mode": root_mode,
        "shared_modules": shared_modules,
        "root_mode_hint": root_mode_hint,
        "warnings": warnings,
        "repo_paths": _sorted_repo_paths(repo_paths),
        "shared_count": len(shared_modules),
        "module_count": len(repo_modules),
        "repo_count": len(examined_repos),
        "excluded_repos": effective_excludes,
        "examined_repos": examined_repos,
        "min_repo_count": min_repo_count,
        "module_candidates": candidates,
        "recommended_modules": recommendations,
    }


def materialize_module_candidate_manifest(
    module: str,
    *,
    repos_root: Path | None = None,
    repos_root_mode: str | None = None,
    repos: list[str] | None = None,
    min_repo_count: int = 2,
    module_prefix: str = SCAN_SHARED_REPOS_DEFAULT_MODULE_PREFIX,
    output_dir: Path | None = None,
    dry_run: bool = False,
    update_index: bool = True,
) -> dict[str, Any]:
    if not module.strip():
        raise ValueError("module name cannot be empty")
    if min_repo_count < 2:
        raise ValueError("min_repo_count must be at least 2")

    state = scan_shared_modules_across_repos(
        repos_root=repos_root,
        repos_root_mode=repos_root_mode,
        min_repo_count=min_repo_count,
    )
    shared_modules = state.get("shared_modules")
    if not isinstance(shared_modules, dict) or module not in shared_modules:
        raise ValueError(f"module {module} is not shared at min_repo_count={min_repo_count}")

    selected_repos = sorted(shared_modules[module])
    if repos:
        selected_repos = sorted(set(repos) & set(selected_repos))
        if len(selected_repos) < min_repo_count:
            raise ValueError(
                f"module {module} has insufficient pinned repos after filtering: {len(selected_repos)} < {min_repo_count}"
            )

    candidates = build_scan_candidates({module: selected_repos}, module_prefix=module_prefix)
    if not candidates:
        raise ValueError(f"module {module} has no qualifying repos")
    candidate = candidates[0]
    target_output_dir = (output_dir or module_manifests_root()).expanduser().resolve()
    return materialize_scan_candidate_manifest(
        candidate,
        output_dir=target_output_dir,
        dry_run=dry_run,
        update_index=update_index,
    )


=======
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
<<<<<<< HEAD
) -> tuple[str | None, str | None, dict[str, str] | None]:
=======
) -> tuple[str | None, str | None, str | None]:
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
<<<<<<< HEAD
        profile_env = get_env_profile(target=lock.target_name)
    elif not selected_profile.strip():
        profile_env = {}
=======
        if env_profile is None:
            profile_env = get_env_profile(target=lock.target_name)
        else:
            profile_env = None
    elif not selected_profile.strip():
        profile_env = None
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
<<<<<<< HEAD
            raise ValueError("--all-repos requires --runner and --command or module-level overrides for each repo")
=======
            raise ValueError(
                "--all-repos requires --runner and --command or module-level overrides for each repo"
            )
>>>>>>> 1f1db2e462 (feat: add module-driven phench target composition)
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
