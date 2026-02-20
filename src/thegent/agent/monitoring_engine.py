"""Monitoring engine for agent crew."""

import logging
from datetime import UTC, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class MonitoringEngine:
    """Monitor agent crew execution."""

    def __init__(self) -> None:
        """Initialize monitoring engine."""
        self.metrics: list[dict[str, Any]] = []

    def record_metric(self, name: str, value: Any, tags: dict[str, Any] | None = None) -> None:
        """Record a metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
        """
        self.metrics.append(
            {
                "name": name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        logger.debug(f"Recorded metric: {name} = {value}")

    def get_metrics(self, name: str | None = None) -> list[dict[str, Any]]:
        """Get metrics.

        Args:
            name: Optional metric name filter

        Returns:
            List of metrics
        """
        if name:
            return [m for m in self.metrics if m["name"] == name]
        return self.metrics

    def get_summary(self) -> dict[str, Any]:
        """Get monitoring summary.

        Returns:
            Summary dictionary
        """
        return {
            "total_metrics": len(self.metrics),
            "metrics_by_name": {
                name: len([m for m in self.metrics if m["name"] == name]) for name in {m["name"] for m in self.metrics}
            },
        }
