"""WP-20002: Neural-Symbolic Hybrid Router.
Combines symbolic risk assessment with neural model capabilities for safety-first routing.
"""

import logging
from typing import Any

from thegent.models.catalog import ModelCatalog, RoutePolicy
from thegent.verification.symbolic import SymbolicRiskExplorer

_log = logging.getLogger(__name__)


class HybridRouter:
    """Combines LLM (Neural) and Symbolic (Formal) methods for model routing."""

    def __init__(self, dag: Any) -> None:
        self.symbolic_explorer = SymbolicRiskExplorer(dag)
        self.catalog = ModelCatalog()

    def route_safely(self, task_type: str, prompt: str, start_node: str) -> tuple[str, str]:
        """Route to a model based on both neural capability and symbolic safety."""
        _log.info("Hybrid routing task: %s (Start: %s)", task_type, start_node)

        # 1. Symbolic Safety Check
        risk_paths = self.symbolic_explorer.explore(start_node)
        high_risk = self.symbolic_explorer.get_highest_risk_path()
        risk_score = high_risk.risk_score if high_risk else 0.0

        # 2. Neural/Standard Route Selection
        # If risk is high, force a higher-quality (more capable/safe) model policy
        policy: RoutePolicy = "roi"
        if risk_score > 0.6:
            _log.warning("High risk detected (score: %s). Escalating to mission_critical policy.", risk_score)
            policy = "pareto"  # Pareto quality-first

        # 3. Resolve route using ModelCatalog
        # In a real system, this might use the risk_score as a parameter to resolve_route
        from thegent.models.catalog import resolve_route

        route = resolve_route(model_id="deepseek-v3.2", policy=policy, quality_floor=risk_score)

        if not route:
            # Fallback to ultra-safe
            _log.warning("No route found for hybrid policy. Falling back to claude-opus-4.6")
            return ("claude", "claude-opus-4.6")

        _log.info("Hybrid routing complete: %s/%s (Risk: %s)", route[0], route[1], risk_score)
        return route
