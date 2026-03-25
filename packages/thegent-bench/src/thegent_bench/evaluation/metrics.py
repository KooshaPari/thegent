"""
Metrics Collector

Collects and aggregates performance metrics.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from collections import defaultdict
import time
import json


@dataclass
class Metric:
    """A single metric measurement."""

    name: str
    value: float
    timestamp: float
    tags: dict = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self):
        self._metrics: dict[str, list[Metric]] = defaultdict(list)
        self._start_time = time.time()

    def record(self, name: str, value: float, tags: dict | None = None) -> None:
        """Record a metric."""
        metric = Metric(name=name, value=value, timestamp=time.time(), tags=tags or {})
        self._metrics[name].append(metric)

    def timing(self, name: str, duration: float, tags: dict | None = None) -> None:
        """Record a timing metric."""
        self.record(name, duration, tags)

    def increment(self, name: str, value: float = 1.0, tags: dict | None = None) -> None:
        """Increment a counter metric."""
        current = self._metrics[name][-1].value if self._metrics[name] else 0
        self.record(name, current + value, tags)

    def gauge(self, name: str, value: float, tags: dict | None = None) -> None:
        """Record a gauge metric (current value)."""
        self.record(name, value, tags)

    def histogram(self, name: str, value: float, tags: dict | None = None) -> None:
        """Record a histogram metric."""
        self.record(name, value, tags)

    def stats(self, name: str) -> dict:
        """Get statistics for a metric."""
        metrics = self._metrics.get(name, [])
        if not metrics:
            return {}

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "last": values[-1],
        }

    def percentile(self, name: str, p: float) -> Optional[float]:
        """Get percentile for a metric."""
        metrics = self._metrics.get(name, [])
        if not metrics:
            return None

        values = sorted([m.value for m in metrics])
        index = int(len(values) * p / 100)
        return values[min(index, len(values) - 1)]

    def summary(self) -> dict:
        """Get summary of all metrics."""
        return {"uptime": time.time() - self._start_time, "metrics": {name: self.stats(name) for name in self._metrics}}

    def export(self, format: str = "json") -> str:
        """Export metrics."""
        data = self.summary()
        if format == "json":
            return json.dumps(data, indent=2)
        return str(data)

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()


class Timer:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, name: str, tags: dict | None = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start = None
        self.duration = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.duration = time.time() - self.start
        self.collector.timing(self.name, self.duration, self.tags)
