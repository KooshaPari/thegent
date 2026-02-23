"""Session inspection and log operations: status, inspect, logs.

Extracted from session_impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2-split).
Listing operations (ps, session_list) extracted to session_ops_list_impl.py.
Contains:
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

from thegent.cli.commands.session_ops_list_impl import ps_impl as ps_impl

_log = logging.getLogger(__name__)

_LOG_FOLLOW_POLL_SECONDS = 0.5


def _session_meta_impl():
    from thegent.cli.commands import impl as cli_impl

    return cli_impl


def _settings() -> Any:
    from thegent.config import ThegentSettings

    return ThegentSettings()


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

    settings = _settings()
    try:
        meta_path = _session_meta_impl()._find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    p = _session_paths(base=meta_path.parent, session_id=session_id)
    m = _session_meta_impl()._read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _session_meta_impl()._resolve_session_status(m, p["rc"], running=running)
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
    settings = _settings()
    try:
        meta_path = _session_meta_impl()._find_session_meta(settings, session_id)
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
