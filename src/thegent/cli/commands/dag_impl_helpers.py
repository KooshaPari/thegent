"""DAG helpers: parsing, validation, serialization (WL-120).

Contains DagDocument dataclass and low-level helpers for DAG manipulation.
"""

from __future__ import annotations

import os
import re
import logging
from dataclasses import dataclass
from pathlib import Path

from thegent.agents import list_agent_names, resolve_agent

__all__ = [
    "DagDocument",
    "_parse_dag_full",
    "_escape_cell",
    "_serialize_dag",
    "_atomic_write",
    "_parse_dag_session",
    "_validate_task_id",
    "_validate_agent",
    "_check_dag_cycles",
    "_validate_dag",
    "_ensure_evidence_header",
    "_ensure_contract_version_header",
    "_dag_update_task",
]

_log = logging.getLogger(__name__)


@dataclass
class DagDocument:
    """Parsed DAG session document with structure preserved for round-trip."""

    frontmatter: dict[str, str]
    tasks: list[dict[str, str]]
    before_table: str
    after_table: str
    table_headers: list[str]


def _parse_dag_full(path: Path) -> DagDocument:
    """Parse .factory/dag-session.md with full structure for round-trip."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            for line in parts[0].strip().split("\n")[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip()
            text = parts[1]
            lines = text.splitlines()

    tasks: list[dict[str, str]] = []
    headers: list[str] = []
    table_start = -1
    table_end = -1

    for i, line in enumerate(lines):
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not headers:
                headers = [h.lower().replace(" ", "_") for h in cells]
                table_start = i
                continue
            is_separator = all(bool(re.fullmatch(r":?-{3,}:?", c.replace(" ", ""))) for c in cells)
            if cells and not is_separator:
                row = dict(zip(headers, cells, strict=False))
                tasks.append(row)
            table_end = i
        elif headers and table_end >= 0:
            break

    before_table = "\n".join(lines[: table_start - 1 if table_start > 0 else 0]) + "\n" if table_start > 0 else ""
    if table_start >= 0:
        before_table = "\n".join(lines[:table_start]) + "\n"
    after_table = "\n".join(lines[table_end + 1 :]) + "\n" if table_end >= 0 and table_end + 1 < len(lines) else ""

    return DagDocument(
        frontmatter=frontmatter,
        tasks=tasks,
        before_table=before_table,
        after_table=after_table,
        table_headers=headers
        or [
            "id",
            "agent",
            "prompt",
            "depends_on",
            "status",
            "evidence",
            "retry_count",
            "max_retries",
            "quorum",
            "confidence",
        ],
    )


def _escape_cell(s: str) -> str:
    """Escape | for markdown table cells."""
    return s.replace("|", "\\|").replace("\n", " ")


def _serialize_dag(doc: DagDocument) -> str:
    """Serialize DagDocument to markdown."""
    h = doc.table_headers or ["id", "agent", "prompt", "depends_on", "status"]
    rows = []
    for t in doc.tasks:
        cells = [_escape_cell(str(t.get(k, "\u2014"))) for k in h]
        rows.append("| " + " | ".join(cells) + " |")
    sep = "|" + "|".join("---" for _ in h) + "|"
    table = "| " + " | ".join(h) + " |\n" + sep + "\n" + "\n".join(rows)
    return doc.before_table + "\n" + table + "\n\n" + doc.after_table


def _atomic_write(path: Path, content: str, backup: bool = False) -> None:
    """Write content atomically. Optional backup before overwrite."""
    if backup and path.exists():
        import shutil

        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _parse_dag_session(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Parse .factory/dag-session.md: return (frontmatter, tasks)."""
    doc = _parse_dag_full(path)
    return doc.frontmatter, doc.tasks


TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _validate_task_id(task_id: str) -> str | None:
    """Validate task ID format. Returns error message if invalid, else None."""
    if not task_id or not task_id.strip():
        return "Task ID cannot be empty"
    if not TASK_ID_RE.match(task_id.strip()):
        return f"Invalid task ID '{task_id}': must match [A-Za-z0-9][A-Za-z0-9_-]*"
    return None


def _validate_agent(agent: str) -> str | None:
    """Validate agent is in list_agent_names (or resolves via alias). Returns error message if invalid, else None."""
    if not agent or not agent.strip():
        return "Agent cannot be empty"
    canonical = resolve_agent(agent.strip())
    valid = list_agent_names()
    if canonical not in valid:
        return f"Unknown agent '{agent}'; valid: {', '.join(valid)}"
    return None


def _check_dag_cycles(tasks: list[dict[str, str]]) -> list[str]:
    """DFS cycle detection. Returns list of cycle error messages."""
    id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
    errors: list[str] = []

    def __parse_deps(dep_str: str) -> list[str]:
        if not dep_str or dep_str.strip() in ("\u2014", "-"):
            return []
        return [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() not in ("\u2014", "-")]

    def _dfs_cycle(node: str, path: list[str], visited: set[str], rec_stack: set[str]) -> list[str] | None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        task = id_to_task.get(node)
        deps = __parse_deps(task.get("depends_on", "")) if task else []
        for dep in deps:
            if dep not in id_to_task:
                errors.append(f"Task '{node}' depends on unknown task '{dep}'")
                continue
            if dep not in visited:
                cycle = _dfs_cycle(dep, path, visited, rec_stack)
                if cycle is not None:
                    return cycle
            elif dep in rec_stack:
                idx = path.index(dep)
                return [*path[idx:], dep]
        path.pop()
        rec_stack.discard(node)
        return None

    visited: set[str] = set()
    for tid in id_to_task:
        if tid not in visited:
            cycle = _dfs_cycle(tid, [], visited, set())
            if cycle is not None:
                errors.append(f"DAG cycle: {' -> '.join(cycle)}")
    return errors


def _validate_dag(doc: DagDocument) -> list[str]:
    """Validate DAG document. Returns list of error messages."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, t in enumerate(doc.tasks):
        tid = (t.get("id") or "").strip()
        agent = (t.get("agent") or "").strip()

        if err := _validate_task_id(tid):
            errors.append(f"Task row {i + 1}: {err}")
        elif tid in seen_ids:
            errors.append(f"Task row {i + 1}: Duplicate task ID '{tid}'")
        else:
            seen_ids.add(tid)

        if agent and (err := _validate_agent(agent)):
            errors.append(f"Task '{tid}': {err}")

        dep_str = t.get("depends_on", "")
        for d in [x.strip() for x in dep_str.split(",") if x.strip() and x.strip() not in ("\u2014", "-")]:
            if d and (e := _validate_task_id(d)):
                errors.append(f"Task '{tid}' depends on '{d}': {e}")

        # WP-2007: Evidence completeness linting
        status = (t.get("status") or "").strip().lower()
        if status == "done" and not (t.get("evidence") or t.get("session_id")):
            errors.append(f"Task '{tid}': status is 'done' but evidence/session_id is missing.")

    cycle_errors = _check_dag_cycles(doc.tasks)
    errors.extend(cycle_errors)
    return errors


def _ensure_evidence_header(doc: DagDocument) -> None:
    """Ensure evidence is in table_headers if any task has it or session_id."""
    if not doc.table_headers:
        doc.table_headers = ["id", "agent", "prompt", "depends_on", "status"]
    if "evidence" not in doc.table_headers and any(t.get("evidence") or t.get("session_id") for t in doc.tasks):
        # Insert evidence after status if possible
        if "status" in doc.table_headers:
            idx = doc.table_headers.index("status")
            doc.table_headers = [*list(doc.table_headers[: idx + 1]), "evidence", *list(doc.table_headers[idx + 1 :])]
        else:
            doc.table_headers = [*list(doc.table_headers), "evidence"]


def _ensure_contract_version_header(doc: DagDocument) -> None:
    """XA4: Ensure contract_version is in table_headers if any task has it."""
    if not doc.table_headers:
        return
    if "contract_version" not in doc.table_headers and any(t.get("contract_version") for t in doc.tasks):
        if "status" in doc.table_headers:
            idx = doc.table_headers.index("status")
            doc.table_headers = [
                *list(doc.table_headers[: idx + 1]),
                "contract_version",
                *list(doc.table_headers[idx + 1 :]),
            ]
        else:
            doc.table_headers = [*list(doc.table_headers), "contract_version"]


def _dag_update_task(
    doc: DagDocument,
    task_id: str,
    *,
    status: str | None = None,
    session_id: str | None = None,
    prompt: str | None = None,
    agent: str | None = None,
    depends_on: str | None = None,
    retry_count: int | None = None,
    contract_version: str | None = None,
) -> bool:
    """Update task by id. Returns True if found and updated. XA4: contract_version in task metadata."""
    task_id = task_id.strip()
    for t in doc.tasks:
        if (t.get("id") or "").strip() == task_id:
            if status is not None:
                t["status"] = status
            if session_id is not None:
                t["evidence"] = session_id
                t["session_id"] = session_id
                _ensure_evidence_header(doc)
            if prompt is not None:
                t["prompt"] = prompt
            if agent is not None:
                t["agent"] = agent
            if depends_on is not None:
                t["depends_on"] = depends_on
            if retry_count is not None:
                t["retry_count"] = str(retry_count)
            if contract_version is not None:
                t["contract_version"] = contract_version
                _ensure_contract_version_header(doc)
            return True
    return False
