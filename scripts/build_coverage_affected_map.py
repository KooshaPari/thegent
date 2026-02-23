#!/usr/bin/env python3
"""Build source_file -> [test_files] map from .coverage for P7 coverage-based test selection.

Run after: pytest --cov=src --cov-context=test -q
Output: HOOK_CACHE_DIR/coverage_affected_map.json

Usage:
  python scripts/build_coverage_affected_map.py
  # or: task coverage:map (if task added)
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path


def _ctx_to_test_file(ctx: str, root: Path) -> str | None:
    """Extract test file path from context string. Returns None if not a test context."""
    if not ctx or ctx.isspace():
        return None
    # Format 1: "tests/test_foo.py::test_bar" (pytest-cov)
    if "::" in ctx:
        tf = ctx.split("::", maxsplit=1)[0]
        if (root / tf).exists():
            return tf
        return None
    # Format 2: "tests.test_foo.test_bar" or "tests.test_foo.TestClass.test_baz"
    parts = ctx.split(".")
    for i, p in enumerate(parts):
        if p == "tests" and i + 1 < len(parts):
            test_mod = parts[i + 1]
            tf = f"tests/{test_mod}.py"
            if (root / tf).exists():
                return tf
            return None
        if p.startswith("test_") and (root / "tests" / f"{p}.py").exists():
            return f"tests/{p}.py"
    return None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    cov_file = root / ".coverage"
    if not cov_file.exists():
        print("No .coverage file. Run: pytest --cov=src --cov-context=test -q", file=os.sys.stderr)
        return 1

    cache_dir = Path(os.environ.get("HOOK_CACHE_DIR") or tempfile.gettempdir()) / f"claude-hook-cache-{os.getuid()}"
    out_path = cache_dir / "coverage_affected_map.json"

    conn = sqlite3.connect(cov_file)
    try:
        files = {r[0]: r[1] for r in conn.execute("SELECT id, path FROM file")}
        # Context table may be empty if coverage run without dynamic_context
        try:
            contexts = {r[0]: r[1] for r in conn.execute("SELECT id, context FROM context")}
        except sqlite3.OperationalError:
            contexts = {}
        file_to_contexts: dict[int, set[int]] = {}
        # line_bits: (file_id, context_id, numbits); arc: (file_id, context_id, fromno, tono)
        try:
            for row in conn.execute("SELECT file_id, context_id FROM line_bits"):
                fid, cid = row
                file_to_contexts.setdefault(fid, set()).add(cid)
        except sqlite3.OperationalError:
            pass
        try:
            for row in conn.execute("SELECT file_id, context_id FROM arc"):
                fid, cid = row
                file_to_contexts.setdefault(fid, set()).add(cid)
        except sqlite3.OperationalError:
            pass
    finally:
        conn.close()

    source_to_tests: dict[str, list[str]] = {}
    for fid, path in files.items():
        if "tests/" in path or "__pycache__" in path or path.endswith("conftest.py"):
            continue
        try:
            rel = os.path.relpath(path, root) if path.startswith(str(root)) else path
        except ValueError:
            continue
        cids = file_to_contexts.get(fid, set())
        test_files: set[str] = set()
        for cid in cids:
            ctx = contexts.get(cid, "")
            tf = _ctx_to_test_file(ctx, root)
            if tf:
                test_files.add(tf)

        if test_files:
            source_to_tests[rel] = sorted(test_files)

    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(source_to_tests, f, indent=0, sort_keys=True)

    print(f"Wrote {len(source_to_tests)} source->test mappings to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
