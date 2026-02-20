"""Metrics collection system."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Metrics collection."""

    def __init__(self):
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

    def get_stats(self, metric_name: str) -> dict[str, float]:
        """Get statistics for metric.

        Args:
            metric_name: Metric name

        Returns:
            Statistics dictionary
        """
        values = self.metrics.get(metric_name, [])
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }
