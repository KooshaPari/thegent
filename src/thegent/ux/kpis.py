"""WP-Y7: TRAFFIC KPI dashboard."""

import logging
from datetime import UTC, datetime
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class KPIDashboard:
    """Aggregates and displays TRAFFIC KPIs (Throughput, Reliability, Availability, Finance, Fatigue, Integrity, Continuity)."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings

    def get_metrics(self) -> dict[str, Any]:
        """Aggregate KPIs from various subsystems."""
        # This would call CostAggregator, LoadClassifier, etc.
        metrics = {
            "throughput": 0,  # Placeholder
            "reliability": 1.0,
            "availability": 1.0,
            "finance": 0.0,  # Cost in USD
            "fatigue": 0.0,  # 0.0 to 1.0
            "integrity": 1.0,
            "continuity": 1.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # WP-5003: Cost awareness
        try:
            from thegent.governance.cost import CostAggregator

            agg = CostAggregator(self.settings.session_dir)
            metrics["finance"] = agg.get_mtd_total()
        except Exception:
            pass

        # WP-4004: Fatigue
        try:
            from thegent.ux.alerts import AlertFatigueController

            afc = AlertFatigueController(self.settings)
            metrics["fatigue"] = afc.get_fatigue_level()
        except Exception:
            pass

        return metrics

    def render_summary(self) -> str:
        """Render a text-based KPI summary."""
        m = self.get_metrics()
        return (
            f"TRAFFIC KPIs at {m['timestamp']}:\n"
            f"- Finance: ${m['finance']:.2f}\n"
            f"- Fatigue: {m['fatigue']:.1%}\n"
            f"- Reliability: {m['reliability']:.1%}\n"
        )
