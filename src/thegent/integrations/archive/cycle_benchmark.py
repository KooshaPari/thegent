"""Cycle performance benchmark harness.

# @trace WL-215
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, UTC


@dataclass
class CycleBenchmark:
    """Represents a single cycle benchmark measurement."""

    cycle_id: str
    start_time: datetime
    end_time: datetime | None = None
    item_count: int = 0


class CycleBenchmarkHarness:
    """Harness for benchmarking cycle performance."""

    def __init__(self) -> None:
        """Initialize the benchmark harness."""
        self._benchmarks: dict[str, CycleBenchmark] = {}

    def start_cycle(self, cycle_id: str) -> CycleBenchmark:
        """Start a new cycle benchmark.

        Args:
            cycle_id: Unique identifier for this cycle.

        Returns:
            The created CycleBenchmark.
        """
        benchmark = CycleBenchmark(
            cycle_id=cycle_id,
            start_time=datetime.now(UTC),
        )
        self._benchmarks[cycle_id] = benchmark
        return benchmark

    def end_cycle(self, cycle_id: str, item_count: int) -> CycleBenchmark:
        """End a cycle benchmark.

        Args:
            cycle_id: Unique identifier for the cycle.
            item_count: Number of items processed in this cycle.

        Returns:
            The updated CycleBenchmark.

        Raises:
            KeyError: If the cycle was not started.
        """
        benchmark = self._benchmarks[cycle_id]
        benchmark.end_time = datetime.now(UTC)
        benchmark.item_count = item_count
        return benchmark

    def get_duration_seconds(self, cycle_id: str) -> float:
        """Get the duration of a cycle in seconds.

        Args:
            cycle_id: Unique identifier for the cycle.

        Returns:
            Duration in seconds. Returns 0 if cycle has not ended.

        Raises:
            KeyError: If the cycle was not started.
        """
        benchmark = self._benchmarks[cycle_id]
        if benchmark.end_time is None:
            return 0.0
        delta = benchmark.end_time - benchmark.start_time
        return delta.total_seconds()

    def all_benchmarks(self) -> list[CycleBenchmark]:
        """Get all recorded benchmarks.

        Returns:
            List of all CycleBenchmark records in insertion order.
        """
        return list(self._benchmarks.values())
