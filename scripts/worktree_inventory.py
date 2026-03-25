#!/usr/bin/env python3
"""Inventory git worktrees and classify governance conformance."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    return Path(out)


def _worktrees() -> list[Path]:
    out = subprocess.check_output(["git", "worktree", "list", "--porcelain"], text=True)
    paths: list[Path] = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line.split(" ", 1)[1]))
    return paths


def main() -> int:
    repo_root = _repo_root()
    repo_name = repo_root.name
    wt_root = Path(os.environ.get("THGENT_WORKTREE_ROOT", str(repo_root / ".worktrees")))
    name_re = re.compile(rf"^{re.escape(repo_name)}--[A-Za-z0-9._-]+$")

    rows: list[dict[str, object]] = []
    for wt in _worktrees():
        if wt == repo_root:
            continue
        in_root = str(wt).startswith(str(wt_root) + os.sep)
        name_ok = bool(name_re.match(wt.name))
        rows.append(
            {
                "path": str(wt),
                "in_required_root": in_root,
                "name_conformant": name_ok,
                "conformant": bool(in_root and name_ok),
            }
        )

    payload = {
        "repo_root": str(repo_root),
        "required_root": str(wt_root),
        "total": len(rows),
        "conformant": sum(1 for r in rows if r["conformant"]),
        "nonconformant": sum(1 for r in rows if not r["conformant"]),
        "rows": rows,
    }
    out_path = repo_root / "artifacts" / "governance" / "worktree_inventory.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
