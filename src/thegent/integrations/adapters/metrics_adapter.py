"""Metrics and reporting adapter for workstream autosync.

Handles Prometheus metrics export, cycle metrics, and change digest.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from thegent.observability.prometheus import get_metrics_collector


class MetricsAdapter:
    """Adapter for metrics and reporting operations."""
    
    def __init__(self, config: Any):
        self.config = config
        self._metrics = get_metrics_collector()
        self._cycle_metrics_path = config.cycle_metrics_path or Path("docs/reference/workstream_autosync_cycle_metrics.jsonl")
        self._change_digest_path = config.change_digest_path or Path("artifacts/workstream_autosync_change_digest.jsonl")
        self._prometheus_export_path = config.autosync_prometheus_export_path or Path("docs/reference/workstream_autosync_metrics.prom")
    
    def flush_prometheus_metrics(self) -> None:
        """Export Prometheus metrics to file."""
        try:
            metrics_output = self._metrics.export()
            self._prometheus_export_path.parent.mkdir(parents=True, exist_ok=True)
            self._prometheus_export_path.write_text(metrics_output)
        except Exception:
            pass  # Non-critical
    
    def record_connector_latency(self, connector: str, duration_seconds: float) -> None:
        """Record connector latency metric."""
        # Implementation would update actual metrics
        pass
    
    def append_cycle_metrics(self, cycle_data: dict[str, Any]) -> None:
        """Append cycle metrics to JSONL file."""
        try:
            self._cycle_metrics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cycle_metrics_path, "a") as f:
                f.write(json.dumps(cycle_data) + "\n")
        except Exception:
            pass
    
    def get_change_digest_path(self) -> Path:
        return self._change_digest_path
    
    def refresh_change_digest(self, current_digest: dict[str, Any]) -> dict[str, Any]:
        """Refresh hourly change digest."""
        now = datetime.now(timezone.utc)
        hour_key = now.strftime("%Y-%m-%dT%H")
        
        if "hours" not in current_digest:
            current_digest["hours"] = {}
        
        if hour_key not in current_digest["hours"]:
            current_digest["hours"][hour_key] = {"changes": 0, "syncs": 0}
        
        return current_digest


__all__ = ["MetricsAdapter"]
