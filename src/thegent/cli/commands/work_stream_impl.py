"""Work stream management: parse, collect, claim, complete, incorporate, do-next, wait-next, spawn-next.

Extracted from impl.py as part of WL-120 LOC Reduction Program (Phase 2).
Contains:
- WORK_STREAM.md parsing and dependency checking
- Priority sorting and item collection
- Queue collection (PromptQueue, EscalationQueue, DeferralManager, BacklogManager)
- Pre-work governance hard gate
- do_next_impl, wait_next_impl, spawn_next_impl
- work_stream_claim_impl, work_stream_complete_impl, incorporate_impl
- continuity_snapshot_impl
- _validate_task_and_record_errors
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from thegent.cli.services import pre_work_gate_helpers
from thegent.cli.services import work_stream_orchestration


# ---------------------------------------------------------------------------
# Public API: do-next, wait-next, spawn-next, claim, complete, incorporate
# ---------------------------------------------------------------------------

_log = __import__("logging").getLogger(__name__)


def _pre_work_gate_defaults() -> dict[str, Any]:
    """Wrapper for pre-work gate defaults helper."""
    return pre_work_gate_helpers.pre_work_gate_defaults()


def _pre_work_gate_thresholds(project_dir: Path) -> tuple[dict[str, Any], str]:
    """Wrapper for pre-work gate thresholds helper."""
    return pre_work_gate_helpers.pre_work_gate_thresholds(project_dir)


def _evidence_age_minutes(path: Path) -> int:
    """Wrapper for evidence-age helper."""
    return pre_work_gate_helpers.evidence_age_minutes(path)


def _pre_work_governance_block_payload(
    *,
    project_dir: Path,
    thresholds: dict[str, Any],
    violations: list[dict[str, Any]],
    config_source: str,
) -> dict[str, Any]:
    """Wrapper for governance block payload helper."""
    return pre_work_gate_helpers.pre_work_governance_block_payload(
        project_dir=project_dir,
        thresholds=thresholds,
        violations=violations,
        config_source=config_source,
    )


def _enforce_pre_work_hard_gate(project_dir: Path) -> dict[str, Any] | None:
    """Wrapper for pre-work hard gate helper."""
    return pre_work_gate_helpers.enforce_pre_work_hard_gate(project_dir)


def _validate_task_and_record_errors(tf: Path, validation_errors: list[dict[str, Any]]) -> None:
    """Wrapper for orchestration validation helper."""
    return work_stream_orchestration._validate_task_and_record_errors(tf, validation_errors)


_PRE_WORK_WRAPPER_EXPORTS = (
    _pre_work_gate_defaults,
    _pre_work_gate_thresholds,
    _evidence_age_minutes,
    _pre_work_governance_block_payload,
    _enforce_pre_work_hard_gate,
    _validate_task_and_record_errors,
)


def do_next_impl(cd: Path | None = None, limit: int = 5) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.do_next_impl(cd=cd, limit=limit)


def wait_next_impl(
    cd: Path | None = None,
    poll_interval: float = 2.0,
    timeout: float = 0.0,
    sources: tuple[str, ...] = ("do_next",),
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.wait_next_impl(
        cd=cd,
        poll_interval=poll_interval,
        timeout=timeout,
        sources=sources,
    )


def spawn_next_impl(
    cd: Path | None = None,
    limit: int = 10,
    agent: str = "free",
    timeout: int | None = None,
    lane: str = "critical",
    override_reason: str = "manual-next-step",
    claim: bool = True,
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.spawn_next_impl(
        cd=cd,
        limit=limit,
        agent=agent,
        timeout=timeout,
        lane=lane,
        override_reason=override_reason,
        claim=claim,
    )


def work_stream_claim_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def work_stream_complete_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def incorporate_impl(cd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.incorporate_impl(cd=cd, dry_run=dry_run)


def continuity_snapshot_impl(
    owner: str,
    run_ids: list[str],
    state_summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
    )
