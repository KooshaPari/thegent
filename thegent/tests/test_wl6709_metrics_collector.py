from __future__ import annotations

from thegent.metrics.collector import MetricsCollector


def test_get_stats_empty_metric_returns_stable_schema() -> None:
    stats = MetricsCollector().get_stats("missing")
    assert stats == {"count": 0, "min": None, "max": None, "avg": None}


def test_get_stats_single_metric_value() -> None:
    collector = MetricsCollector()
    collector.record("latency_ms", 42.0)

    stats = collector.get_stats("latency_ms")

    assert stats == {"count": 1, "min": 42.0, "max": 42.0, "avg": 42.0}


def test_get_stats_multiple_metric_values() -> None:
    collector = MetricsCollector()
    collector.record("latency_ms", 10.0)
    collector.record("latency_ms", 20.0)
    collector.record("latency_ms", 30.0)

    stats = collector.get_stats("latency_ms")

    assert stats == {"count": 3, "min": 10.0, "max": 30.0, "avg": 20.0}
