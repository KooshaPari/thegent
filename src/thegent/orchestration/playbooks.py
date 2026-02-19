"""Recovery playbook automation (WP-2004, FR-008)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from thegent.orchestration.failure_modes import FailureMode, classify_failure

if TYPE_CHECKING:
    from pathlib import Path


def get_playbook_for_failure(error_message: str) -> list[str]:
    """Return ordered recovery steps for a failure (playbook)."""
    mode = classify_failure(error_message)
    playbooks: dict[FailureMode, list[str]] = {
        FailureMode.TIMEOUT: ["retry_with_backoff", "increase_timeout", "escalate"],
        FailureMode.RATE_LIMIT: ["wait_and_retry", "reduce_concurrency", "escalate"],
        FailureMode.AUTH_FAILURE: ["refresh_credentials", "escalate"],
        FailureMode.NETWORK_PARTITION: ["retry", "failover_provider", "escalate"],
        FailureMode.MALFORMED_RESPONSE: ["log_drift", "fallback_parser", "escalate"],
        FailureMode.STATE_CORRUPTION: ["rollback_checkpoint", "escalate"],
        FailureMode.BUDGET_EXCEEDED: ["pause_non_critical", "escalate"],
        FailureMode.CIRCUIT_OPEN: ["wait_recovery_window", "half_open_trial", "escalate"],
        FailureMode.POLICY_DENY: ["request_override", "escalate"],
        FailureMode.CONTRACT_DRIFT: ["emit_drift_event", "fallback_contract", "escalate"],
        FailureMode.RETRY_EXHAUSTED: ["dlq_enqueue", "escalate"],
        FailureMode.CHECKPOINT_FAILED: ["retry_checkpoint", "rollback", "escalate"],
        FailureMode.ROLLBACK_TRIGGERED: ["verify_rollback", "resume_or_escalate"],
        FailureMode.UNKNOWN: ["log", "escalate"],
    }
    return playbooks.get(mode, playbooks[FailureMode.UNKNOWN])


def execute_playbook_step(
    session_dir: Path,
    step: str,
    run_id: str,
    context: dict[str, object | None] | None = None,
) -> dict[str, object]:
    """Execute a single playbook step. Returns status dict."""
    ctx = context or {}
    if step == "escalate":
        from thegent.execution import EscalationQueue

        eq = EscalationQueue(session_dir)
        eq.add(run_id=run_id, agent=ctx.get("agent", ""), reason=str(ctx.get("reason", "playbook_escalation")))
        return {"step": step, "status": "escalated"}
    if step == "dlq_enqueue":
        from thegent.execution import DLQManager, RunMeta

        dlq = DLQManager(session_dir)
        meta = RunMeta(
            run_id=run_id,
            agent=str(ctx.get("agent", "")),
            prompt=str(ctx.get("prompt", "")),
            cwd=str(ctx.get("cwd", ".")),
            owner=str(ctx.get("owner", "system")),
        )
        dlq.enqueue(meta, str(ctx.get("error", "retry_exhausted")))
        return {"step": step, "status": "enqueued"}
    return {"step": step, "status": "pending", "message": f"Step {step} requires manual execution"}
