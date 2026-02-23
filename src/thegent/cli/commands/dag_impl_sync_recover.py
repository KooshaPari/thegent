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
    """For each task with session_id show id, status, session_id, session_status."""
    from thegent.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd

    cwd = _resolve_cwd(cd) or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "tasks": []}

    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    rows = []

    for t in doc.tasks:
        session_id = t.get("session_id") or t.get("evidence")
        if not session_id:
            continue

        # Handle comma-separated session_ids
        sids = [s.strip() for s in session_id.split(",") if s.strip()]
        if not sids:
            continue

        # Use first session_id for status
        sid = sids[0]
        try:
            session_status = _session_status_for(sid, settings)
        except Exception:
            session_status = "not_found"

        rows.append(
            {
                "id": t.get("id", ""),
                "status": t.get("status", ""),
                "session_id": sid,
                "session_status": session_status,
            }
        )

    return {"tasks": rows}


def rules_sync_impl(cd: Path | None = None, force: bool = False, check: bool = False) -> dict[str, Any]:  # pyright: ignore[reportUnusedVariable]
    """Sync rules implementation (WP-9002)."""
    from thegent.rules.sync import RulesSync

    project_root = cd or Path.cwd()
    syncer = RulesSync(project_root)

    try:
        synced_files = syncer.sync()
        return {
            "success": True,
            "synced": synced_files,
            "in_sync": len(synced_files) == 0 if check else True,
            "drift": [],
            "error": None,
        }
    except Exception as e:
        return {"success": False, "synced": [], "in_sync": False, "drift": [], "error": str(e)}


def dag_sync_impl(cd: Path | None = None, auto_run_next: bool = False) -> dict[str, Any]:
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc."""
    from thegent.cli.commands.impl import (
        _find_session_meta,
        _is_pid_running,
        _read_session_meta,
        _resolve_cwd,
        _session_paths,
    )
    from thegent.cli.commands.dag_impl_helpers import _dag_update_task

    cwd = _resolve_cwd(cd) or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "changed": False}

    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    changed = False

    for t in doc.tasks:
        if t.get("status", "").lower() != "running":
            continue

        session_id = t.get("session_id") or t.get("evidence")
        if not session_id:
            continue

        # Handle comma-separated session_ids
        sids = [s.strip() for s in session_id.split(",") if s.strip()]
        if not sids:
            continue

        # Check first session_id
        sid = sids[0]
        try:
            meta_path = _find_session_meta(settings, sid)
            p = _session_paths(base=meta_path.parent, session_id=sid)
            m = _read_session_meta(meta_path)
            pid = int(m.get("pid", 0) or 0)
            running = _is_pid_running(pid)

            rc = 1  # Default to failure; will be overwritten if session succeeded
            if not running:
                # Read exit code
                rc = 0
                if p["rc"].exists():
                    try:
                        rc_raw = p["rc"].read_text(encoding="utf-8").strip()
                        if rc_raw:
                            rc = int(rc_raw)
                    except (OSError, ValueError) as exc:
                        _log.warning("Unable to read valid rc for session %s: %s", sid, exc)
                        rc = 1

            new_status = "done" if rc == 0 else "failed"
            _dag_update_task(doc, t.get("id", ""), status=new_status)
            changed = True
        except Exception:
            # Session not found or error - mark as failed
            _dag_update_task(doc, t.get("id", ""), status="failed")
            changed = True

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))

    run_next_result = {}
    if auto_run_next and changed:
        settings = ThegentSettings()
        _max_parallel: int | None = settings.max_parallel
        run_next_result = dag_run_impl(cd=cd, max_parallel=_max_parallel)

    return {
        "changed": changed,
        "run_next": run_next_result if auto_run_next else None,
    }


def dag_recover_impl(cd: Path | None = None, action: str = "retry-failed") -> dict[str, Any]:
    """Perform recovery playbook actions on the DAG."""
    from thegent.cli.commands.impl import _resolve_cwd
    from thegent.cli.commands.dag_impl_helpers import _dag_update_task

    cwd = _resolve_cwd(cd) or Path.cwd()
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return {"error": f"DAG not found: {dag_path}", "changed": False}

    doc = _parse_dag_full(dag_path)
    changed = False

    for t in doc.tasks:
        status = t.get("status", "").lower()
        if (action == "retry-failed" and status == "failed") or (action == "clear-stuck" and status == "running"):
            _dag_update_task(doc, t.get("id", ""), status="pending")
            changed = True
        elif action == "reset-retries":
            if int(t.get("retry_count", 0)) > 0:
                t["retry_count"] = "0"
                changed = True
        elif action == "fallback" and status == "failed":
            fallback = t.get("fallback_agent")
            if fallback:
                t["agent"] = fallback
                _dag_update_task(doc, t.get("id", ""), status="pending")
                changed = True

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))

    return {"changed": changed, "action": action}


__all__ = [
    "dag_sync_impl",
    "dag_recover_impl",
]
