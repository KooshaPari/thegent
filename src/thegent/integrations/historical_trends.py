"""Historical trend reports for drift, error, and latency metrics.

Tracks metric values over time and provides trend analysis for long-horizon
reporting on drift, errors, and latency.

# @trace WL-257
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class TrendDataPoint:
    """A single data point in a metric trend.

    Attributes:
        timestamp: When the data point was recorded.
        metric: Name of the metric.
        value: Numeric value of the metric.
    """

    timestamp: datetime
    metric: str
    value: float


class HistoricalTrendReport:
    """Tracks and reports on historical trends of metrics.

    Maintains time-series data and provides trend analysis for metrics
    like drift, errors, and latency.
    """

    def __init__(self) -> None:
        """Initialize the trend report tracker."""
        self._data: dict[str, list[TrendDataPoint]] = {}
        logger.debug("HistoricalTrendReport initialized")

    def record(self, metric: str, value: float) -> TrendDataPoint:
        """Record a new metric value.

        Args:
            metric: Name of the metric.
            value: Numeric value to record.

        Returns:
            TrendDataPoint for the recorded value.
        """
        point = TrendDataPoint(timestamp=datetime.now(timezone.utc), metric=metric, value=value)
        if metric not in self._data:
            self._data[metric] = []
        self._data[metric].append(point)
        logger.debug(f"Recorded metric {metric}={value}")
        return point

    def get_series(self, metric: str) -> list[TrendDataPoint]:
        """Get all data points for a metric.

        Args:
            metric: Name of the metric.

        Returns:
            List of TrendDataPoint objects for the metric, or empty list if not found.
        """
        return self._data.get(metric, [])

    def average(self, metric: str) -> float:
        """Calculate average value for a metric.

        Args:
            metric: Name of the metric.

        Returns:
            Average value, or 0.0 if no data exists.
        """
        points = self._data.get(metric, [])
        if not points:
            return 0.0
        return sum(p.value for p in points) / len(points)

    def trend(self, metric: str) -> str:
        """Determine trend direction based on first vs last value.

        Args:
            metric: Name of the metric.

        Returns:
            "up" if increasing, "down" if decreasing, "stable" if no data or no change.
        """
        points = self._data.get(metric, [])
        if len(points) < 2:
            return "stable"

        first_value = points[0].value
        last_value = points[-1].value

        if last_value > first_value:
            return "up"
        if last_value < first_value:
            return "down"
        return "stable"
