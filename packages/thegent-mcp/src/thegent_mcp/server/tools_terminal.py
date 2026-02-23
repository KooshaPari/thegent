"""Handoff and terminal-route tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from pathlib import Path
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def handoff_impl(
    *,
    owner: str,
    cd: str | None,
    resolve_cwd: Callable[[Path | None], Path | None],
    error_result: Callable[..., ToolResult],
    settings_factory: Callable[[], Any],
    escalate_list_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    from thegent.execution import HandoffManager, RunRegistry

    cwd = resolve_cwd(Path(cd) if cd else None)
    if cwd is None:
        return error_result("Ambiguous cwd.", "Provide cd=/path", extra={})
    settings = settings_factory()
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=50)
    run_ids = [r["run_id"] for r in runs if r.get("status") == "running"]
    escalation_items = escalate_list_impl(past_sla_only=False, limit=50)
    escalation_run_ids = [e["run_id"] for e in escalation_items]
    past_sla = escalate_list_impl(past_sla_only=True, limit=50)
    state_summary = {
        "running_count": len(run_ids),
        "escalation_backlog": len(escalation_run_ids),
        "past_sla_count": len(past_sla),
    }
    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    evidence_summary = [
        {"run_id": r.get("run_id"), "status": r.get("status"), "agent": r.get("agent")}
        for r in (completed[-5:] + failed[-5:])
    ]
    next_steps: list[str] = []
    if past_sla:
        next_steps.append(f"Resolve {len(past_sla)} past-SLA escalation(s)")
    if failed:
        next_steps.append(f"Review {len(failed)} failed run(s)")
    if run_ids:
        next_steps.append(f"Monitor {len(run_ids)} active run(s)")
    hm = HandoffManager(settings.session_dir)
    snapshot_id = hm.create_snapshot(
        owner,
        run_ids,
    )
    result = {
        "snapshot_id": snapshot_id,
        "owner": owner,
        "run_ids": run_ids,
        "state_summary": state_summary,
        "evidence_summary": evidence_summary,
        "next_steps": next_steps,
    }
    return ToolResult(
        content=json.dumps(result).decode().decode(),
        structured_content=result,
        meta={"execution_time_ms": 0},
    )


def handoff_list_impl(
    *,
    limit: int,
    settings_factory: Callable[[], Any],
) -> ToolResult:
    from thegent.execution import HandoffManager

    settings = settings_factory()
    hm = HandoffManager(settings.session_dir)
    snapshots = hm.list_pending_snapshots(limit=limit)
    return ToolResult(
        content=json.dumps(snapshots).decode().decode(),
        structured_content=snapshots,
        meta={"count": len(snapshots)},
    )


def handoff_show_impl(
    *,
    snapshot_id: str,
    settings_factory: Callable[[], Any],
    error_result: Callable[..., ToolResult],
) -> ToolResult:
    from thegent.execution import HandoffManager

    settings = settings_factory()
    hm = HandoffManager(settings.session_dir)
    snap = hm.get_snapshot(snapshot_id)
    if not snap:
        return error_result(f"Snapshot {snapshot_id} not found.", "Run thegent_handoff_list", extra={})
    return ToolResult(
        content=json.dumps(snap).decode().decode(),
        structured_content=snap,
        meta={},
    )


def handoff_confirm_impl(
    *,
    snapshot_id: str,
    incoming_owner: str,
    confidence: float,
    settings_factory: Callable[[], Any],
) -> ToolResult:
    from thegent.execution import HandoffManager

    settings = settings_factory()
    hm = HandoffManager(settings.session_dir)
    ok = hm.confirm_handoff(snapshot_id=snapshot_id, incoming_owner=incoming_owner, confidence=confidence)
    return ToolResult(
        content=json.dumps({"success": ok, "snapshot_id": snapshot_id}).decode().decode(),
        structured_content={"success": ok, "snapshot_id": snapshot_id},
        meta={},
    )


def terminal_route_impl(
    *,
    prompt: str,
    cd: str | None,
) -> ToolResult:
    from thegent.config import ThegentSettings
    from thegent.utils.routing_impl.task_router import TaskRouter
    from thegent.skills.terminal import send_to_tmux_pane

    settings = ThegentSettings()
    router = TaskRouter(settings)
    target_path = str(cd or Path.cwd())
    pane_id = router.find_active_terminal_for_path(target_path)
    if pane_id:
        success = send_to_tmux_pane(pane_id, prompt)
        return ToolResult(
            content=json.dumps({"routed": True, "pane_id": pane_id, "success": success}).decode().decode(),
            structured_content={"routed": True, "pane_id": pane_id, "success": success},
            meta={},
        )
    return ToolResult(
        content=json.dumps({"routed": False, "fallback": "Use thegent_run or thegent_bg"}).decode().decode(),
        structured_content={"routed": False, "fallback": "Use thegent_run or thegent_bg"},
        meta={},
    )


def thegent_terminal_attach_impl(
    *,
    pane_id: str,
    list_tmux_panes: Callable[[], list[Any]],
    error_result_impl: Callable[..., ToolResult],
) -> ToolResult:
    start_time = time.perf_counter()
    panes = list_tmux_panes()
    pane = next((item for item in panes if item.pane_id == pane_id), None)
    if not pane:
        return error_result_impl("Pane not found.", "Run: thegent terminal_list", extra={"pane_id": pane_id})

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    command = f"tmux attach-session -t {pane.session_name}"
    msg = f"To attach to this session, run: {command}"
    return ToolResult(
        content=msg,
        structured_content={"session": pane.session_name, "command": command},
        meta={"execution_time_ms": elapsed_ms},
    )
