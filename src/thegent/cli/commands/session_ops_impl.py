"""Session listing and read operations: ps, list, status, inspect, logs.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
Control operations (wait, stop, send, history, metrics, prune, events, meta, negotiate, purge,
explain) split to session_control_impl.py.
Contains:
- ps_impl: list active sessions from registry + legacy dirs + IDE scan
- session_list_impl: list all sessions including completed ones
- status_impl: get status of a background session
- inspect_impl: get status + logs for one or more sessions
- logs_impl: get or follow logs from a background session
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import typer

from thegent.cli.commands.session_meta_impl import (
    _find_session_meta,
    _normalize_contract_string,
    _read_session_meta,
    _resolve_session_status,
)
from thegent.config import ThegentSettings
from thegent.execution import RunRegistry

_log = logging.getLogger(__name__)

_LOG_FOLLOW_POLL_SECONDS = 0.5


def ps_impl(
    owner: str | None = None,
    all: bool = False,
    agent: str | None = None,
    status: str | None = None,
    limit: int = 50,
    scan_ide: bool = False,
    include_contract: bool = False,
) -> list[dict[str, Any]]:
    """
    List agent sessions (managed + discovered) (WP-9006).

    Args:
        owner: Filter by owner (default: current user)
        all: Show sessions for all owners
        agent: Filter by agent name
        status: Filter by status (running, completed, failed, paused)
        limit: Max sessions to return
        scan_ide: Include IDE-managed sessions (Cursor, Claude CLI, Codex)
        include_contract: Include route contract metadata
    """
    from thegent.cli.commands.impl import _default_owner_tag, _is_pid_running, _session_paths

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    registry = RunRegistry(settings.session_dir)

    # Get managed runs from registry
    runs = registry.list_runs(limit=max(1000, limit * 2))

    rows: list[dict[str, Any]] = []
    for r in runs:
        # Security check: owner scoping
        if not all and r.get("owner") != own:
            continue

        # Filter: agent
        if agent and r.get("agent") != agent:
            continue

        # Determine live status (running check)
        if r.get("event") != "finish":
            pid = int(r.get("pid", 0) or 0)
            if pid > 0 and _is_pid_running(pid):
                r["status"] = "running"
            elif r.get("status") == "started":
                r["status"] = "unknown/crashed"

        # Filter: status
        if status and r.get("status") != status:
            continue

        row = {
            "id": r.get("run_id") or r.get("correlation_id"),
            "run_id": r.get("run_id"),
            "correlation_id": r.get("correlation_id"),
            "agent": r.get("agent", "?"),
            "model": r.get("model"),
            "owner": r.get("owner", "?"),
            "status": r.get("status", "unknown"),
            "started_at_utc": r.get("started_at_utc", ""),
            "prompt": r.get("prompt", ""),
            "prompt_preview": (r.get("prompt", "")[:40] + "...")
            if len(r.get("prompt", "")) > 40
            else (r.get("prompt", "") or "\u2014"),
            "source": r.get("source", "thegent-run"),
            "interactivity": r.get("interactivity", "headless-logs"),
            "attach_target": r.get("attach_target"),
            "pid": r.get("pid"),
        }

        if include_contract:
            row["route_contract"] = r.get("route_contract")
            row["route_request"] = r.get("route_request")

        rows.append(row)

    # Collect legacy sessions from subdirectories if any
    for scope_dir in settings.session_dir.iterdir():
        if not scope_dir.is_dir():
            continue
        if not all and scope_dir.name != own.replace(":", "_"):
            continue
        for json_file in scope_dir.glob("*.json"):
            sid = json_file.stem
            if any(r.get("id") == sid or r.get("run_id") == sid for r in rows):
                continue
            try:
                m = _read_session_meta(json_file)
                sid_value = m.get("session_id") or sid
                pid = int(m.get("pid", 0) or 0)
                running = pid > 0 and _is_pid_running(pid)
                rc_path = _session_paths(base=scope_dir, session_id=sid)["rc"]
                rc = rc_path.read_text(encoding="utf-8").strip() if rc_path.exists() else ""
                status_value = "running" if running else ("exited:" + rc if rc else m.get("status", "unknown"))
                row = {
                    "id": sid_value,
                    "run_id": m.get("run_id") or sid_value,
                    "agent": m.get("agent", "?"),
                    "owner": m.get("owner", scope_dir.name),
                    "status": status_value,
                    "pid": pid,
                    "prompt_preview": m.get("prompt", "")[:40],
                }
                if include_contract:
                    row["route_contract"] = m.get("route_contract")
                rows.append(row)
            except Exception:
                continue

    # IDE agent scanning is not implemented; scan_ide flag is accepted but unused
    _ = scan_ide

    # Sort by started_at_utc desc
    rows.sort(key=lambda x: x.get("started_at_utc", ""), reverse=True)

    return rows[:limit]


def session_list_impl(
    owner: str | None = None,
    all_sessions: bool = False,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    List all sessions including completed ones by reading state.json files.
    Different from ps_impl which only shows active sessions from registry.
    """
    import json as json_mod

    from thegent.cli.commands.impl import _default_owner_tag

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    root = settings.session_dir.expanduser().resolve()

    rows: list[dict[str, Any]] = []

    for state_path in root.glob("*/state.json"):
        try:
            payload = json_mod.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        session_id = _normalize_contract_string(payload.get("session_id"))
        run_id = _normalize_contract_string(payload.get("run_id"))
        if session_id is None or run_id is None:
            continue

        session_dir = state_path.parent
        dir_owner = session_dir.name.replace(":", "_")

        if not all_sessions and dir_owner != own:
            continue

        if not all_sessions and payload.get("owner") and payload.get("owner") != own:
            if own not in dir_owner and dir_owner not in own:
                continue

        row = {
            "session_id": session_id,
            "run_id": run_id,
            "agent": payload.get("agent"),
            "model": payload.get("model"),
            "owner": payload.get("owner") or dir_owner,
            "status": payload.get("status", "unknown"),
            "cwd": payload.get("cwd"),
            "updated_at_utc": payload.get("updated_at_utc"),
            "source": "state_contract",
        }
        rows.append(row)

    # Also collect from registry for additional metadata
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=max(1000, limit * 2))

    existing_session_ids = {r["session_id"] for r in rows if r.get("session_id")}

    for r in runs:
        correlation_id = _normalize_contract_string(r.get("correlation_id") or r.get("run_id"))
        if correlation_id is None:
            continue
        if correlation_id in existing_session_ids:
            for row in rows:
                if row.get("session_id") == correlation_id:
                    if not row.get("owner") or row.get("owner") == "?":
                        row["owner"] = r.get("owner") or row.get("owner")
                    if not row.get("status") or row.get("status") == "unknown":
                        row["status"] = r.get("status") or row.get("status")
                    if not row.get("started_at_utc"):
                        row["started_at_utc"] = r.get("started_at_utc")
                    break
        else:
            if not all_sessions and r.get("owner") != own:
                continue

            row = {
                "session_id": correlation_id,
                "run_id": _normalize_contract_string(r.get("run_id")),
                "agent": r.get("agent"),
                "model": r.get("model"),
                "owner": r.get("owner"),
                "status": r.get("status", "unknown"),
                "cwd": r.get("cwd"),
                "started_at_utc": r.get("started_at_utc"),
                "source": "registry",
            }
            rows.append(row)

    rows.sort(
        key=lambda x: x.get("updated_at_utc") or x.get("started_at_utc") or "",
        reverse=True,
    )

    return rows[:limit]


def status_impl(
    session_id: str,
    include_contract: bool = False,
) -> dict[str, Any]:
    """
    Get status of a background session.
    """
    from thegent.cli.commands.impl import _is_pid_running, _session_paths

    def _resolve_exit_code(payload: dict[str, Any], rc_path: Path, is_running: bool) -> int | None:
        if is_running:
            return None
        exit_code = payload.get("exit_code")
        if isinstance(exit_code, int):
            return exit_code
        if isinstance(exit_code, str):
            try:
                return int(exit_code.strip())
            except ValueError as exc:
                _log.debug("Failed to parse exit_code '%s' for session status: %s", exit_code, exc)
        if rc_path.exists():
            try:
                raw = rc_path.read_text(encoding="utf-8").strip()
                return int(raw) if raw else None
            except (OSError, ValueError):
                return None
        return None

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    p = _session_paths(base=meta_path.parent, session_id=session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _resolve_session_status(m, p["rc"], running=running)
    exit_code = _resolve_exit_code(m, p["rc"], is_running=running)
    payload: dict[str, Any] = {
        "session_id": session_id,
        "status": status,
        "pid": pid,
        "running": running,
        "exit_code": exit_code,
        "owner": m.get("owner", ""),
        "host": m.get("host"),
        "agent": m.get("agent"),
        "mode": m.get("mode"),
        "cwd": m.get("cwd"),
        "timeout_hint_s": m.get("timeout_hint_s"),
        "command": m.get("command", []),
        "launcher_pid": m.get("launcher_pid"),
        "launcher_ppid": m.get("launcher_ppid"),
        "launcher_uid": m.get("launcher_uid"),
        "started_at_utc": m.get("started_at_utc"),
        "ended_at_utc": m.get("ended_at_utc"),
        "duration_seconds": m.get("duration_seconds"),
        "timed_out": m.get("timed_out", False),
        "paths": m.get("paths", {}),
    }
    if include_contract:
        payload["route_contract"] = m.get("route_contract")
        payload["route_request"] = m.get("route_request")
    return payload


def inspect_impl(
    session_ids: list[str],
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    include_contract: bool = False,
) -> list[dict[str, Any]]:
    """
    Get status and logs for one or more sessions. Returns list of {session_id, status, logs}.
    """
    if not session_ids and owner:
        rows = ps_impl(owner=owner, all=False)
        session_ids = [r["id"] for r in rows]
    if not session_ids:
        return []
    out: list[dict[str, Any]] = []
    for sid in session_ids:
        st = status_impl(session_id=sid, include_contract=include_contract)
        try:
            log_text = logs_impl(session_id=sid, tail=tail, stderr=stderr)
        except Exception as e:
            log_text = f"Error: {e}"
        out.append({"session_id": sid, "status": st, "logs": log_text})
    return out


def logs_impl(session_id: str, tail: int | None = None, stderr: bool = False, follow: bool = False) -> str | None:
    """
    Get or follow logs from a background session. Returns log text or None if following.
    """
    from rich.console import Console

    from thegent.cli.commands.impl import _default_owner_tag, _resolve_cwd, _session_paths
    from thegent.execution import AuditEntry, AuditRegistry

    console = Console()
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except Exception as e:
        return f"Error: {e}"

    p = _session_paths(base=meta_path.parent, session_id=session_id)
    target = p["stderr"] if stderr else p["stdout"]
    if not target.exists():
        return f"Log file missing: {target}"

    if follow:
        try:
            audit_path = meta_path.parent / f"{session_id}.audit.jsonl"
            audit = AuditRegistry(audit_path)
            audit.record(
                AuditEntry(
                    action="logs",
                    actor=str(_default_owner_tag(_resolve_cwd(None))),
                    session_id=session_id,
                    details={"follow": True, "stream": "stderr" if stderr else "stdout"},
                )
            )

            with target.open("r", encoding="utf-8", errors="replace") as f:
                if tail and tail > 0:
                    from thegent.utils.helpers import read_file_tail

                    lines = read_file_tail(target, num_lines=tail)
                    if lines:
                        for line in lines:
                            console.print(line)
                    f.seek(0, os.SEEK_END)
                else:
                    f.seek(0, os.SEEK_END)

                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    console.print(line, end="")
        except KeyboardInterrupt:
            return None
    else:
        audit_path = meta_path.parent / f"{session_id}.audit.jsonl"
        audit = AuditRegistry(audit_path)
        audit.record(
            AuditEntry(
                action="logs",
                actor=str(_default_owner_tag(_resolve_cwd(None))),
                session_id=session_id,
                details={"follow": False, "stream": "stderr" if stderr else "stdout"},
            )
        )

        from thegent.utils.helpers import read_file_tail, safe_read_file

        if tail is not None and tail > 0:
            lines = read_file_tail(target, num_lines=tail)
            if lines is None:
                return f"Error reading tail of {target}"
            log_text = "\n".join(lines)
        else:
            log_text = safe_read_file(target) or ""

        return log_text
