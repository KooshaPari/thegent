"""DAG operations: list, ready, run, sync, recover (WL-120).

High-level DAG session operations (impl functions).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from phenotype_thegent_cli.cli.commands.dag_impl_helpers import (
    _parse_dag_full,
    _serialize_dag,
    _atomic_write,
    _parse_dag_session,
)

_log = logging.getLogger(__name__)


def dag_list_impl(cd: Path | None = None) -> dict[str, Any]:
    """List DAG tasks. Returns {frontmatter, tasks} or error."""
    from phenotype_thegent_cli.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd

    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {"error": "Ambiguous cwd; use --cd to specify project root."}
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "frontmatter": {}, "tasks": []}
    frontmatter, tasks = _parse_dag_session(dag_path)
    return {"frontmatter": frontmatter, "tasks": tasks}


def dag_raw_impl(cd: Path | None = None) -> str:
    """Get raw DAG markdown content. Returns markdown string or error message."""
    from phenotype_thegent_cli.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd

    cwd = _resolve_cwd(cd)
    if cwd is None:
        return "# Error\nAmbiguous cwd; use --cd to specify project root."
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return f"# Error\nDAG not found: {dag_path}"
    return dag_path.read_text(encoding="utf-8")


def dag_ready_impl(cd: Path | None = None) -> dict[str, Any]:
    """List task ids that are ready (pending with all deps done|cancelled|skipped)."""
    from phenotype_thegent_cli.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd

    cwd = _resolve_cwd(cd) or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "ready_task_ids": []}

    doc = _parse_dag_full(dag_path)
    ready_ids = _get_ready_task_ids(doc.tasks)
    ready_tasks = [t for t in doc.tasks if t.get("id", "").strip() in ready_ids]

    return {
        "ready_task_ids": ready_ids,
        "tasks": ready_tasks,
    }


def dag_run_impl(
    cd: Path | None = None,
    dry_run: bool = False,
    task: str | None = None,
    max_parallel: int | None = None,
    lane: str | None = None,
    check_drift: bool = False,  # pyright: ignore[reportUnusedVariable]
    contract_version: str | None = None,
) -> dict[str, Any]:
    """Spawn thegent bg for each ready task; update status=running and session_id."""
    from phenotype_thegent_cli.cli.commands.impl import _default_owner_tag, _resolve_cwd, bg_impl
    from phenotype_thegent_cli.cli.commands.dag_impl_helpers import _dag_update_task

    cwd = _resolve_cwd(cd) or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}"}

    doc = _parse_dag_full(dag_path)
    ready_ids = _get_ready_task_ids(doc.tasks)

    if task:
        if task not in ready_ids:
            return {"error": f"Task {task} is not ready"}
        ready_ids = [task]

    if not ready_ids:
        return {"message": "No ready tasks"}

    if max_parallel:
        ready_ids = ready_ids[:max_parallel]

    if dry_run:
        would_run = []
        for tid in ready_ids:
            t = next((t for t in doc.tasks if t.get("id", "").strip() == tid), None)
            if t:
                prompt = _resolve_prompt(tid, t.get("prompt", ""), cwd)
                would_run.append(
                    {
                        "task_id": tid,
                        "agent": t.get("agent", ""),
                        "prompt_preview": prompt[:60] + "..." if len(prompt) > 60 else prompt,
                    }
                )
        return {"dry_run": True, "would_run": would_run}

    spawned = []
    errors = []

    for tid in ready_ids:
        t = next((t for t in doc.tasks if t.get("id", "").strip() == tid), None)
        if not t:
            errors.append({"task_id": tid, "error": "Task not found"})
            continue

        agent = t.get("agent", "").strip()
        prompt = _resolve_prompt(tid, t.get("prompt", ""), cwd)

        try:
            result = bg_impl(
                agent=agent,
                prompt=prompt,
                cd=cwd,
                mode="default",
                timeout=3600,
                full=False,
                model=None,
                provider=None,
                owner=_default_owner_tag(cwd),
                lane=lane,
                contract_version=contract_version or t.get("contract_version"),
                task_id=tid,
            )

            if "error" in result:
                errors.append({"task_id": tid, "error": result["error"]})
                continue

            session_id = result.get("session_id")
            if not session_id:
                errors.append({"task_id": tid, "error": "bg_impl returned no session_id"})
                continue

            _dag_update_task(doc, tid, status="running", session_id=session_id)
            spawned.append({"task_id": tid, "session_id": session_id})
        except Exception as e:
            errors.append({"task_id": tid, "error": str(e)})

    if spawned:
        _atomic_write(dag_path, _serialize_dag(doc))

    return {
        "spawned": spawned,
        "errors": errors,
    }


def dag_status_impl(cd: Path | None = None) -> dict[str, Any]:
    pass


def rules_sync_impl(cd: Path | None = None, force: bool = False) -> dict[str, Any]:
    pass


def dag_sync_impl(cd: Path | None = None) -> dict[str, Any]:
    pass


__all__ = [
    "dag_list_impl",
    "dag_raw_impl",
    "dag_ready_impl",
    "dag_run_impl",
    "dag_status_impl",
    "rules_sync_impl",
]
