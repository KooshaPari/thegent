"""Observability escalation and sweep implementations (WL-120).

Escalation queue operations and policy sweep.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from thegent_cli.cli.services import governance as governance_service
from thegent_cli.cli.services import observability as observability_service
from thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)

__all__ = [
    "_extract_agent_from_line",
    "_process_run_line",
    "escalate_add_impl",
    "escalate_approve_impl",
    "escalate_list_impl",
    "escalate_resolve_impl",
    "update_calibration_impl",
    "sweep_impl",
]


def escalate_add_impl(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    agent: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> None:
    """WP-3008: Add a blocked run to the escalation queue."""
    governance_service.escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        agent=agent,
        lane=lane,
        priority=priority,
    )


def escalate_approve_impl(run_id: str) -> bool:
    """WP-3008: Approve an escalation, marking it as approved in the queue (G-GP-05)."""
    return governance_service.escalate_approve_impl(run_id)


def escalate_list_impl(past_sla_only: bool = False, limit: int = 50) -> list[dict[str, Any]]:
    """WP-3008: List escalation queue items (blocked runs with SLA)."""
    return governance_service.escalate_list_impl(past_sla_only=past_sla_only, limit=limit)


def escalate_resolve_impl(run_id: str, resolution: str = "resolved") -> bool:
    """WP-3008: Mark an escalation item as resolved."""
    return governance_service.escalate_resolve_impl(run_id=run_id, resolution=resolution)


def _extract_agent_from_line(agents: set[str], line: str) -> None:
    """Extract agent name from a single registry line."""
    import orjson as json

    try:
        data = json.loads(line)
        a = data.get("agent")
        if a:
            agents.add(a)
    except Exception as exc:
        _log.debug("Failed to parse run registry line: %s", exc)


def _process_run_line(runs: dict[str, dict[str, Any]], line: str, agent: str) -> None:
    """Process a single run line for a specific agent."""
    import orjson as json

    try:
        data = json.loads(line)
        rid = data.get("run_id")
        if not rid:
            return
        if data.get("event") == "finish":
            if rid in runs:
                runs[rid].update(data)
        elif data.get("event") == "feedback":
            if rid in runs:
                runs[rid]["feedback_score"] = data.get("feedback_score")
        elif data.get("agent") == agent:
            runs[rid] = data
    except Exception as exc:
        _log.debug("Failed to process run registry line for %s: %s", agent, exc)


def update_calibration_impl() -> dict[str, Any]:
    """G-GP-09: Recalculate and persist calibration factors for all agents."""
    from thegent_execution.execution import CalibrationRegistry, RunRegistry

    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    registry = RunRegistry(session_dir)
    cal = CalibrationRegistry(session_dir)

    if not registry.registry_path.exists():
        return {}

    agents: set[str] = set()
    with registry.registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            _extract_agent_from_line(agents, line)

    results: dict[str, Any] = {}
    for agent in agents:
        runs: dict[str, dict[str, Any]] = {}

        with registry.registry_path.open("r", encoding="utf-8") as f:
            for line in f:
                _process_run_line(runs, line, agent)

        relevant_runs = [r for r in runs.values() if r.get("feedback_score") is not None]
        if not relevant_runs:
            continue

        avg_feedback = sum(float(r["feedback_score"]) for r in relevant_runs) / len(relevant_runs)
        avg_confidence = sum(float(r.get("confidence") or 0.5) for r in relevant_runs) / len(relevant_runs)

        if avg_confidence > 0:
            factor = min(2.0, max(0.5, avg_feedback / avg_confidence))
            cal.update_agent(agent, factor, sample_size=len(relevant_runs))
            results[agent] = {"factor": factor, "samples": len(relevant_runs)}

    return results


def sweep_impl(
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    include_audit: bool = False,
) -> dict[str, Any]:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    return observability_service.sweep_impl(
        drift_window=drift_window,
        structural_budget=structural_budget,
        semantic_budget=semantic_budget,
        include_audit=include_audit,
        update_calibration_fn=update_calibration_impl,
    )
