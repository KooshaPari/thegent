"""DAG session management: parse, validate, serialize, list, run, sync, recover.

Extracted from impl.py as part of WL-120 LOC Reduction Program (Phase 2).
Contains:
- DagDocument dataclass and DAG parsing/serialization helpers
- DAG validation (task ID, agent, cycle detection)
- DAG task update and ready-task resolution
- dag_list_impl, dag_raw_impl, dag_ready_impl, dag_run_impl
- dag_status_impl, dag_sync_impl, dag_recover_impl, rules_sync_impl
"""

from __future__ import annotations

import os
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from thegent_agents.agents import list_agent_names, resolve_agent
from thegent_core.config import ThegentSettings

__all__ = [
    "_dag_path",
    "_ensure_dag_file",
    "_validate_dag",
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


def _dag_path(cd: Path | None) -> tuple[Path | None, Path | None]:
    """Resolve cwd and dag-session.md path. Returns (None, None) if cwd cannot be resolved."""
    from thegent_cli.commands.impl import _resolve_cwd

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

    from thegent_cli.commands.impl import _find_session_meta, _is_pid_running, _read_session_meta, _session_paths

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


# ---------------------------------------------------------------------------
# DAG impl functions (public API)
# ---------------------------------------------------------------------------


def dag_list_impl(cd: Path | None = None) -> dict[str, Any]:
    """List DAG tasks. Returns {frontmatter, tasks} or error."""
    from thegent_cli.commands.impl import _resolve_cwd

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
    from thegent_cli.commands.impl import _resolve_cwd

    cwd = _resolve_cwd(cd)
    if cwd is None:
        return "# Error\nAmbiguous cwd; use --cd to specify project root."
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        return f"# Error\nDAG not found: {dag_path}"
    return dag_path.read_text(encoding="utf-8")


def dag_ready_impl(cd: Path | None = None) -> dict[str, Any]:
    """List task ids that are ready (pending with all deps done|cancelled|skipped)."""
    from thegent_cli.commands.impl import _resolve_cwd

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
    from thegent_cli.commands.impl import _default_owner_tag, _resolve_cwd, bg_impl

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
    """For each task with session_id show id, status, session_id, session_status."""
    from thegent_cli.commands.impl import _resolve_cwd

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
    from thegent_skills.rules.sync import RulesSync

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
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc.
    If --auto-run-next, spawn next ready tasks after sync."""
    from thegent_cli.commands.impl import (
        _find_session_meta,
        _is_pid_running,
        _read_session_meta,
        _resolve_cwd,
        _session_paths,
    )

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
    """Perform recovery playbook actions on the DAG.

    Actions:
        retry-failed: Reset all failed tasks to pending.
        clear-stuck: Reset all running tasks to pending.
        reset-retries: Reset all retry counters.
        fallback: Swap failed tasks to fallback agents.
    """
    from thegent_cli.commands.impl import _resolve_cwd

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
