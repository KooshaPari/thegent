"""DAG operations: list, ready, run, sync, recover (WL-120).

High-level DAG session operations (impl functions).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from thegent.cli.commands.dag_impl_helpers import (
    DagDocument,
    _parse_dag_full,
    _serialize_dag,
    _atomic_write,
    _parse_dag_session,
    _validate_dag,
)
from thegent.config import ThegentSettings

__all__ = [
    "_dag_path",
    "_ensure_dag_file",
    "_session_status_for",
    "_parse_depends_on",
    "_get_ready_task_ids",
    "_resolve_prompt",
    "dag_list_impl",
    "dag_raw_impl",
    "dag_ready_impl",
    "dag_run_impl",
    "dag_status_impl",
    "rules_sync_impl",
    "dag_sync_impl",
    "dag_recover_impl",
]

_log = logging.getLogger(__name__)


def _dag_path(cd: Path | None) -> tuple[Path | None, Path | None]:
    """Resolve cwd and dag-session.md path. Returns (None, None) if cwd cannot be resolved."""
    from thegent.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd

    cwd = _resolve_cwd(cd)
    if cwd is None:
        return None, None
    dag_path = cwd / ".factory" / "dag-session.md"
    return cwd, dag_path


def _ensure_dag_file(dag_path: Path) -> DagDocument:
    """Load DAG or create minimal empty document if file does not exist."""
    if dag_path.exists():
        return _parse_dag_full(dag_path)
    return DagDocument(
        frontmatter={"version": "1", "project": "", "owner": ""},
        tasks=[],
        before_table="# DAG Session\n\n## Tasks\n\n",
        after_table="",
        table_headers=["id", "agent", "prompt", "depends_on", "status"],
    )


def _session_status_for(session_id: str, settings: ThegentSettings) -> str:
    """Return session_status: running or exited:rc."""
    import typer

    from thegent.cli.commands.impl import _find_session_meta, _is_pid_running, _read_session_meta, _session_paths

    try:
        meta_path = _find_session_meta(settings, session_id)
        p = _session_paths(base=meta_path.parent, session_id=session_id)
        m = _read_session_meta(meta_path)
        pid = int(m.get("pid", 0) or 0)
        running = _is_pid_running(pid)
        rc = p["rc"].read_text(encoding="utf-8").strip() if p["rc"].exists() else ""
        return "running" if running else ("exited:" + rc if rc else "exited")
    except (typer.BadParameter, Exception):
        return "not_found"


def _parse_depends_on(dep_str: str) -> list[str]:
    """Parse comma-separated depends_on string."""
    if not dep_str or dep_str.strip() in ("\u2014", "-"):
        return []
    return [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() not in ("\u2014", "-")]


def _get_ready_task_ids(tasks: list[dict[str, str]]) -> list[str]:
    """Return task IDs that are pending and have dependencies satisfied."""
    id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
    ready = []
    for tid, t in id_to_task.items():
        status = t.get("status", "").lower()
        if status != "pending":
            continue
        deps = _parse_depends_on(t.get("depends_on", ""))
        sat = True
        for d in deps:
            dt = id_to_task.get(d)
            if not dt or dt.get("status", "").lower() not in ("done", "completed", "cancelled", "skipped"):
                sat = False
                break
        if sat:
            ready.append(tid)
    return ready


def _resolve_prompt(task_id: str, prompt: str, cwd: Path) -> str:  # pyright: ignore[reportUnusedVariable]
    """Resolve prompt: inline string or @.factory/prompts/<id>.md."""
    if prompt.startswith("@"):
        path = cwd / prompt[1:]
        if path.exists():
            return path.read_text(encoding="utf-8")
    return prompt



__all__ = [
    "_dag_path",
    "_ensure_dag_file",
    "_session_status_for",
    "_parse_depends_on",
    "_get_ready_task_ids",
    "_resolve_prompt",
]
