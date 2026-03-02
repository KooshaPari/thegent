"""WP-20002: Neural-Symbolic Hybrid Router.
Combines symbolic risk assessment with neural model capabilities for safety-first routing.

Circular-dependency note
------------------------
This module previously imported SymbolicRiskExplorer directly from
thegent_audit.verification.symbolic, creating a Core ↔ Audit cycle.
It now accepts any object satisfying the SymbolicRiskPort protocol defined in
thegent_core.ports.driven.symbolic_risk.  The concrete SymbolicRiskExplorer
(from thegent-audit) is injected by callers that have access to that package.
"""

import logging
from typing import Any

from thegent_core.models.catalog import ModelCatalog, RoutePolicy
from thegent_core.ports.driven.symbolic_risk import NullSymbolicRiskPort, SymbolicRiskPort

_log = logging.getLogger(__name__)


class HybridRouter:
    """Combines LLM (Neural) and Symbolic (Formal) methods for model routing."""

    def __init__(self, dag: Any, symbolic_explorer: SymbolicRiskPort | None = None) -> None:
        # Accept an injected explorer; fall back to the null-object so the
        # module can be imported even when thegent-audit is absent.
        if symbolic_explorer is None:
            symbolic_explorer = NullSymbolicRiskPort(dag)
            _log.debug(
                "HybridRouter: no SymbolicRiskPort injected; using NullSymbolicRiskPort. "
                "Pass a concrete SymbolicRiskExplorer from thegent-audit for live risk assessment."
            )
        self.symbolic_explorer: SymbolicRiskPort = symbolic_explorer
        self.catalog = ModelCatalog()

    def route_safely(self, task_type: str, prompt: str, start_node: str) -> tuple[str, str]:
        """Route to a model based on both neural capability and symbolic safety."""
        _log.info("Hybrid routing task: %s (Start: %s)", task_type, start_node)

        # 1. Symbolic Safety Check
        _risk_paths = self.symbolic_explorer.explore(start_node)
        high_risk = self.symbolic_explorer.get_highest_risk_path()
        risk_score = high_risk.risk_score if high_risk else 0.0

        # 2. Neural/Standard Route Selection
        # If risk is high, force a higher-quality (more capable/safe) model policy
        policy: RoutePolicy = "cheapest"
        if risk_score > 0.6:
            _log.warning("High risk detected (score: %s). Escalating to mission_critical policy.", risk_score)
            policy = "pareto"  # Pareto quality-first

        # 3. Resolve route using ModelCatalog
        # In a real system, this might use the risk_score as a parameter to resolve_route
        from thegent_core.models.catalog import resolve_route

        route = resolve_route(model_id="deepseek-v3.2", policy=policy, quality_floor=risk_score)

        if not route:
            # Fallback to ultra-safe
            _log.warning("No route found for hybrid policy. Falling back to claude-opus-4.6")
            return ("claude", "claude-opus-4.6")

        _log.info("Hybrid routing complete: %s/%s (Risk: %s)", route[0], route[1], risk_score)
        return route
