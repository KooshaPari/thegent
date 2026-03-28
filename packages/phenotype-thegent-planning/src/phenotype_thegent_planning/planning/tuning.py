"""WP-14004: Auto-generated runbook tuning and operational recommendations."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class TuningRecommendation:
    id: str
    metric: str
    current_value: float
    recommended_action: str
    rationale: str
    impact_estimate: str
    created_at: str = datetime.now(UTC).isoformat()


class RunbookTuner:
    """Recommends operational tuning actions based on system performance (WP-14004)."""

    def __init__(self, slo_metrics: dict[str, Any]) -> None:
        self.slo_metrics = slo_metrics

    def generate_recommendations(self) -> list[TuningRecommendation]:
        """Analyze metrics and generate tuning recommendations."""
        recs = []

        # 1. Check for sustained latency issues
        if self.slo_metrics.get("consecutive_breaches", 0) >= 3:
            recs.append(
                TuningRecommendation(
                    id="TUNE-LAT-001",
                    metric="latency",
                    current_value=self.slo_metrics["current_ms"],
                    recommended_action="Increase 'latency' weight in ObjectiveSelector by 0.1",
                    rationale="Sustained latency breaches detected by SLORegulator.",
                    impact_estimate="Expected to favor faster flash models.",
                )
            )

        # 2. Check for budget pressure
        budget_utilization = self.slo_metrics.get("budget_utilization", 0.0)
        if budget_utilization > 0.8:
            recs.append(
                TuningRecommendation(
                    id="TUNE-COST-001",
                    metric="budget",
                    current_value=budget_utilization,
                    recommended_action="Enable 'cheapest' objective profile globally.",
                    rationale=f"Budget utilization is at {budget_utilization:.1%}.",
                    impact_estimate="Will reduce spend by approx 30% while increasing latency.",
                )
            )

        # 3. Check for high success rates (potential for cost optimization)
        success_rate = self.slo_metrics.get("success_rate", 1.0)
        if success_rate > 0.98 and budget_utilization > 0.5:
            recs.append(
                TuningRecommendation(
                    id="TUNE-OPT-001",
                    metric="success_rate",
                    current_value=success_rate,
                    recommended_action="Shift 0.1 weight from 'quality' to 'cost'.",
                    rationale="Success rate is very high; opportunity for cost optimization.",
                    impact_estimate="Slightly lower quality models with significantly lower cost.",
                )
            )

        return recs
