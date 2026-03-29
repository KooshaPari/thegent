"""Tests for WL-173 Cycle Metrics Emission.

# @trace WL-173
"""

from __future__ import annotations

import pytest

from thegent.integrations.cycle_metrics import CycleMetric, CycleMetricsEmitter


@pytest.mark.requirement("WL-173")
class TestCycleMetric:
    """Tests for CycleMetric dataclass."""

    def test_cycle_metric_creation(self) -> None:
        """CycleMetric can be created with required fields."""
        metric = CycleMetric(cycle_id="cycle-1", metric_name="latency", value=42.5)
        assert metric.cycle_id == "cycle-1"
        assert metric.metric_name == "latency"
        assert metric.value == 42.5

    def test_cycle_metric_with_zero_value(self) -> None:
        """CycleMetric can have zero value."""
        metric = CycleMetric(cycle_id="cycle-1", metric_name="count", value=0.0)
        assert metric.value == 0.0

    def test_cycle_metric_with_negative_value(self) -> None:
        """CycleMetric can have negative value."""
        metric = CycleMetric(cycle_id="cycle-1", metric_name="delta", value=-10.5)
        assert metric.value == -10.5


@pytest.mark.requirement("WL-173")
class TestCycleMetricsEmitter:
    """Tests for CycleMetricsEmitter class."""

    def test_emit_single_metric(self) -> None:
        """emit() stores a metric and returns it."""
        emitter = CycleMetricsEmitter()
        metric = emitter.emit("cycle-1", "latency", 42.5)

        assert isinstance(metric, CycleMetric)
        assert metric.cycle_id == "cycle-1"
        assert metric.metric_name == "latency"
        assert metric.value == 42.5

    def test_emit_multiple_metrics(self) -> None:
        """emit() can store multiple metrics."""
        emitter = CycleMetricsEmitter()
        m1 = emitter.emit("cycle-1", "latency", 10.0)
        m2 = emitter.emit("cycle-1", "throughput", 100.0)
        m3 = emitter.emit("cycle-2", "latency", 20.0)

        assert m1.value == 10.0
        assert m2.value == 100.0
        assert m3.value == 20.0

    def test_get_metrics_empty(self) -> None:
        """get_metrics() returns empty list for unknown cycle."""
        emitter = CycleMetricsEmitter()
        metrics = emitter.get_metrics("unknown-cycle")
        assert metrics == []

    def test_get_metrics_single_cycle(self) -> None:
        """get_metrics() returns all metrics for a specific cycle."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "latency", 10.0)
        emitter.emit("cycle-1", "throughput", 100.0)
        emitter.emit("cycle-2", "latency", 20.0)

        metrics = emitter.get_metrics("cycle-1")
        assert len(metrics) == 2
        assert all(m.cycle_id == "cycle-1" for m in metrics)

    def test_get_metrics_multiple_cycles(self) -> None:
        """get_metrics() filters by cycle correctly."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "metric", 1.0)
        emitter.emit("cycle-1", "metric", 2.0)
        emitter.emit("cycle-2", "metric", 10.0)

        c1_metrics = emitter.get_metrics("cycle-1")
        c2_metrics = emitter.get_metrics("cycle-2")

        assert len(c1_metrics) == 2
        assert len(c2_metrics) == 1
        assert c2_metrics[0].value == 10.0

    def test_aggregate_single_metric(self) -> None:
        """aggregate() sums values for a metric in a cycle."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "count", 10.0)
        emitter.emit("cycle-1", "count", 20.0)
        emitter.emit("cycle-1", "count", 30.0)

        total = emitter.aggregate("cycle-1", "count")
        assert total == 60.0

    def test_aggregate_different_metrics(self) -> None:
        """aggregate() sums only for the specified metric."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "count", 10.0)
        emitter.emit("cycle-1", "latency", 100.0)
        emitter.emit("cycle-1", "count", 20.0)

        count_total = emitter.aggregate("cycle-1", "count")
        latency_total = emitter.aggregate("cycle-1", "latency")

        assert count_total == 30.0
        assert latency_total == 100.0

    def test_aggregate_different_cycles(self) -> None:
        """aggregate() sums only for the specified cycle."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "metric", 10.0)
        emitter.emit("cycle-1", "metric", 20.0)
        emitter.emit("cycle-2", "metric", 100.0)

        c1_total = emitter.aggregate("cycle-1", "metric")
        c2_total = emitter.aggregate("cycle-2", "metric")

        assert c1_total == 30.0
        assert c2_total == 100.0

    def test_aggregate_unknown_cycle(self) -> None:
        """aggregate() returns 0.0 for unknown cycle."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "metric", 10.0)

        total = emitter.aggregate("unknown-cycle", "metric")
        assert total == 0.0

    def test_aggregate_unknown_metric(self) -> None:
        """aggregate() returns 0.0 for unknown metric in known cycle."""
        emitter = CycleMetricsEmitter()
        emitter.emit("cycle-1", "count", 10.0)

        total = emitter.aggregate("cycle-1", "unknown-metric")
        assert total == 0.0
