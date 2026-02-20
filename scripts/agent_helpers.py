#!/usr/bin/env python3
"""
Agent Helpers Library

Reusable helper functions for common patterns used across agents, hooks, and scripts.

Reduces friction and code duplication in the agent ecosystem by providing thin
wrappers around common operations:

- log_friction: Record DX/UX/AX friction points to FRICTION_LOG.md
- get_next_items: Read next actionable work items from WORK_STREAM.md
- update_work_stream: Claim or complete items in WORK_STREAM.md
- run_quality_check: Run ruff lint and pytest, return structured results
- read_config: Read ThegentSettings with key fallback
- format_summary: Format agent output summaries consistently

Usage:
    from agent_helpers import (
        log_friction,
        get_next_items,
        update_work_stream,
        run_quality_check,
        read_config,
        format_summary,
    )
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent

# Canonical file paths used by helpers
_FRICTION_LOG_PATH = _PROJECT_ROOT / "docs" / "research" / "FRICTION_LOG.md"
_WORK_STREAM_PATH = _PROJECT_ROOT / "docs" / "reference" / "WORK_STREAM.md"

# ---------------------------------------------------------------------------
# ThegentSettings import — optional; not required for all helpers.
# Stored as a plain object reference to avoid annotation-level imports.
# ---------------------------------------------------------------------------

_SETTINGS_AVAILABLE: bool = False
_ThegentSettings_cls: Any = None

try:
    _src_path = str(_PROJECT_ROOT / "src")
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)
    import importlib as _importlib

    _mod = _importlib.import_module("thegent.config")
    _ThegentSettings_cls = getattr(_mod, "ThegentSettings", None)
    _SETTINGS_AVAILABLE = _ThegentSettings_cls is not None
except (ImportError, ModuleNotFoundError, AttributeError):
    _SETTINGS_AVAILABLE = False
    _ThegentSettings_cls = None


# ===========================================================================
# 1. log_friction
# ===========================================================================


def log_friction(
    category: str,
    description: str,
    impact: str = "medium",
    *,
    task_id: str | None = None,
    friction_type: str = "general",
    location: str = "unknown",
    solution: str = "",
    priority: str = "P2",
    friction_log_path: Path | None = None,
) -> bool:
    """Log a DX/UX/AX friction point to FRICTION_LOG.md.

    Creates the log file with a valid header if it does not exist.  Appends a
    new Markdown section for each friction entry so entries are human-readable
    and searchable.

    Args:
        category: Friction category — one of ``dx``, ``ux``, or ``ax``.
        description: Human-readable description of the friction point.
        impact: Qualitative impact level — ``low``, ``medium``, or ``high``.
        task_id: Optional task/work-item ID to associate the entry with.
                 Auto-generated from category + timestamp when omitted.
        friction_type: Sub-type label (e.g. ``verbosity``, ``complexity``).
        location: File, function, or pattern where friction was observed.
        solution: Proposed fix or mitigation.
        priority: Priority level — ``P1`` (blocking) or ``P2`` (improvement).
        friction_log_path: Override the default ``FRICTION_LOG.md`` path
                           (primarily for testing).

    Returns:
        ``True`` on success, ``False`` if the log file could not be written.
    """
    log_path = friction_log_path or _FRICTION_LOG_PATH

    category_display = category.upper()
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    if task_id is None:
        slug = re.sub(r"[^a-z0-9]+", "-", category.lower())
        task_id = f"{slug}-{timestamp[:10].replace('-', '')}"

    entry = (
        f"\n### {task_id}\n\n"
        f"- **Category**: {category_display}\n"
        f"- **Type**: {friction_type}\n"
        f"- **Location**: {location}\n"
        f"- **Description**: {description}\n"
        f"- **Impact**: {impact}\n"
        f"- **Solution**: {solution or 'TBD'}\n"
        f"- **Priority**: {priority}\n"
        f"- **Timestamp**: {timestamp}\n"
    )

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if not log_path.exists():
            header = (
                "# Friction Points Log\n\n"
                "> **Purpose**: Continuous log of friction points identified during agent workflows\n"
                f"> **Last Updated**: {timestamp[:10]}\n\n"
                "---\n\n"
                "## Friction Points\n"
            )
            log_path.write_text(header, encoding="utf-8")

        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(entry)

        return True
    except OSError:
        return False


# ===========================================================================
# 2. get_next_items (and internal parser)
# ===========================================================================


def _parse_work_stream(work_stream_path: Path) -> dict[str, list[dict[str, str]]]:
    """Parse WORK_STREAM.md into structured sections.

    Returns:
        Dict with keys ``backlog``, ``claimed``, and ``completed``, each
        containing a list of item dicts.
    """
    result: dict[str, list[dict[str, str]]] = {
        "backlog": [],
        "claimed": [],
        "completed": [],
    }

    if not work_stream_path.exists():
        return result

    content = work_stream_path.read_text(encoding="utf-8")
    current_section: str | None = None

    for line in content.splitlines():
        upper = line.upper()
        if "## BACKLOG" in upper:
            current_section = "backlog"
        elif "## CLAIMED" in upper:
            current_section = "claimed"
        elif "## COMPLETED" in upper:
            current_section = "completed"
        elif current_section and line.startswith("|"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 2:
                continue
            # Skip header separator rows (e.g. |---|---|)
            if all(set(p).issubset({"-", " "}) for p in parts):
                continue
            # Skip column header rows
            if parts[0].upper() in {"ID", "ITEM", "TASK"}:
                continue

            if current_section == "backlog":
                result["backlog"].append(
                    {
                        "id": parts[0],
                        "title": parts[1] if len(parts) > 1 else "",
                        "source": parts[2] if len(parts) > 2 else "",
                        "priority": parts[3] if len(parts) > 3 else "",
                        "depends": parts[4] if len(parts) > 4 else "",
                    }
                )
            elif current_section == "claimed":
                result["claimed"].append(
                    {
                        "id": parts[0],
                        "agent": parts[1] if len(parts) > 1 else "",
                        "timestamp": parts[2] if len(parts) > 2 else "",
                    }
                )
            elif current_section == "completed":
                result["completed"].append(
                    {
                        "id": parts[0],
                        "agent": parts[1] if len(parts) > 1 else "",
                        "timestamp": parts[2] if len(parts) > 2 else "",
                    }
                )

    return result


def get_next_items(
    limit: int = 5,
    *,
    priority: str | None = None,
    work_stream_path: Path | None = None,
) -> list[dict[str, str]]:
    """Return the next actionable unclaimed items from WORK_STREAM.md.

    Filters out items that are already CLAIMED or COMPLETED, and only returns
    items whose dependencies (``Depends`` column) are already in the COMPLETED
    set (or are empty / ``-``).

    Args:
        limit: Maximum number of items to return.
        priority: Optional priority filter (e.g. ``"P1"``).  When ``None``,
                  all priorities are included.
        work_stream_path: Override path to WORK_STREAM.md (for testing).

    Returns:
        List of item dicts with keys ``id``, ``title``, ``source``,
        ``priority``, and ``depends``.
    """
    ws_path = work_stream_path or _WORK_STREAM_PATH
    ws = _parse_work_stream(ws_path)

    claimed_ids = {item["id"] for item in ws["claimed"]}
    completed_ids = {item["id"] for item in ws["completed"]}
    excluded = claimed_ids | completed_ids

    ready: list[dict[str, str]] = []
    for item in ws["backlog"]:
        if item["id"] in excluded:
            continue
        if priority and item.get("priority") != priority:
            continue
        # Check dependency satisfaction
        depends_raw = item.get("depends", "").strip()
        if depends_raw and depends_raw != "-":
            deps = [d.strip() for d in depends_raw.split(",") if d.strip()]
            if not all(d in completed_ids for d in deps):
                continue
        ready.append(item)
        if len(ready) >= limit:
            break

    return ready


# ===========================================================================
# 3. update_work_stream
# ===========================================================================


def update_work_stream(
    item_id: str,
    status: str,
    notes: str = "",
    *,
    agent_id: str = "agent-helpers",
    work_stream_path: Path | None = None,
) -> bool:
    """Claim or complete a work stream item in WORK_STREAM.md.

    - ``status="claimed"`` — appends a row to the CLAIMED table and removes
      the item from the BACKLOG table (if present).
    - ``status="completed"`` — removes the item from both BACKLOG and CLAIMED
      tables and appends a row to the COMPLETED table.

    Args:
        item_id: The work-item ID to update.
        status: Target status — ``"claimed"`` or ``"completed"``.
        notes: Optional notes stored alongside the timestamp field.
        agent_id: Identifier of the agent performing the operation.
        work_stream_path: Override the default WORK_STREAM.md path (for
                          testing).

    Returns:
        ``True`` when the file was updated successfully, ``False`` otherwise.

    Raises:
        ValueError: If *status* is not ``"claimed"`` or ``"completed"``.
    """
    if status not in {"claimed", "completed"}:
        raise ValueError(f"status must be 'claimed' or 'completed', got {status!r}")

    ws_path = work_stream_path or _WORK_STREAM_PATH
    if not ws_path.exists():
        return False

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    content = ws_path.read_text(encoding="utf-8")

    note_suffix = f" ({notes})" if notes else ""
    new_row = f"| {item_id} | {agent_id} | {timestamp}{note_suffix} |\n"

    # Remove existing rows for this item_id from all sections
    content = re.sub(
        rf"^\| {re.escape(item_id)} \|.*\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Insert the new row into the target section table (after separator row)
    section_header = "## CLAIMED" if status == "claimed" else "## COMPLETED"
    insert_pattern = re.compile(
        rf"({re.escape(section_header)}.*?^\|[-| ]+\|\n)",
        re.DOTALL | re.MULTILINE,
    )
    match = insert_pattern.search(content)
    if match:
        insert_at = match.end()
        content = content[:insert_at] + new_row + content[insert_at:]
    else:
        # Section exists but has no table yet — find section boundary
        idx = content.find(section_header)
        if idx != -1:
            next_section = content.find("\n## ", idx + 1)
            if next_section == -1:
                content += f"\n{new_row}"
            else:
                content = content[:next_section] + f"\n{new_row}" + content[next_section:]
        else:
            # Section header missing entirely — append to end of file
            content += f"\n{new_row}"

    try:
        ws_path.write_text(content, encoding="utf-8")
        return True
    except OSError:
        return False


# ===========================================================================
# 4. run_quality_check
# ===========================================================================


def run_quality_check(
    *,
    project_root: Path | None = None,
    run_lint: bool = True,
    run_tests: bool = True,
    test_path: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run lint (ruff) and/or tests (pytest) and return structured results.

    Both commands are run via ``uv run`` so that the correct virtual
    environment is used without requiring prior activation.

    Args:
        project_root: Directory in which to run the commands.  Defaults to
                      the repository root inferred from this file's location.
        run_lint: Whether to run ``ruff check``.
        run_tests: Whether to run ``pytest``.
        test_path: Optional path or glob to pass to pytest (e.g.
                   ``"tests/test_agent_helpers.py"``).  When ``None``,
                   pytest discovers tests automatically.
        timeout: Per-command timeout in seconds.

    Returns:
        Dict with the following keys:

        - ``lint_passed`` (bool): ``True`` when ruff exited with code 0.
        - ``lint_output`` (str): Combined stdout/stderr from ruff.
        - ``tests_passed`` (bool): ``True`` when pytest exited with code 0.
        - ``tests_output`` (str): Combined stdout/stderr from pytest.
        - ``overall_passed`` (bool): ``lint_passed and tests_passed``.
        - ``errors`` (list[str]): Any errors encountered while running.
    """
    root = project_root or _PROJECT_ROOT
    results: dict[str, Any] = {
        "lint_passed": True,
        "lint_output": "",
        "tests_passed": True,
        "tests_output": "",
        "overall_passed": True,
        "errors": [],
    }

    def _run(cmd: list[str], label: str) -> tuple[bool, str]:
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode == 0, output
        except FileNotFoundError as exc:
            return False, f"{label}: command not found — {exc}"
        except subprocess.TimeoutExpired:
            return False, f"{label}: timed out after {timeout}s"
        except OSError as exc:
            return False, f"{label}: OS error — {exc}"

    if run_lint:
        lint_cmd = ["uv", "run", "ruff", "check", ".", "--output-format=grouped"]
        passed, output = _run(lint_cmd, "lint")
        results["lint_passed"] = passed
        results["lint_output"] = output
        if not passed:
            results["errors"].append(f"Lint failed: {output[:200]}")

    if run_tests:
        test_cmd = ["uv", "run", "pytest", "-q"]
        if test_path:
            test_cmd.append(test_path)
        passed, output = _run(test_cmd, "tests")
        results["tests_passed"] = passed
        results["tests_output"] = output
        if not passed:
            results["errors"].append(f"Tests failed: {output[:200]}")

    results["overall_passed"] = results["lint_passed"] and results["tests_passed"]
    return results


# ===========================================================================
# 5. read_config
# ===========================================================================


def read_config(key: str, default: Any = None) -> Any:
    """Read a configuration value from ThegentSettings with a fallback.

    Wraps ``ThegentSettings`` so callers do not need to import or instantiate
    the settings object themselves.  If the settings class is unavailable
    (e.g. running outside the installed package), the *default* is returned.

    Args:
        key: The attribute name on ``ThegentSettings`` (e.g.
             ``"default_timeout"``).
        default: Value to return when the key is not found or settings are
                 unavailable.

    Returns:
        The setting value or *default*.
    """
    if not _SETTINGS_AVAILABLE or _ThegentSettings_cls is None:
        return default

    try:
        settings = _ThegentSettings_cls()
        return getattr(settings, key, default)
    except Exception:
        return default


# ===========================================================================
# 6. format_summary
# ===========================================================================


def format_summary(title: str, items: list[Any]) -> str:
    """Format a consistent agent output summary.

    Produces a Markdown-style summary block that agents can include in their
    output or log for downstream consumption.

    The summary contains:
    - A bold title line with item count.
    - A numbered list of items (each item is converted to a string).
    - A footer with a UTC timestamp.

    Args:
        title: Short descriptive title for the summary.
        items: List of items to include.  Each item is rendered via ``str()``.

    Returns:
        Formatted multi-line string.

    Example::

        >>> print(format_summary("Friction Points Found", ["cd && issue", "2>&1 pattern"]))
        ## Friction Points Found (2 items)
        ...
    """
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    count = len(items)

    lines: list[str] = [
        f"## {title} ({count} item{'s' if count != 1 else ''})",
        "",
    ]

    if not items:
        lines.append("_(no items)_")
    else:
        for idx, item in enumerate(items, 1):
            lines.append(f"{idx}. {item}")

    lines.extend(["", f"_Generated: {timestamp}_"])
    return "\n".join(lines)


# ===========================================================================
# CLI entry point (for quick manual use)
# ===========================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Agent Helpers CLI")
    sub = parser.add_subparsers(dest="command")

    next_p = sub.add_parser("next", help="Get next work items")
    next_p.add_argument("--limit", type=int, default=5)
    next_p.add_argument("--priority", default=None)

    log_p = sub.add_parser("log-friction", help="Log a friction point")
    log_p.add_argument("category")
    log_p.add_argument("description")
    log_p.add_argument("--impact", default="medium")

    sub.add_parser("quality", help="Run quality check")

    args = parser.parse_args()

    if args.command == "next":
        next_items = get_next_items(limit=args.limit, priority=args.priority)
        print(json.dumps(next_items, indent=2))
    elif args.command == "log-friction":
        ok = log_friction(args.category, args.description, impact=args.impact)
        print("Logged." if ok else "Failed to log friction point.")
    elif args.command == "quality":
        result = run_quality_check()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
