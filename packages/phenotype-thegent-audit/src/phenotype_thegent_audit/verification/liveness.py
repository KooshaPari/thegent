"""WP-25001: Liveness Proofs for Autonomous Agent Loops.
Ensures that an agent loop will eventually terminate or make progress.
Uses formal-inspired invariant checking on loop state history.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class LivenessViolation(BaseModel):
    """Details of a detected liveness violation."""

    type: str  # 'infinite_retry', 'no_progress', 'starvation'
    reason: str
    timestamp: str = datetime.now(UTC).isoformat()


class LivenessChecker:
    """Verifies liveness properties of autonomous execution loops."""

    def __init__(self, run_id: str, max_retries: int = 5, progress_timeout_s: int = 300) -> None:
        self.run_id = run_id
        self.max_retries = max_retries
        self.progress_timeout_s = progress_timeout_s
        self.history: list[dict[str, Any]] = []

    def record_step(self, step_type: str, state: dict[str, Any]):
        """Record a step in the agent loop for liveness analysis."""
        entry = {"timestamp": datetime.now(UTC).timestamp(), "step_type": step_type, "state": state}
        self.history.append(entry)

    def check_invariants(self) -> list[LivenessViolation]:
        """Check for liveness violations in the execution history."""
        violations = []

        if not self.history:
            return []

        # 1. Infinite Retry Invariant (L1)
        retry_count = sum(1 for h in self.history if h["step_type"] == "retry")
        if retry_count > self.max_retries:
            violations.append(
                LivenessViolation(
                    type="infinite_retry", reason=f"Retry count {retry_count} exceeds limit {self.max_retries}"
                )
            )

        # 2. No Progress Invariant (L2)
        # Check if state has changed significantly in the last few steps
        if len(self.history) >= 3:
            last_three = self.history[-3:]
            if all(h["state"] == last_three[0]["state"] for h in last_three):
                violations.append(
                    LivenessViolation(type="no_progress", reason="State has not changed for 3 consecutive steps")
                )

        # 3. Temporal Progress Invariant (L3)
        time_since_last_progress = datetime.now(UTC).timestamp() - self.history[-1]["timestamp"]
        if time_since_last_progress > self.progress_timeout_s:
            violations.append(
                LivenessViolation(
                    type="starvation",
                    reason=f"No progress for {time_since_last_progress:.1f}s (exceeds {self.progress_timeout_s}s)",
                )
            )

        return violations
