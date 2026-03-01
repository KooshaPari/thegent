"""Metrics collection system."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Metrics collection."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.metrics: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        """Record a metric.

        Args:
            metric_name: Metric name
            value: Metric value
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)

    def get_stats(self, metric_name: str) -> dict[str, float | int | None]:
        """Get statistics for metric.

        Args:
            metric_name: Metric name

        Returns:
            Statistics dictionary
        """
        values = self.metrics.get(metric_name, [])
        if not values:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
            }

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }

    def emit_slo_stub(
        self,
        metric_name: str,
        value: float,
        *,
        threshold: float | None = None,
        lane: str = "fast-lane",
    ) -> dict[str, Any]:
        """Build an SLO metric payload without external transport.

        WL-135 stub: this method intentionally only structures data so that
        downstream dashboard/report wiring can be added incrementally.
        """
        status = self._compute_threshold_status(value=value, threshold=threshold)
        payload = self._build_slo_payload(
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            status=status,
            lane=lane,
        )
        logger.info("slo_stub_emit metric=%s value=%s status=%s", metric_name, value, status)
        return payload

    @staticmethod
    def _compute_threshold_status(*, value: float, threshold: float | None) -> str:
        """Compute threshold status for a metric value."""
        if threshold is None:
            return "unknown"
        return "pass" if value <= threshold else "fail"

    @staticmethod
    def _build_slo_payload(
        *,
        metric_name: str,
        value: float,
        threshold: float | None,
        status: str,
        lane: str,
    ) -> dict[str, Any]:
        """Build the SLO payload envelope."""
        return {
            "emitter": "wl135-slo-stub",
            "metric_name": metric_name,
            "value": value,
            "threshold": threshold,
            "status": status,
            "lane": lane,
            "timestamp_unix": time.time(),
        }
