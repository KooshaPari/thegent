"""WP-14005: Policy-safe exploration harness for candidate policy variants."""

from dataclasses import dataclass

from thegent_planning.planning.simulation import SimulationEngine


@dataclass
class ExplorationResult:
    variant_id: str
    base_run_id: str
    is_safe: bool
    cost_delta: float
    latency_delta: float
    recommendation: str


class PolicyExplorationHarness:
    """Harness for controlled simulation of candidate policy variants (WP-14005)."""

    def __init__(self, simulation_engine: SimulationEngine) -> None:
        self.engine = simulation_engine

    def explore_variant(self, variant_id: str, base_run_ids: list[str]) -> list[ExplorationResult]:
        """Run simulation across a set of historical runs for a policy variant."""
        results = []
        for rid in base_run_ids:
            # Simulate what-if for each historical run
            sim = self.engine.simulate_what_if(rid, target_env="sandbox")

            # Simplified outcome analysis
            is_safe = sim.get("allowed", False)
            cost_delta = -0.05  # Mock: variant reduces cost by 5%
            latency_delta = 100.0  # Mock: variant increases latency by 100ms

            results.append(
                ExplorationResult(
                    variant_id=variant_id,
                    base_run_id=rid,
                    is_safe=is_safe,
                    cost_delta=cost_delta,
                    latency_delta=latency_delta,
                    recommendation="PROCEED" if is_safe and cost_delta < 0 else "REJECT",
                )
            )
        return results
