"""Cost sensitivity experiment framework."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CostSensitivityFramework:
    """Framework for cost sensitivity experiments."""

    def __init__(self):
        """Initialize cost sensitivity framework."""
        self.experiments: list[dict[str, Any]] = []

    def run_experiment(self, baseline_cost: float, variant_cost: float) -> dict[str, Any]:
        """Run a cost sensitivity experiment.
        
        Args:
            baseline_cost: Baseline cost
            variant_cost: Variant cost
            
        Returns:
            Experiment results
        """
        savings = baseline_cost - variant_cost
        savings_percent = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        
        return {
            "baseline_cost": baseline_cost,
            "variant_cost": variant_cost,
            "savings": savings,
            "savings_percent": savings_percent,
        }

    def analyze_cost_patterns(self, cost_history: list[float]) -> dict[str, Any]:
        """Analyze cost patterns.
        
        Args:
            cost_history: Historical cost data
            
        Returns:
            Analysis results
        """
        if not cost_history:
            return {}
        
        avg_cost = sum(cost_history) / len(cost_history)
        max_cost = max(cost_history)
        min_cost = min(cost_history)
        
        return {
            "average": avg_cost,
            "max": max_cost,
            "min": min_cost,
            "range": max_cost - min_cost,
        }
