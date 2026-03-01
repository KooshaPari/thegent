"""WP-18004: Automated Formal Verification Loop.
Continously runs symbolic execution and logical verification on the active plan.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from thegent.verification.symbolic import SymbolicRiskExplorer

_log = logging.getLogger(__name__)


class FormalVerificationLoop:
    """Automated loop that periodically verifies the agent's plan for logical consistency."""

    def __init__(self, plan_dag: Any) -> None:
        self.explorer = SymbolicRiskExplorer(plan_dag)
        self.last_run = None
        self.verifications = []

    def run(self, start_task: str) -> dict[str, Any]:
        """Execute a formal verification pass."""
        _log.info("Running formal verification loop for plan starting at: %s", start_task)

        # 1. Run symbolic execution
        risk_paths = self.explorer.explore(start_task)

        # 2. Analyze highest risk path
        high_risk = self.explorer.get_highest_risk_path()

        # 3. Create verification verdict
        verdict = "VERIFIED"
        if high_risk and high_risk.risk_score > 0.7:
            verdict = "GAPS: Potential high-risk path detected"

        result = {
            "timestamp": datetime.now(UTC).isoformat(),
            "start_task": start_task,
            "verdict": verdict,
            "paths_explored": len(risk_paths),
            "highest_risk": high_risk.__dict__ if high_risk else None,
        }

        self.verifications.append(result)
        self.last_run = result

        _log.info("Formal verification verdict: %s", verdict)
        return result

    def get_history(self) -> list[dict[str, Any]]:
        """Return history of verification passes."""
        return self.verifications
