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

from thegent.cli.services import work_stream_orchestration




# ---------------------------------------------------------------------------
# Public API: do-next, wait-next, spawn-next, claim, complete, incorporate
# ---------------------------------------------------------------------------

_log = __import__("logging").getLogger(__name__)


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
