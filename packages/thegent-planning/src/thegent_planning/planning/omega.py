"""WP-45001: Entropy-Minimizing Execution Loop (Omega).
Optimizes execution by minimizing planning entropy and pruning redundant actions.
"""

import logging
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class OmegaExecutionResult(BaseModel):
    """Result of an entropy-minimized execution step."""

    cycle_id: str
    entropy_score: float  # Lower is better (0.0 to 1.0)
    pruned_actions: list[str]
    executed_actions: list[str]
    efficiency_gain: float


class OmegaLoop:
    """The final-stage execution loop for thegent (Phase 45).
    Focuses on minimizing entropy (wasted effort, redundant plans, and uncertainty).
    """

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self.history: list[OmegaExecutionResult] = []

    def calculate_entropy(self, plan: list[dict[str, Any]]) -> float:
        """Calculate the entropy (unpredictability/redundancy) of a proposed plan."""
        if not plan:
            return 0.0

        # Simple entropy heuristic: number of overlapping dependencies vs total actions
        unique_deps: set[str] = set()
        total_actions = len(plan)

        for action in plan:
            deps = action.get("depends_on", [])
            if isinstance(deps, list):
                unique_deps.update(deps)

        # Entropy is higher if there are many interdependent actions with few unique root dependencies
        # (indicating high potential for cascading failure/rework)
        if total_actions == 0:
            return 0.0

        # Heuristic calculation for demo purposes
        entropy = len(unique_deps) / (total_actions * 2)
        return min(entropy, 1.0)

    def minimize_entropy(self, cycle_id: str, proposed_plan: list[dict[str, Any]]) -> OmegaExecutionResult:
        """Optimize a plan by pruning redundant or high-entropy actions."""
        _log.info("Starting Omega entropy minimization for cycle %s", cycle_id)

        initial_entropy = self.calculate_entropy(proposed_plan)
        pruned_actions: list[str] = []
        executed_actions_ids: list[str] = []

        # Rule 1: Prune duplicate actions (actions with same ID or content)
        seen_actions: set[str] = set()
        for action in proposed_plan:
            action_id = action.get("id", "unknown")
            content_key = str(action.get("payload", ""))

            if action_id in seen_actions or content_key in seen_actions:
                _log.debug("Pruning redundant action: %s", action_id)
                pruned_actions.append(action_id)
            else:
                seen_actions.add(action_id)
                seen_actions.add(content_key)
                executed_actions_ids.append(action_id)

        # Re-calculate entropy for the pruned plan
        pruned_plan = [a for a in proposed_plan if a.get("id") in executed_actions_ids]
        final_entropy = self.calculate_entropy(pruned_plan)
        efficiency_gain = max(0.0, initial_entropy - final_entropy)

        result = OmegaExecutionResult(
            cycle_id=cycle_id,
            entropy_score=final_entropy,
            pruned_actions=pruned_actions,
            executed_actions=executed_actions_ids,
            efficiency_gain=efficiency_gain,
        )

        self.history.append(result)
        _log.info(
            "Omega optimization complete: %d actions pruned, efficiency gain %.2f", len(pruned_actions), efficiency_gain
        )
        return result
