# libs/shared/metrics/__init__.py
# Phenotype Shared Metrics Library
# Version: 0.1.0

"""
Shared metrics library for the Phenotype ecosystem.

Provides standardized metrics collection interfaces and adapters for:
- Counter metrics (incrementing values)
- Gauge metrics (point-in-time values)
- Histogram metrics (value distributions)
- Summary metrics (percentile distributions)

Architecture:
    Ports (interfaces) → Domain (logic) → Adapters (implementations)

Design Principles:
    - SOLID: Single responsibility via dedicated metric types
    - DRY: Shared abstractions in shared library
    - KISS: Simple metric interface
"""

from typing import Protocol, Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# =============================================================================
# Domain Layer - Value Objects
# =============================================================================

class MetricType(Enum):
    """Types of metrics supported."""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Statistical distribution
    SUMMARY = "summary"       # Quantile estimates


@dataclass(frozen=True)
class MetricLabel:
    """Immutable label for metric categorization."""
    name: str
    value: str

    def __post_init__(self):
        if not self.name or not self.value:
            raise ValueError("Label name and value must be non-empty")


@dataclass
class MetricPoint:
    """Single metric observation."""
    value: float
    timestamp: datetime
    labels: tuple[MetricLabel, ...]

    def __post_init__(self):
        self.labels = tuple(self.labels) if self.labels else ()


# =============================================================================
# Ports Layer - Interfaces
# =============================================================================

class MetricsRecorder(Protocol):
    """Port for recording metrics (adapter interface)."""

    def record_counter(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        """Record a counter metric."""
        ...

    def record_gauge(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        """Record a gauge metric."""
        ...

    def record_histogram(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        """Record a histogram metric."""
        ...


class MetricsExporter(Protocol):
    """Port for exporting metrics to external systems."""

    def export(self, metrics: Dict[str, List[MetricPoint]]) -> None:
        """Export collected metrics."""
        ...


class MetricsProvider(Protocol):
    """Port for obtaining metrics instances."""
    pass


# =============================================================================
# Domain Layer - Services
# =============================================================================

class MetricsCollector:
    """
    Domain service for collecting and managing metrics.

    Single Responsibility: Manages metric collection lifecycle
    """

    def __init__(self, recorder: MetricsRecorder):
        self._recorder = recorder
        self._metrics: Dict[str, List[MetricPoint]] = {}

    def record(self, metric_type: MetricType, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        """Record a metric observation."""
        method_map = {
            MetricType.COUNTER: self._recorder.record_counter,
            MetricType.GAUGE: self._recorder.record_gauge,
            MetricType.HISTOGRAM: self._recorder.record_histogram,
        }
        method_map.get(metric_type, self._recorder.record_counter)(name, value, labels)

        # Store locally
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(MetricPoint(value, datetime.now(), labels))

    def get_metrics(self) -> Dict[str, List[MetricPoint]]:
        """Get all collected metrics."""
        return self._metrics.copy()


# =============================================================================
# Adapters Layer - Implementations
# =============================================================================

class InMemoryMetricsRecorder:
    """Adapter: In-memory metrics recording (testing/dev)."""

    def __init__(self):
        self._data: Dict[str, List[MetricPoint]] = {}

    def record_counter(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        self._data.setdefault(name, []).append(MetricPoint(value, datetime.now(), labels))

    def record_gauge(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        self._data.setdefault(name, []).append(MetricPoint(value, datetime.now(), labels))

    def record_histogram(self, name: str, value: float, labels: tuple[MetricLabel, ...]) -> None:
        self._data.setdefault(name, []).append(MetricPoint(value, datetime.now(), labels))

    def get_data(self) -> Dict[str, List[MetricPoint]]:
        return self._data.copy()


class PrometheusMetricsAdapter:
    """Adapter: Prometheus-format metrics export."""

    def __init__(self, namespace: str = "phenotype"):
        self._namespace = namespace

    def export(self, metrics: Dict[str, List[MetricPoint]]) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        for name, points in metrics.items():
            full_name = f"{self._namespace}_{name}"
            for point in points:
                label_str = ",".join(f'{l.name}="{l.value}"' for l in point.labels)
                if label_str:
                    lines.append(f"{full_name}{{{label_str}}} {point.value} {int(point.timestamp.timestamp())}")
                else:
                    lines.append(f"{full_name} {point.value} {int(point.timestamp.timestamp())}")
        return "\n".join(lines) + "\n"


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Domain
    "MetricType",
    "MetricLabel",
    "MetricPoint",
    "MetricsCollector",
    # Ports
    "MetricsRecorder",
    "MetricsExporter",
    "MetricsProvider",
    # Adapters
    "InMemoryMetricsRecorder",
    "PrometheusMetricsAdapter",
]
