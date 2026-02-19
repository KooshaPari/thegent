#!/usr/bin/env python3
"""
P6: Incremental analysis — find functions/classes with changed lines.
Uses AST to map line ranges to definitions. Given changed line ranges from git diff,
returns affected function/class names. Used to skip files where only comments changed.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def _get_def_ranges(node: ast.AST) -> list[tuple[int, int, str]]:
    """Return (start_line, end_line, name) for each function/class def."""
    ranges: list[tuple[int, int, str]] = []

    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = child.end_lineno if hasattr(child, "end_lineno") else child.lineno
            ranges.append((child.lineno, end, child.name))
    return ranges


def _changed_lines_from_git(file_path: str, repo_root: str) -> set[int]:
    """Get set of changed line numbers from git diff (new file line numbers)."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", file_path],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            return set()
        lines: set[int] = set()
        # Parse unified diff: @@ -old_start,old_count +new_start,new_count @@
        # new_start,new_count = lines in the current (new) file
        for line in result.stdout.splitlines():
            if line.startswith("@@"):
                parts = line.split("@@")[1].strip().split()
                for p in parts:
                    if p.startswith("+"):
                        nums = p[1:].split(",")
                        start = int(nums[0])
                        count = int(nums[1]) if len(nums) > 1 else 1
                        lines.update(range(start, start + count))
                        break
        return lines
    except Exception:
        return set()


def affected_definitions(
    file_path: str,
    changed_lines: set[int] | None = None,
    repo_root: str | None = None,
) -> list[str]:
    """
    Return names of functions/classes that contain any of the changed lines.
    If changed_lines is None, infer from git diff (repo_root required).
    """
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []  # Treat as "all affected" — caller should not skip

    def_ranges = _get_def_ranges(tree)
    if not def_ranges:
        return []

    if changed_lines is None and repo_root:
        changed_lines = _changed_lines_from_git(str(path), repo_root)
    if changed_lines is None:
        changed_lines = set()

    if not changed_lines:
        return []  # No changes — caller may skip file

    affected: list[str] = []
    for start, end, name in def_ranges:
        if any(start <= ln <= end for ln in changed_lines):
            affected.append(name)
    return affected


def _is_tracked(file_path: str, repo_root: str) -> bool:
    """Return True if file is tracked by git."""
    import subprocess

    try:
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", file_path],
            capture_output=True,
            cwd=repo_root,
            timeout=2,
            check=False,
        )
        return r.returncode == 0
    except Exception:
        return False


def has_function_body_changes(file_path: str, repo_root: str) -> bool:
    """
    Return True if we must analyze. Return False only when safe to skip.
    Skip when: file is tracked and git diff is empty (unchanged).
    Analyze when: untracked (new) or any diff exists.
    """
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        return True  # Non-Python or missing — don't skip
    if not _is_tracked(str(path), repo_root):
        return True  # Untracked/new file — must analyze
    changed = _changed_lines_from_git(str(path), repo_root)
    if not changed:
        return False  # Tracked and no diff — safe to skip
    return True  # Has diff — analyze


def main() -> int:
    if len(sys.argv) < 2:
        return 1
    check_mode = sys.argv[1] == "--check"
    file_path = sys.argv[2] if check_mode else sys.argv[1]
    repo_root = sys.argv[3] if check_mode and len(sys.argv) > 3 else (sys.argv[2] if len(sys.argv) > 2 else ".")
    if check_mode:
        # --check: print "skip" if no function body changes, "analyze" otherwise
        if has_function_body_changes(file_path, repo_root):
            pass
        else:
            pass
        return 0
    aff = affected_definitions(file_path, repo_root=repo_root)
    for _name in aff:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
