"""Generate a cross-repo reusable-module inventory for sibling repos.

This scan intentionally excludes known excluded repos and worktree mirrors,
then reports:
- duplicate top-level filenames by count and location
- duplicate relative paths by count and location
- candidate shared utility modules
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


_MIRROR_SUFFIXES = ("-composite-actions", "-governance", "-upstream")


def _canonical_repo_name(name: str) -> str:
    for suffix in _MIRROR_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _is_candidate_repo(path: Path, excluded: set[str]) -> bool:
    if not path.is_dir() or not (path / "AGENTS.md").exists():
        return False
    name = path.name
    if name in excluded or name.endswith("-wtrees") or name.endswith("-wtress"):
        return False
    return True


def _collect_py_modules(repo_root: Path) -> dict[str, list[str]]:
    modules: dict[str, list[str]] = defaultdict(list)
    for file in repo_root.glob("**/*.py"):
        if "site-packages" in file.parts or ".venv" in file.parts:
            continue
        if file.name.startswith("."):
            continue
        rel = file.relative_to(repo_root).as_posix()
        modules[file.name].append(rel)
        modules[f"REL::{rel}"] .append(rel)
    return modules


def audit(repos_root: Path, excluded: set[str]) -> dict[str, Any]:
    repo_paths = sorted(
        (path for path in repos_root.iterdir() if _is_candidate_repo(path, excluded)),
        key=lambda p: p.name,
    )
    canonical_repo_paths: dict[str, Path] = {}
    for repo_path in repo_paths:
        canonical = _canonical_repo_name(repo_path.name)
        canonical_repo_paths.setdefault(canonical, repo_path)
    repo_names = sorted(canonical_repo_paths.values(), key=lambda p: p.name)

    basename_count: dict[str, list[tuple[str, list[str]]]] = defaultdict(list)
    rel_count: dict[str, list[tuple[str, list[str]]]] = defaultdict(list)
    utility_candidates: dict[str, list[tuple[str, list[str]]]] = defaultdict(list)

    for repo_path in repo_names:
        modules = _collect_py_modules(repo_path)
        for key, rels in modules.items():
            if key.startswith("REL::"):
                continue
            basename_count[key].append((repo_path.name, rels))

            for rel in rels:
                rel_count[rel].append((repo_path.name, [rel]))
                if rel.endswith("/utils.py") or rel.endswith("/util.py"):
                    utility_candidates[rel].append((repo_path.name, [rel]))

    duplicate_names = {
        name: entries
        for name, entries in sorted(basename_count.items())
        if len(entries) >= 2
    }
    duplicate_rels = {
        rel: entries
        for rel, entries in sorted(rel_count.items())
        if rel.startswith("src/") and len(entries) >= 2
    }
    utility_hits = {
        rel: entries
        for rel, entries in sorted(utility_candidates.items())
        if len(entries) >= 2
    }

    return {
        "repos_scanned": [path.name for path in repo_names],
        "counted_repos": len(repo_names),
        "excluded_repos": sorted(excluded),
        "top_level_filename_dupes": sorted(duplicate_names.items()),
        "relative_path_dupes": sorted(duplicate_rels.items()),
        "shared_utilities": sorted(utility_hits.items()),
    }


def write_reports(out_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "shared-module-audit.json"
    md_path = out_dir / "shared-module-audit.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Reusable Module Audit", ""]
    lines.append(f"- Repos scanned: {payload['counted_repos']}")
    lines.append(f"- Repositories: {', '.join(payload['repos_scanned'])}")
    lines.append("")
    lines.append("## Shared utility modules")
    if payload["shared_utilities"]:
        for path, owners in payload["shared_utilities"]:
            names = ", ".join(owner for owner, _ in owners)
            lines.append(f"- `{path}` across: {names}")
    else:
        lines.append("- None found above threshold")

    lines.append("")
    lines.append("## Duplicate basenames (>=2 repos)")
    for name, owners in payload["top_level_filename_dupes"][:200]:
        repos = ", ".join(owner for owner, _ in owners)
        sample_paths = " | ".join(f"{owner}:{items[0]}" for owner, items in owners)
        lines.append(f"- `{name}`: {repos} ({sample_paths})")

    lines.append("")
    lines.append("## Duplicate relative paths (src/*, >=2 repos)")
    for rel, owners in payload["relative_path_dupes"][:200]:
        repos = ", ".join(owner for owner, _ in owners)
        lines.append(f"- `{rel}`: {repos}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    repos_root = root.parent
    excluded = {"4sgm", "trace", "parpour", "civ"}

    payload = audit(repos_root, excluded)
    report_root = root / "docs" / "reports"
    report_root.mkdir(parents=True, exist_ok=True)
    json_path, md_path = write_reports(report_root / "shared-module-audit", payload)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
