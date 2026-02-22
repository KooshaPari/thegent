"""Session control operations: wait, stop, send, history, metrics, prune, events,
meta, negotiate, purge, explain.

Extracted from session_ops_impl.py as part of WL-120 max-lines enforcement.
Contains:
- wait_impl: wait for a background session to complete
- session_send_impl: send a message to a running session
- stop_impl: stop a background session
- history_impl: list execution history
- metrics_impl: gather metrics for the agent registry
- prune_sessions_impl: prune old session data
- events_impl: list raw telemetry events
- session_meta_impl: get full session metadata
- session_contract_negotiate_impl: contract negotiation
- purge_impl: tiered retention purge
- explain_run_impl: multi-tier explanation for run decisions
"""

from __future__ import annotations

import json
import logging
import os
import signal
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import typer

from thegent.cli.commands.session_meta_impl import (
    _find_session_meta,
    _read_session_meta,
)
from thegent.config import ThegentSettings
from thegent.execution import RunRegistry

_log = logging.getLogger(__name__)


def wait_impl(session_id: str, timeout: int | None = None) -> dict[str, Any]:
    """
    Wait for a background session to complete.
    """
    from thegent.cli.commands.impl import _is_pid_running, _session_paths

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    p = _session_paths(base=meta_path.parent, session_id=session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    start = time.time()
    timed_out = False
    while _is_pid_running(pid):
        if timeout and timeout > 0 and (time.time() - start) >= timeout:
            timed_out = True
            break
        time.sleep(0.5)
    rc = int(p["rc"].read_text(encoding="utf-8").strip()) if p["rc"].exists() else 0
    return {
        "session_id": session_id,
        "exit_code": rc,
        "timed_out": timed_out,
    }


def session_send_impl(session_id: str, message: str, msg_type: str = "reprompt") -> tuple[bool, str]:
    """Send a message to a running session by queuing it in the registry (WP-9004)."""
    from thegent.cli.commands.impl import _default_owner_tag, _resolve_cwd
    from thegent.execution import AuditEntry, AuditRegistry, MessageEntry, MessageRegistry

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except Exception as e:
        return False, f"Session {session_id} not found: {e}"

    msg_path = meta_path.parent / f"{session_id}.messages.jsonl"

    registry = MessageRegistry(msg_path)
    entry = MessageEntry(
        type=msg_type,
        content=message,
        sender="user",
    )
    registry.push(entry)

    audit_path = meta_path.parent / f"{session_id}.audit.jsonl"
    audit = AuditRegistry(audit_path)
    audit.record(
        AuditEntry(
            action="send",
            actor=_default_owner_tag(_resolve_cwd(None)),
            session_id=session_id,
            details={"type": msg_type, "content_len": len(message)},
        )
    )

    sent_via = ["registry"]

    m = _read_session_meta(meta_path)
    attach_target = m.get("attach_target") or {}
    tmux_pane = attach_target.get("tmux_pane")
    if m.get("interactivity") == "tmux" or tmux_pane:
        if tmux_pane:
            import subprocess

            try:
                subprocess.run(["tmux", "send-keys", "-t", tmux_pane, message, "C-m"], check=False)
                sent_via.append("tmux")
            except Exception as exc:
                _log.warning("TMUX send failed for session %s: %s", session_id, exc)

    fifo_path = meta_path.parent / f"{session_id}.in"
    if fifo_path.exists():
        try:
            fd = os.open(str(fifo_path), os.O_WRONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "w") as f:
                f.write(message + "\n")
            sent_via.append("fifo")
        except OSError as exc:
            _log.warning("FIFO send failed for session %s: %s", session_id, exc)

    return True, f"Message queued/sent via {', '.join(sent_via)}."


def stop_impl(session_id: str, force: bool = False) -> dict[str, Any]:
    """
    Stop a background session.
    """
    from thegent.cli.commands.impl import _is_pid_running

    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
    except typer.BadParameter as e:
        return {"error": str(e), "session_id": session_id}
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    if not _is_pid_running(pid):
        return {"session_id": session_id, "status": "not_running"}
    try:
        if force:
            os.killpg(pid, signal.SIGKILL)
            return {"session_id": session_id, "status": "stopped_force"}
        os.killpg(pid, signal.SIGTERM)
        return {"session_id": session_id, "status": "stopped"}
    except OSError as e:
        return {"session_id": session_id, "status": "error", "error": str(e)}


def history_impl(limit: int = 50) -> list[dict[str, Any]]:
    """
    List execution history from the run registry.
    """
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    return registry.list_runs(limit=limit)


def metrics_impl() -> dict[str, Any]:
    """Gather metrics for the agent registry (WP-9005)."""
    from thegent.cli.commands.session_ops_impl import ps_impl

    sessions = ps_impl(all=True)
    stats = {
        "active_sessions": sum(1 for s in sessions if s.get("status") == "running"),
        "total_sessions": len(sessions),
        "by_agent": {},
        "by_status": {},
    }
    for s in sessions:
        agent = s.get("agent", "unknown")
        stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
        status = s.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    return stats


def prune_sessions_impl(days: int | None = None) -> dict[str, Any]:
    """Prune old session data (WP-3006)."""
    from thegent.cli.commands.impl import _is_pid_running, _session_paths

    settings = ThegentSettings()
    retention_days = days or settings.retention_days_sessions
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)

    base = settings.session_dir.expanduser().resolve()
    pruned_count = 0
    errors = 0

    for scope_dir in base.glob("*"):
        if not scope_dir.is_dir():
            continue
        for meta_file in scope_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(meta_file.stat().st_mtime, tz=UTC)
                if mtime < cutoff:
                    m = json.loads(meta_file.read_text())
                    if m.get("status") == "running" and _is_pid_running(m.get("pid", 0)):
                        continue  # Don't prune running sessions

                    session_id = meta_file.stem
                    p = _session_paths(base=scope_dir, session_id=session_id)
                    for path in p.values():
                        if path.exists():
                            path.unlink()
                    if meta_file.exists():
                        meta_file.unlink()
                    pruned_count += 1
            except Exception:
                errors += 1

    return {"pruned": pruned_count, "errors": errors, "cutoff": cutoff.isoformat()}


def events_impl(run_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """
    List raw telemetry events from the run registry.
    """
    settings = ThegentSettings()
    registry_path = settings.session_dir / "run_registry.jsonl"
    if not registry_path.exists():
        return []

    events: list[dict[str, Any]] = []
    with registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if run_id and data.get("run_id") != run_id:
                    continue
                events.append(data)
            except Exception:
                continue

    return events[-limit:]


def session_meta_impl(session_id: str) -> dict[str, Any]:
    """Get full session metadata. Returns meta dict or error."""
    settings = ThegentSettings()
    try:
        meta_path = _find_session_meta(settings, session_id)
        return _read_session_meta(meta_path)
    except typer.BadParameter as e:
        return {"error": str(e)}


def session_contract_negotiate_impl(contract_id: str, supported_versions: list[str]) -> dict[str, Any]:
    """
    WP-7001: Implementation of contract negotiation logic.
    """
    from thegent.contracts.registry import ContractNegotiator

    negotiator = ContractNegotiator()
    return negotiator.negotiate(contract_id, supported_versions)


def purge_impl(dry_run: bool = True) -> dict[str, int]:
    """WP-3006: Tiered retention purge implementation (G-GP-07)."""
    from typing import cast

    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    default_days = settings.retention_days_registry
    by_domain = settings.retention_by_domain

    _purge: Any = getattr(registry, "purge_expired", None)
    if callable(_purge):
        return cast(
            "dict[str, int]",
            _purge(default_days=default_days, by_domain=by_domain, dry_run=dry_run),
        )
    return {"kept": 0, "purged": 0}


def explain_run_impl(run_id: str) -> dict[str, Any]:
    """WP-4002: Multi-tier explanation framework for run decisions."""
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)

    runs = registry.list_runs(limit=100)
    run = next((r for r in runs if r.get("run_id") == run_id), None)

    if not run:
        return {"error": f"Run {run_id} not found", "exit_code": 1}

    concise = run.get("policy_reason") or run.get("error_class") or "No concise rationale available."
    detailed = run.get("rationale") or "No detailed rationale available."

    return {
        "run_id": run_id,
        "concise_rationale": concise,
        "detailed_rationale": detailed,
        "agent": run.get("agent"),
        "status": run.get("status"),
        "confidence": run.get("confidence"),
    }
