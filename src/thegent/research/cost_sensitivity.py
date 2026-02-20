"""Cost sensitivity experiment framework."""

import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CostSensitivityFramework:
    """Framework for cost sensitivity experiments."""

    def __init__(
        self,
        baseline_config: dict[str, Any],
        experiment_a_config: dict[str, Any],
        experiment_b_config: dict[str, Any],
    ) -> None:
        """Initialize cost sensitivity framework with configurations."""
        self.configs = {
            "baseline": baseline_config,
            "experiment_a": experiment_a_config,
            "experiment_b": experiment_b_config,
        }
        self.results: dict[str, list[dict[str, Any]]] = {
            "baseline": [],
            "experiment_a": [],
            "experiment_b": [],
        }

    def record_metric(self, variant: str, latency_ms: float, cost: float, success: bool, sla_breach: bool):
        """Record metrics for a specific experiment variant."""
        if variant not in self.results:
            return

        self.results[variant].append(
            {
                "timestamp": time.time(),
                "latency_ms": latency_ms,
                "cost": cost,
                "success": success,
                "sla_breach": sla_breach,
            }
        )

    def run_experiment(self, variant: str, action_fn: Any) -> dict[str, Any]:
        """Run a single action and record metrics."""
        start_time = time.perf_counter()
        try:
            # Simulate action with config-specific depth
            config = self.configs.get(variant, {})
            depth = config.get("policy_depth", 1)
            # Simulate policy lookup overhead
            time.sleep(depth * 0.01)

            res = action_fn()
            latency = (time.perf_counter() - start_time) * 1000

            # Assume cost is related to model but fixed for simulation
            cost = 0.05 if variant == "baseline" else (0.04 if variant == "experiment_a" else 0.03)

            sla_breach = latency > 200  # 200ms SLA

            self.record_metric(variant, latency, cost, True, sla_breach)
            return {"status": "success", "latency": latency}
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            self.record_metric(variant, latency, 0, False, False)
            return {"status": "error", "error": str(e)}

    def analyze(self) -> dict[str, Any]:
        """Analyze all experiment results."""
        analysis = {}
        for variant, data in self.results.items():
            if not data:
                continue

            avg_latency = sum(d["latency_ms"] for d in data) / len(data)
            avg_cost = sum(d["cost"] for d in data) / len(data)
            success_rate = sum(1 for d in data if d["success"]) / len(data)
            sla_breach_rate = sum(1 for d in data if d["sla_breach"]) / len(data)

            analysis[variant] = {
                "avg_latency_ms": avg_latency,
                "avg_cost": avg_cost,
                "success_rate": success_rate,
                "sla_breach_rate": sla_breach_rate,
                "sample_count": len(data),
            }

        return analysis
