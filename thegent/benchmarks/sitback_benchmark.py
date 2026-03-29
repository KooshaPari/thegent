"""Sitback/monitoring benchmarks.

Measures the MetricsCollector hot paths:
- record(): append a value to an in-memory list
- get_stats(): compute min/max/avg over a list of values

# @trace WL-078
# @trace FR-OPT-003
"""

from __future__ import annotations

import pytest

from thegent.metrics.collector import MetricsCollector


@pytest.mark.requirement("FR-OPT-003")
def bench_metrics_record(benchmark):
    """Benchmark: MetricsCollector.record() for a single metric value. # @trace FR-OPT-003"""
    collector = MetricsCollector()

    def _record():
        collector.record("latency_ms", 42.0)

    benchmark(_record)


@pytest.mark.requirement("FR-OPT-003")
def bench_metrics_get_stats_100(benchmark):
    """Benchmark: MetricsCollector.get_stats() over 100 pre-recorded values. # @trace FR-OPT-003"""
    collector = MetricsCollector()
    for i in range(100):
        collector.record("latency_ms", float(i))

    benchmark(collector.get_stats, "latency_ms")


@pytest.mark.requirement("FR-OPT-003")
def bench_metrics_get_stats_1000(benchmark):
    """Benchmark: MetricsCollector.get_stats() over 1000 pre-recorded values. # @trace FR-OPT-003"""
    collector = MetricsCollector()
    for i in range(1000):
        collector.record("latency_ms", float(i))

    benchmark(collector.get_stats, "latency_ms")
