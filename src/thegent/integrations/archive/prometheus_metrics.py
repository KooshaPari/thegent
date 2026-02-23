"""Prometheus metrics export.

Implements metrics collection and export in Prometheus text format, enabling
integration with monitoring and observability platforms.

# @trace WL-196
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MetricSample:
    """A single metric sample with name, value, and optional labels."""

    name: str
    value: float
    labels: dict[str, str]


class PrometheusMetricsExporter:
    """Collects and exports metrics in Prometheus text format."""

    def __init__(self) -> None:
        """Initialize the metrics exporter."""
        self._samples: list[MetricSample] = []
        logger.debug("Initialized Prometheus metrics exporter")

    def _normalize_labels(self, labels: dict[str, str] | None) -> dict[str, str]:
        """Return an isolated labels mapping for storage."""
        if labels is None:
            return {}
        return dict(labels)

    @staticmethod
    def _format_sample(sample: MetricSample) -> str:
        """Format one metric sample into Prometheus text format."""
        if sample.labels:
            label_parts = [f'{k}="{v}"' for k, v in sorted(sample.labels.items())]
            label_str = "{" + ",".join(label_parts) + "}"
            return f"{sample.name}{label_str} {sample.value}"
        return f"{sample.name} {sample.value}"

    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a metric sample.

        Args:
            name: Metric name (e.g., "requests_total").
            value: Metric value (numeric).
            labels: Optional dict of label key-value pairs.

        Raises:
            ValueError: If name is empty.
        """
        if not name:
            raise ValueError("metric name cannot be empty")

        label_dict = self._normalize_labels(labels)
        sample = MetricSample(name=name, value=value, labels=label_dict)
        self._samples.append(sample)

        logger.debug(f"Recorded metric: {name}={value} labels={label_dict}")

    def export(self) -> str:
        """Export all metrics in Prometheus text format.

        Returns:
            String in Prometheus text format, with one metric per line.
            Format: metric_name{label1="val1",label2="val2"} 1.0
        """
        lines = [self._format_sample(sample) for sample in self._samples]

        result = "\n".join(lines)
        logger.debug(f"Exported {len(self._samples)} metrics")

        return result

    def get_samples(self, name: str) -> list[MetricSample]:
        """Get all samples for a specific metric name.

        Args:
            name: Metric name to filter by.

        Returns:
            List of MetricSample objects matching the name.
        """
        return [s for s in self._samples if s.name == name]

    def clear(self) -> None:
        """Clear all recorded metrics."""
        self._samples.clear()
        logger.debug("Cleared all metrics")
