#!/usr/bin/env python3
"""LOC and complexity collector for thegent.

Collects:
- Total Python LOC in src/thegent/
- LOC per top-level module
- Top-5 largest files
- Functions exceeding 40 lines

Writes JSON output to .quality/loc-metrics.json with timestamp.
Uses only stdlib + optional tokei subprocess.

# @trace WL-135 B90-W2-C4
"""

from __future__ import annotations

import ast
import orjson as json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src" / "thegent"
OUTPUT_PATH = ROOT / ".quality" / "loc-metrics.json"

MAX_FUNCTION_LINES = 40


def _count_loc_ast(path: Path) -> int:
    """Count non-blank, non-comment lines via AST source read."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    lines = source.splitlines()
    return sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))


def _collect_oversized_functions(path: Path) -> list[dict]:
    """Return list of functions >MAX_FUNCTION_LINES in the given file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return []

    oversized = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef | ast.AsyncFunctionDef)):
            start = node.lineno
            end = node.end_lineno or start
            length = end - start + 1
            if length > MAX_FUNCTION_LINES:
                oversized.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "function": node.name,
                        "start_line": start,
                        "end_line": end,
                        "lines": length,
                    }
                )
    return oversized


def _try_tokei(src: Path) -> dict | None:
    """Attempt to collect LOC via tokei if installed. Returns None if not available."""
    result = subprocess.run(
        ["which", "tokei"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    tokei_result = subprocess.run(
        ["tokei", str(src), "--output", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if tokei_result.returncode != 0:
        return None

    try:
        data = json.loads(tokei_result.stdout)
        python_data = data.get("Python", {})
        return {
            "source": "tokei",
            "total_loc": python_data.get("code", 0),
            "blanks": python_data.get("blanks", 0),
            "comments": python_data.get("comments", 0),
        }
    except (json.JSONDecodeError, KeyError):
        return None


def collect_metrics() -> dict:
    """Collect LOC metrics from src/thegent/ and return structured dict."""
    if not SRC.exists():
        msg = f"Source directory does not exist: {SRC}"
        raise FileNotFoundError(msg)

    all_py_files = sorted(SRC.rglob("*.py"))

    # Per-file LOC
    file_locs: list[dict] = []
    for path in all_py_files:
        loc = _count_loc_ast(path)
        file_locs.append(
            {
                "file": str(path.relative_to(ROOT)),
                "loc": loc,
            }
        )

    total_loc = sum(f["loc"] for f in file_locs)

    # Per top-level module LOC
    by_module: dict[str, int] = {}
    for entry in file_locs:
        parts = Path(entry["file"]).parts
        # parts = ("src", "thegent", "<module>", ...)
        if len(parts) >= 3:
            module = parts[2]
        else:
            module = "_root"
        by_module[module] = by_module.get(module, 0) + entry["loc"]

    # Top-5 largest files
    top5 = sorted(file_locs, key=lambda x: x["loc"], reverse=True)[:5]

    # Oversized functions
    oversized_functions: list[dict] = []
    for path in all_py_files:
        oversized_functions.extend(_collect_oversized_functions(path))

    # Try tokei for cross-check
    tokei_summary = _try_tokei(SRC)

    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "source_dir": str(SRC.relative_to(ROOT)),
        "total_files": len(all_py_files),
        "total_loc": total_loc,
        "by_module": by_module,
        "top5_largest_files": top5,
        "oversized_functions_count": len(oversized_functions),
        "oversized_functions": oversized_functions[:20],  # cap output
        "tokei_summary": tokei_summary,
        "thresholds": {
            "max_function_lines": MAX_FUNCTION_LINES,
        },
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    metrics = collect_metrics()

    OUTPUT_PATH.write_text(json.dumps(metrics, indent=2).decode().decode())

    print(f"LOC metrics written to {OUTPUT_PATH}")
    print(f"  Total LOC   : {metrics['total_loc']}")
    print(f"  Total files : {metrics['total_files']}")
    print(f"  Oversized fns: {metrics['oversized_functions_count']} (>{MAX_FUNCTION_LINES} lines)")
    print("  Top-5 largest files:")
    for entry in metrics["top5_largest_files"]:
        print(f"    {entry['loc']:>6} LOC  {entry['file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
