"""Scan sibling repos for reusable tooling/workflow modules.

This tool is designed for fast, repeatable cross-repo standardization planning.
It intentionally focuses on:
- scripts/ (all files)
- .github/scripts/
- .github/workflows/
- tools/
- top-level Taskfile/taskfile files (both common casing variants)

Exclusions are tuned for Phenotype workspace: worktrees/backups/archives/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_EXCLUDE_PATTERNS = [
    "*worktree*",
    "*wtrees*",
    "*wtress*",
    "*archive*",
    "*backup*",
    "*.git",
    ".git",
]

IGNORE_DIR_PARTS = {
    ".venv",
    "node_modules",
    "vendor",
    "target",
    "dist",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    ".git-cache",
}

TARGET_ROOT_DIRS = ["scripts", ".github/scripts", ".github/workflows", "tools"]
TARGET_TASK_FILES = [
    "Taskfile.yml",
    "taskfile.yml",
    "Taskfile.yaml",
    "taskfile.yaml",
]

_SPLIT_EXCLUDE_PARTS = {"tests", "fixtures", "README.md"}
_MAX_HASH_VARIANTS_FOR_PHASE1 = 1
_MIN_REPO_COUNT_PHASE1 = 4
_MIN_REPO_COUNT_PHASE2 = 5
_MAX_HASH_VARIANTS_PHASE2 = 3


@dataclass
class FileFingerprint:
    repo: str
    path: str
    hash: str
    size: int


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _safe_name(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9._-]+$", value))


def _is_candidate_repo(path: Path, explicit_include_hidden: bool = True) -> bool:
    if not path.is_dir():
        return False

    if not (path / "AGENTS.md").exists():
        return False

    if not explicit_include_hidden and path.name.startswith("."):
        return False

    for pattern in REPO_EXCLUDE_PATTERNS:
        if path.match(pattern):
            return False

    return True


def _should_skip_relative(relative: Path) -> bool:
    parts = list(relative.parts)
    if set(parts).intersection(IGNORE_DIR_PARTS):
        return True

    # Skip internal git cache trees that are repo-local artifacts.
    if any(part == ".git" for part in parts):
        return True

    return False


def _collect_repo_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []

    # Explicit top-level taskfile variants.
    for taskfile in TARGET_TASK_FILES:
        if (repo_root / taskfile).exists():
            files.append(repo_root / taskfile)

    for rel_root in TARGET_ROOT_DIRS:
        root_dir = repo_root / rel_root
        if not root_dir.exists():
            continue

        for path in root_dir.rglob("*"):
            if not path.is_file():
                continue

            rel = path.relative_to(repo_root)
            if _should_skip_relative(rel):
                continue

            # Skip dotfiles in tooling trees (e.g. .DS_Store).
            if not _safe_name(path.name) and path.name.startswith("."):
                continue

            files.append(path)

    # Remove duplicates if a path is repeated by construction.
    return sorted(set(files), key=lambda p: str(p))


def _build_split_plan(
    duplicate_path_groups: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    candidates = sorted(
        duplicate_path_groups,
        key=lambda item: (item["count"], len(item["sha"]), item["path"]),
        reverse=True,
    )

    phase1: list[dict[str, Any]] = []
    phase2: list[dict[str, Any]] = []

    for item in candidates:
        if item["count"] < 2:
            continue

        path = item["path"]
        parts = set(path.split("/"))
        if _SPLIT_EXCLUDE_PARTS.intersection(parts):
            continue

        path_obj = Path(path)
        rel = path_obj.as_posix()
        if not (
            rel.startswith(".github/workflows/")
            or rel.startswith(".github/scripts/")
            or rel.startswith("scripts/")
            or rel.lower().startswith("taskfile")
        ):
            continue

        hash_variants = len(item["sha"])
        if item["count"] >= _MIN_REPO_COUNT_PHASE1 and hash_variants == _MAX_HASH_VARIANTS_FOR_PHASE1:
            phase1.append(
                {
                    "path": rel,
                    "repo_count": item["count"],
                    "hash_variants": hash_variants,
                    "reason": "identical file body in all observed repos",
                }
            )
            continue

        if (
            item["count"] >= _MIN_REPO_COUNT_PHASE2
            and hash_variants <= _MAX_HASH_VARIANTS_PHASE2
        ):
            phase2.append(
                {
                    "path": rel,
                    "repo_count": item["count"],
                    "hash_variants": hash_variants,
                    "reason": "high reuse with minor forks; standardize next",
                }
            )

    return {"phase1_safe_split": phase1[:20], "phase2_expand": phase2[:20]}


def audit_repos(repos_root: Path, excluded_repos: set[str] | None = None) -> dict[str, Any]:
    if excluded_repos is None:
        excluded_repos = set()

    repo_paths = sorted(
        path for path in repos_root.iterdir() if _is_candidate_repo(path)
        if path.name not in excluded_repos
    )

    fingerprint_by_hash: dict[str, list[FileFingerprint]] = defaultdict(list)
    fingerprint_by_path: dict[str, list[FileFingerprint]] = defaultdict(list)

    for repo in repo_paths:
        for file in _collect_repo_files(repo):
            try:
                rel = file.relative_to(repo).as_posix()
                digest = _sha256_file(file)
                size = file.stat().st_size
            except OSError:
                continue

            fp = FileFingerprint(repo=repo.name, path=rel, hash=digest, size=size)
            fingerprint_by_hash[digest].append(fp)
            fingerprint_by_path[rel].append(fp)

    duplicate_hash_groups = [
        {
            "sha256": sha,
            "count": len(entries),
            "size": entries[0].size,
            "basename": Path(entries[0].path).name,
            "owners": [f.repo for f in entries],
            "path_examples": [f"{entry.repo}:{entry.path}" for entry in entries[:3]],
            "paths": sorted({entry.path for entry in entries}),
        }
        for sha, entries in fingerprint_by_hash.items()
        if len(entries) >= 2
    ]

    duplicate_path_groups = [
        {
            "path": rel,
            "count": len(entries),
            "sha": sorted({entry.hash for entry in entries}),
            "owners": [entry.repo for entry in entries],
        }
        for rel, entries in fingerprint_by_path.items()
        if len(entries) >= 2
    ]

    duplicate_taskfiles = [
        {
            "name": name,
            "count": len(entries),
            "owners": sorted(entries),
        }
        for name, entries in {
            name: {
                f.repo for f in fingerprint_by_path.get(name, [])
            }
            for name in TARGET_TASK_FILES
        }.items()
        if len(entries) >= 2
    ]

    # Build a conservative reusable candidates list prioritizing same path with 3+ hits.
    path_candidates = [
        item
        for item in duplicate_path_groups
        if item["count"] >= 3
    ]

    split_plan = _build_split_plan(path_candidates)

    duplicate_hash_groups.sort(key=lambda item: item["count"], reverse=True)
    path_candidates.sort(key=lambda item: item["count"], reverse=True)

    return {
        "repos_scanned": [path.name for path in repo_paths],
        "counted_repos": len(repo_paths),
        "excluded_repos": sorted(excluded_repos),
        "duplicate_hash_groups": duplicate_hash_groups,
        "duplicate_path_groups": sorted(duplicate_path_groups, key=lambda item: (item["count"], item["path"]), reverse=True),
        "duplicate_taskfile_groups": duplicate_taskfiles,
        "sync_candidates": path_candidates,
        "split_plan": split_plan,
    }


def _group_sync_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in payload["sync_candidates"]:
        basename = Path(item["path"]).name
        grouped[basename].append(item)

    return {
        name: sorted(items, key=lambda x: x["count"], reverse=True)
        for name, items in grouped.items()
    }


def write_reports(output_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "reusable_tooling_audit.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Sibling Tooling & Workflow Reuse Audit",
        "",
        f"- Repos scanned: {payload['counted_repos']}",
        f"- Excluded repos: {', '.join(payload['excluded_repos']) if payload['excluded_repos'] else 'none'}",
        "",
        "## Top duplicate content groups (same hash, >=2 repos)",
        "",
        "| Hash | Basename | Repo count | Example paths |",
        "|---|---|---:|---|",
    ]

    for item in payload["duplicate_hash_groups"][:200]:
        examples = "<br/>".join(item["path_examples"])
        md_lines.append(
            f"| {item['sha256'][:10]}... | {item['basename']} | {item['count']} | {examples} |"
        )

    md_lines.extend(
        [
            "",
            "## Highest-confidence reusable file paths (same path exists in >=3 repos)",
            "",
            "| Path | Repo count |",
            "|---|---:|",
        ]
    )
    for item in payload["sync_candidates"][:200]:
        md_lines.append(f"| {item['path']} | {item['count']} |")

    if payload["duplicate_taskfile_groups"]:
        md_lines.extend(["", "## Taskfile name overlap", "", "| Name | Repo count |", "|---|---:|"])
        for item in payload["duplicate_taskfile_groups"]:
            if item["count"] >= 2:
                md_lines.append(f"| {item['name']} | {item['count']} |")

    md_lines.extend(
        [
            "",
            "## Suggested initial standardization split",
            "",
            "1. `Taskfile*` and workflow policy wrappers: low blast radius, high duplication.",
            "2. `.github/workflows` policy guards with shared contract semantics.",
            "3. `.github/scripts` and `scripts` utility clusters with proven stable hash overlap.",
        ]
    )

    md_lines.extend(
        [
            "",
            "## Minimal safe split (phase 1)",
            "",
            "| Path | Repo count | Hash variants | Why |",
            "|---|---:|---:|---|",
        ]
    )
    for item in payload["split_plan"]["phase1_safe_split"]:
        md_lines.append(
            f"| {item['path']} | {item['repo_count']} | {item['hash_variants']} | {item['reason']} |"
        )

    if payload["split_plan"]["phase2_expand"]:
        md_lines.extend(
            [
                "",
                "## Near-term expansion (phase 2)",
                "",
                "| Path | Repo count | Hash variants | Why |",
                "|---|---:|---:|---|",
            ]
        )
        for item in payload["split_plan"]["phase2_expand"]:
            md_lines.append(
                f"| {item['path']} | {item['repo_count']} | {item['hash_variants']} | {item['reason']} |"
            )

    if payload["split_plan"]["phase1_safe_split"] or payload["split_plan"]["phase2_expand"]:
        md_lines.extend(
            [
                "",
                "- Start phase 1 first because these files are bit-identical in 4+ repos.",
                "- Validate by dry-run sync on one pair of repos before broad rollout.",
            ]
        )

    md_path = output_dir / "reusable_tooling_audit.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    sync_manifest = _group_sync_manifest(payload)
    manifest_path = output_dir / "reusable_tooling_sync_manifest.json"
    manifest_path.write_text(json.dumps(sync_manifest, indent=2), encoding="utf-8")

    return json_path, md_path, manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repos-root",
        type=Path,
        default=Path(__file__).resolve().parents[1].parent,
        help="Root directory containing sibling repos.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "reports" / "reusable-tooling-audit",
        help="Output directory for audit outputs.",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["4sgm", "trace", "parpour", "civ"],
        help="Repos to exclude from scan.",
    )

    args = parser.parse_args()

    payload = audit_repos(args.repos_root, set(args.exclude))
    json_path, md_path, manifest_path = write_reports(args.output_dir, payload)

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
