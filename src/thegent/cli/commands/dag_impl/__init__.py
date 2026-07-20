"""DAG implementation module (AUDIT-N+11: refactored from impl.py).

This module owns the canonical :class:`DagDocument` dataclass and the
DAG parsing/validation helpers extracted from ``cli.commands.impl``.
The :mod:`thegent.cli.services.run_dag_helpers` module re-exports the
public symbols; ``cli.commands.impl`` delegates to those wrappers so
the WL-125 monkeypatch sites resolve.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DagDocument:
    """Parsed DAG session document.

    Attributes:
        frontmatter: YAML frontmatter key/value pairs (raw, pre-parse).
        tasks: Parsed task rows (one per table row, dict).
        before_table: Markdown body before the tasks table.
        after_table: Markdown body after the tasks table.
        table_headers: Column headers from the first table row.
    """

    frontmatter: dict[str, Any] = field(default_factory=dict)
    tasks: list[dict[str, Any]] = field(default_factory=list)
    before_table: str = ""
    after_table: str = ""
    table_headers: list[str] = field(default_factory=list)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Parse YAML-style ``---\\nkey: value\\n---\\n`` frontmatter from ``raw``.

    Returns ``(frontmatter, remainder)`` where ``remainder`` is the body
    after the closing ``---``. Falls back to ``({},"<raw>")`` when no
    frontmatter block is found.
    """
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw
    block = match.group(1)
    frontmatter: dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter, raw[match.end():]


def _parse_dag_full(path: Path) -> DagDocument:
    """Parse a DAG session markdown file at ``path`` into a :class:`DagDocument`.

    The file is expected to have an optional YAML-style frontmatter block
    followed by a markdown body that contains a single tasks table:

    ::

        ---
        version: 1
        ---
        # DAG Session

        ## Tasks

        | id | agent | prompt | depends_on | status |
        | --- | --- | --- | --- | --- |
        | T1 | codex | Do work | — | pending |
    """
    raw = Path(path).read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)

    before_table, _, after_table = body.partition("|")
    table_block = body[body.find("|"):] if "|" in body else ""

    tasks: list[dict[str, Any]] = []
    headers: list[str] = []
    rows = [row for row in table_block.splitlines() if row.strip().startswith("|")]
    if rows:
        headers = [cell.strip() for cell in rows[0].strip().strip("|").split("|")]
        data_rows = [r for r in rows[1:] if not re.match(r"^\|\s*-+", r.strip())]
        for row in data_rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            tasks.append({headers[i]: cells[i] for i in range(len(headers))})

    return DagDocument(
        frontmatter=frontmatter,
        tasks=tasks,
        before_table=before_table,
        after_table=after_table,
        table_headers=headers,
    )


def _serialize_dag(doc: DagDocument) -> str:
    """Render a :class:`DagDocument` back into markdown."""
    lines: list[str] = []
    if doc.frontmatter:
        lines.append("---")
        for key, value in doc.frontmatter.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
    if doc.before_table:
        lines.append(doc.before_table)
    if doc.table_headers:
        lines.append("| " + " | ".join(doc.table_headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(doc.table_headers)) + " |")
        for task in doc.tasks:
            cells = [str(task.get(h, "")) for h in doc.table_headers]
            lines.append("| " + " | ".join(cells) + " |")
    if doc.after_table:
        lines.append(doc.after_table)
    return "\n".join(lines) + "\n"


def _parse_dag_session(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return ``(frontmatter, tasks)`` for the DAG at ``path``."""
    doc = _parse_dag_full(path)
    return doc.frontmatter, doc.tasks


def _validate_task_id(task_id: str) -> str | None:
    """Return an error string if ``task_id`` is not a valid DAG task id."""
    if not task_id or not isinstance(task_id, str):
        return "Task id must be a non-empty string"
    if not re.match(r"^[A-Za-z0-9_\-]+$", task_id):
        return f"Task id {task_id!r} contains invalid characters"
    return None


def _validate_agent(agent: str) -> str | None:
    """Return an error string if ``agent`` is not a known backend."""
    if not agent or not isinstance(agent, str):
        return "Agent must be a non-empty string"
    return None


def _parse_depends_on(depends_on: Any) -> list[str]:
    """Normalize a ``depends_on`` field into a list of dependency ids."""
    if depends_on is None:
        return []
    if isinstance(depends_on, str):
        cleaned = depends_on.replace("\u2014", "").replace("—", "")
        return [d.strip() for d in cleaned.split(",") if d.strip()]
    if isinstance(depends_on, list):
        return [str(d) for d in depends_on if d]
    return []


def _get_ready_task_ids(tasks: list[dict[str, Any]]) -> list[str]:
    """Return ids of tasks whose dependencies are all satisfied."""
    completed = {t.get("id") for t in tasks if t.get("status") == "completed"}
    ready: list[str] = []
    for task in tasks:
        if task.get("status") != "pending":
            continue
        deps = _parse_depends_on(task.get("depends_on"))
        if all(dep in completed for dep in deps):
            ready.append(task.get("id", ""))
    return ready


def _validate_dag(doc: DagDocument) -> list[str]:
    """Validate a :class:`DagDocument`; return list of error strings."""
    errors: list[str] = []
    if not doc.tasks:
        return errors
    task_ids = {t.get("id") for t in doc.tasks}
    for task in doc.tasks:
        deps = _parse_depends_on(task.get("depends_on"))
        for dep in deps:
            if dep not in task_ids:
                errors.append(
                    f"Task {task.get('id')!r} depends on unknown task {dep!r}"
                )
    return errors


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
    """Apply updates to a task row in ``doc``; return True if found."""
    for task in doc.tasks:
        if task.get("id") != task_id:
            continue
        if status is not None:
            task["status"] = status
        if session_id is not None:
            task["session_id"] = session_id
        if prompt is not None:
            task["prompt"] = prompt
        if agent is not None:
            task["agent"] = agent
        if depends_on is not None:
            task["depends_on"] = depends_on
        if retry_count is not None:
            task["retry_count"] = retry_count
        if contract_version is not None:
            task["contract_version"] = contract_version
        return True
    return False


def dag_ready_impl(cd: Path | None = None) -> dict[str, Any]:
    """List ready task ids in the DAG under ``cd/.factory/dag-session.md``."""
    cwd = cd or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "ready": []}
    doc = _parse_dag_full(dag_path)
    return {
        "ready": _get_ready_task_ids(doc.tasks),
        "path": str(dag_path),
    }


__all__ = [
    "DagDocument",
    "_parse_dag_full",
    "_serialize_dag",
    "_parse_dag_session",
    "_validate_task_id",
    "_validate_agent",
    "_parse_depends_on",
    "_get_ready_task_ids",
    "_validate_dag",
    "_dag_update_task",
    "dag_ready_impl",
]
