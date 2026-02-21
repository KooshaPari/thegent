#!/usr/bin/env python3
"""Audit core->tooling import boundary compliance.

Core modules must not import from tooling (cli_dag, cli_tooling, impl_execution).
These CLI tooling modules should only be imported from CLI entry points, not from
core modules like agents/, mcp/, routing/, governance/, or orchestration/.

# @trace WL-136 B90-W3-C4
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLING_MODULES = [
    "thegent.cli.commands.cli_dag",
    "thegent.cli.commands.cli_tooling",
    "thegent.cli.commands.impl_execution",
]
CORE_DIRS = [
    "src/thegent/agents",
    "src/thegent/mcp",
    "src/thegent/routing",
    "src/thegent/governance",
    "src/thegent/orchestration",
]


def audit() -> list[dict]:
    """Scan core directories for tooling module imports.

    Returns:
        List of violation dicts with 'file' and 'import' keys.
    """
    violations: list[dict] = []
    root = Path(__file__).parent.parent
    for core_dir in CORE_DIRS:
        core_path = root / core_dir
        if not core_path.exists():
            continue
        for py_file in core_path.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            for mod in TOOLING_MODULES:
                if mod in text:
                    violations.append({"file": str(py_file.relative_to(root)), "import": mod})
    return violations


if __name__ == "__main__":
    violations = audit()
    if violations:
        print(f"FAIL: {len(violations)} core->tooling boundary violation(s):")
        for v in violations:
            print(f"  {v['file']}: imports {v['import']}")
        sys.exit(1)
    print("PASS: No core->tooling boundary violations found.")
    sys.exit(0)
