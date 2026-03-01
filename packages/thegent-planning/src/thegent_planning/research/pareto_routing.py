"""Pareto Routing & Hysteresis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ParetoRouting:
    """Pareto-optimal routing with hysteresis."""

    def __init__(self) -> None:
        """Initialize Pareto routing."""
        from thegent_core.config import get_settings

        settings = get_settings()
        self.routes: dict[str, Any] = {}
        self.hysteresis_threshold = settings.routing_hysteresis_threshold

    def find_pareto_optimal(self, options: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Find Pareto-optimal options.

        Args:
            options: List of routing options with cost/quality metrics

        Returns:
            List of Pareto-optimal options
        """
        if not options:
            return []

        pareto_front = []
        for option in options:
            is_dominated = False
            for other in options:
                if (other["cost"] < option["cost"] and other["quality"] >= option["quality"]) or (
                    other["cost"] <= option["cost"] and other["quality"] > option["quality"]
                ):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto_front.append(option)

        logger.info(f"Found {len(pareto_front)} Pareto-optimal options")
        return pareto_front

    def apply_hysteresis(self, current_route: str, new_route: str, cost_diff: float) -> str:
        """Apply hysteresis to prevent route oscillation.

        Args:
            current_route: Current route
            new_route: Proposed new route
            cost_diff: Cost difference

        Returns:
            Selected route
        """
        if abs(cost_diff) < self.hysteresis_threshold:
            logger.info(f"Hysteresis: keeping current route {current_route}")
            return current_route
        return new_route
