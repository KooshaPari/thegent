"""WP-Y7: TRAFFIC KPI dashboard."""

import orjson as json
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from phenotype_thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class KPIDashboard:
    """Aggregates and displays TRAFFIC KPIs (Throughput, Reliability, Availability, Finance, Fatigue, Integrity, Continuity)."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings

    def _iter_run_registry_rows(self) -> Iterable[dict[str, Any]]:
        run_registry = Path(self.settings.session_dir) / "run_registry.jsonl"
        if not run_registry.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in run_registry.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except Exception:
                continue
            if isinstance(record, dict):
                rows.append(record)
        return rows

    @staticmethod
    def _safe_ratio(num: int, den: int) -> float:
        if den <= 0:
            return 1.0
        return max(0.0, min(1.0, num / den))

    def _compute_runtime_kpis(self, now: datetime) -> dict[str, float]:
        started = 0
        ended = 0
        completed = 0

        for row in self._iter_run_registry_rows():
            ts_raw = row.get("ts") or row.get("timestamp")
            event = row.get("event")
            if not isinstance(ts_raw, str) or not isinstance(event, str):
                continue
            try:
                ts = datetime.fromisoformat(ts_raw)
            except ValueError:
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            if (now - ts).total_seconds() > 3600:
                continue

            if event == "start":
                started += 1
            if event == "end":
                ended += 1
                if row.get("status") == "completed":
                    completed += 1

        throughput = float(completed)
        reliability = self._safe_ratio(completed, ended)
        availability = self._safe_ratio(ended, started) if started > 0 else 1.0
        return {
            "throughput": max(0.0, throughput),
            "reliability": reliability,
            "availability": availability,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Aggregate KPIs from various subsystems."""
        now = datetime.now(UTC)
        runtime = self._compute_runtime_kpis(now)
        metrics = {
            "throughput": runtime["throughput"],
            "reliability": runtime["reliability"],
            "availability": runtime["availability"],
            "finance": 0.0,  # Cost in USD
            "fatigue": 0.0,  # 0.0 to 1.0
            "integrity": 1.0,
            "continuity": 1.0,
            "timestamp": now.isoformat(),
        }

        # WP-5003: Cost awareness
        try:
            from phenotype_thegent_routing.cost.aggregator import CostAggregator

            agg = CostAggregator(self.settings.session_dir)
            metrics["finance"] = agg.get_mtd_total()
        except Exception:
            pass

        # WP-4004: Fatigue
        try:
            from phenotype_thegent_cli.ux.alerts import AlertFatigueController

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
