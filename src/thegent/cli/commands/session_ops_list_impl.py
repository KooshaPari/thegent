"""Session listing operations: ps, list.

Extracted from session_ops_impl.py as part of LOC reduction.
Contains:
- ps_impl: list active sessions from registry + legacy dirs
- session_list_impl: list all sessions including completed ones
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from thegent.execution import RunRegistry

_log = logging.getLogger(__name__)


def _session_meta_impl():
    from thegent.cli.commands import impl as cli_impl

    return cli_impl


def _settings() -> Any:
    from thegent.config import ThegentSettings

    return ThegentSettings()


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

    settings = _settings()
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
            else (r.get("prompt", "") or "—"),
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
                m = _session_meta_impl()._read_session_meta(json_file)
                owner_value = m.get("owner")
                if not all and owner_value and owner_value != own:
                    continue
                sid_value = m.get("session_id") or sid
                pid = int(m.get("pid", 0) or 0)
                running = pid > 0 and _is_pid_running(pid)
                rc_path = _session_paths(base=scope_dir, session_id=sid_value)["rc"]
                rc = rc_path.read_text(encoding="utf-8").strip() if rc_path.exists() else ""
                status_value = "running" if running else ("exited:" + rc if rc else m.get("status", "unknown"))
                row = {
                    "id": sid_value,
                    "run_id": m.get("run_id") or sid_value,
                    "agent": m.get("agent", "?"),
                    "owner": owner_value or scope_dir.name.replace("_", ":"),
                    "status": status_value,
                    "pid": pid,
                    "prompt_preview": (m.get("prompt", "")[:40] + "...")
                    if len(m.get("prompt", "")) > 40
                    else m.get("prompt", "") or "—",
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

    settings = _settings()
    own = owner or _default_owner_tag()
    root = settings.session_dir.expanduser().resolve()

    rows: list[dict[str, Any]] = []

    for state_path in root.glob("*/state.json"):
        try:
            payload = json_mod.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        session_id = _session_meta_impl()._normalize_contract_string(payload.get("session_id"))
        run_id = _session_meta_impl()._normalize_contract_string(payload.get("run_id"))
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
        correlation_id = _session_meta_impl()._normalize_contract_string(r.get("correlation_id") or r.get("run_id"))
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
                "run_id": _session_meta_impl()._normalize_contract_string(r.get("run_id")),
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
