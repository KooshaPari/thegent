"""Cold/Warm Benchmark Split for performance measurement.

# @trace WL-236
Provides benchmark measurement split between cold-start and warm-cache operation modes,
enabling comparison of performance characteristics under different conditions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BenchmarkRun:
    """A single benchmark run measurement."""

    run_id: str
    warm: bool
    duration_ms: float


class ColdWarmBenchmarkSplitter:
    """Separates and analyzes cold and warm benchmark runs."""

    def __init__(self) -> None:
        """Initialize the benchmark splitter."""
        self._runs: dict[str, BenchmarkRun] = {}
        self._all_runs: list[BenchmarkRun] = []

    def record(self, run_id: str, warm: bool, duration_ms: float) -> BenchmarkRun:
        """Record a benchmark run.

        Args:
            run_id: Unique identifier for the run.
            warm: Whether this is a warm run (True) or cold run (False).
            duration_ms: Duration of the run in milliseconds.

        Returns:
            The created BenchmarkRun.
        """
        run = BenchmarkRun(run_id=run_id, warm=warm, duration_ms=duration_ms)
        self._runs[run_id] = run
        self._all_runs.append(run)
        return run

    def cold_runs(self) -> list[BenchmarkRun]:
        """Get all cold-start benchmark runs.

        Returns:
            List of BenchmarkRuns where warm=False.
        """
        return [run for run in self._all_runs if not run.warm]

    def warm_runs(self) -> list[BenchmarkRun]:
        """Get all warm-cache benchmark runs.

        Returns:
            List of BenchmarkRuns where warm=True.
        """
        return [run for run in self._all_runs if run.warm]

    def average_cold(self) -> float:
        """Calculate average duration for cold runs.

        Returns:
            Average duration in milliseconds, or 0.0 if no cold runs exist.
        """
        cold = self.cold_runs()
        if not cold:
            return 0.0
        return sum(run.duration_ms for run in cold) / len(cold)

    def average_warm(self) -> float:
        """Calculate average duration for warm runs.

        Returns:
            Average duration in milliseconds, or 0.0 if no warm runs exist.
        """
        warm = self.warm_runs()
        if not warm:
            return 0.0
        return sum(run.duration_ms for run in warm) / len(warm)
