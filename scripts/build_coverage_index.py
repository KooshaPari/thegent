#!/usr/bin/env python3
"""Build coverage index for WP-DX1 coverage-based test selection.

Maps source files -> test IDs that cover them. Run after:
  pytest --cov=thegent --cov-context=test ...

Output: coverage-index.json in project root.
Usage: python scripts/build_coverage_index.py [--output PATH]
"""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out_path = root / "coverage-index.json"
    if "--output" in sys.argv:
        i = sys.argv.index("--output")
        out_path = Path(sys.argv[i + 1])

    cov_file = root / ".coverage"
    if not cov_file.exists():
        print("No .coverage file. Run: pytest --cov=thegent ...", file=sys.stderr)
        return 1

    try:
        from coverage import Coverage
    except ImportError:
        print("coverage not installed. pip install coverage", file=sys.stderr)
        return 1

    cov = Coverage(data_file=str(cov_file))
    cov.load()
    data = cov.get_data()
    index: dict[str, list[str]] = {}

    for filepath in data.measured_files():
        # Normalize to project-relative
        try:
            rel = Path(filepath).resolve().relative_to(root)
        except ValueError, OSError:
            continue
        rel_str = str(rel).replace("\\", "/")
        if not rel_str.startswith("src/"):
            continue
        if "__pycache__" in rel_str or ".pyc" in rel_str:
            continue

        contexts: set[str] = set()
        try:
            ctx_by_line = data.contexts_by_lineno(filepath)
        except Exception:
            continue
        if ctx_by_line:
            for ctxs in ctx_by_line.values():
                contexts.update(ctxs)

        if contexts:
            # Convert test nodeids to test file paths for hook consumption
            test_files: set[str] = set()
            for ctx in contexts:
                if "::" in ctx:
                    # tests/test_foo.py::TestClass::test_method
                    parts = ctx.split("::")
                    test_files.add(parts[0])
                else:
                    test_files.add(ctx)
            index[rel_str] = sorted(test_files)

    with open(out_path, "w") as f:
        json.dump(index, f, indent=2)

    if not index:
        print(
            "Wrote empty index (no context data). Run: pytest --cov=thegent ... with conftest context.",
            file=sys.stderr,
        )
    else:
        print(f"Wrote {len(index)} file mappings to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
