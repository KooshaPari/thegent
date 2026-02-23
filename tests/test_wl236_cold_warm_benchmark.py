"""Tests for WL-236: Cold/Warm Benchmark Split.

Tests cover:
- BenchmarkRun dataclass creation
- ColdWarmBenchmarkSplitter measurement recording
- Separation of cold and warm runs
- Average calculation for both run types
"""

from __future__ import annotations

import pytest

from thegent.integrations.cold_warm_benchmark import (
    BenchmarkRun,
    ColdWarmBenchmarkSplitter,
)


@pytest.mark.requirement("WL-236")
class TestBenchmarkRun:
    """Tests for the BenchmarkRun dataclass."""

    def test_benchmark_run_creation_cold(self) -> None:
        """Test creating a cold BenchmarkRun."""
        run = BenchmarkRun(run_id="run-1", warm=False, duration_ms=150.5)
        assert run.run_id == "run-1"
        assert run.warm is False
        assert run.duration_ms == 150.5

    def test_benchmark_run_creation_warm(self) -> None:
        """Test creating a warm BenchmarkRun."""
        run = BenchmarkRun(run_id="run-2", warm=True, duration_ms=50.2)
        assert run.run_id == "run-2"
        assert run.warm is True
        assert run.duration_ms == 50.2

    def test_benchmark_run_attributes(self) -> None:
        """Test all BenchmarkRun attributes are accessible."""
        run = BenchmarkRun(run_id="test", warm=True, duration_ms=100.0)
        assert hasattr(run, "run_id")
        assert hasattr(run, "warm")
        assert hasattr(run, "duration_ms")


@pytest.mark.requirement("WL-236")
class TestColdWarmBenchmarkSplitter:
    """Tests for the ColdWarmBenchmarkSplitter class."""

    def test_create_empty_splitter(self) -> None:
        """Test creating an empty splitter."""
        splitter = ColdWarmBenchmarkSplitter()
        assert splitter.cold_runs() == []
        assert splitter.warm_runs() == []

    def test_record_single_cold_run(self) -> None:
        """Test recording a single cold run."""
        splitter = ColdWarmBenchmarkSplitter()
        run = splitter.record("cold-1", warm=False, duration_ms=200.0)
        assert run.run_id == "cold-1"
        assert run.warm is False
        assert len(splitter.cold_runs()) == 1

    def test_record_single_warm_run(self) -> None:
        """Test recording a single warm run."""
        splitter = ColdWarmBenchmarkSplitter()
        run = splitter.record("warm-1", warm=True, duration_ms=50.0)
        assert run.run_id == "warm-1"
        assert run.warm is True
        assert len(splitter.warm_runs()) == 1

    def test_record_mixed_runs(self) -> None:
        """Test recording both cold and warm runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=200.0)
        splitter.record("warm-1", warm=True, duration_ms=50.0)
        splitter.record("cold-2", warm=False, duration_ms=180.0)
        splitter.record("warm-2", warm=True, duration_ms=60.0)

        assert len(splitter.cold_runs()) == 2
        assert len(splitter.warm_runs()) == 2

    def test_cold_runs_separation(self) -> None:
        """Test that cold_runs returns only cold runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=100.0)
        splitter.record("warm-1", warm=True, duration_ms=50.0)
        splitter.record("cold-2", warm=False, duration_ms=120.0)

        cold = splitter.cold_runs()
        assert len(cold) == 2
        assert all(not run.warm for run in cold)
        assert {run.run_id for run in cold} == {"cold-1", "cold-2"}

    def test_warm_runs_separation(self) -> None:
        """Test that warm_runs returns only warm runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=100.0)
        splitter.record("warm-1", warm=True, duration_ms=50.0)
        splitter.record("warm-2", warm=True, duration_ms=60.0)

        warm = splitter.warm_runs()
        assert len(warm) == 2
        assert all(run.warm for run in warm)
        assert {run.run_id for run in warm} == {"warm-1", "warm-2"}

    def test_average_cold_single_run(self) -> None:
        """Test average_cold with a single cold run."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=150.0)
        assert splitter.average_cold() == 150.0

    def test_average_cold_multiple_runs(self) -> None:
        """Test average_cold with multiple cold runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=100.0)
        splitter.record("cold-2", warm=False, duration_ms=200.0)
        splitter.record("cold-3", warm=False, duration_ms=300.0)
        assert splitter.average_cold() == 200.0

    def test_average_cold_no_runs(self) -> None:
        """Test average_cold with no cold runs returns 0.0."""
        splitter = ColdWarmBenchmarkSplitter()
        assert splitter.average_cold() == 0.0

    def test_average_cold_ignores_warm_runs(self) -> None:
        """Test that average_cold ignores warm runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=100.0)
        splitter.record("warm-1", warm=True, duration_ms=10.0)  # Should not affect
        splitter.record("cold-2", warm=False, duration_ms=200.0)
        assert splitter.average_cold() == 150.0

    def test_average_warm_single_run(self) -> None:
        """Test average_warm with a single warm run."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("warm-1", warm=True, duration_ms=50.0)
        assert splitter.average_warm() == 50.0

    def test_average_warm_multiple_runs(self) -> None:
        """Test average_warm with multiple warm runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("warm-1", warm=True, duration_ms=40.0)
        splitter.record("warm-2", warm=True, duration_ms=60.0)
        splitter.record("warm-3", warm=True, duration_ms=50.0)
        assert splitter.average_warm() == 50.0

    def test_average_warm_no_runs(self) -> None:
        """Test average_warm with no warm runs returns 0.0."""
        splitter = ColdWarmBenchmarkSplitter()
        assert splitter.average_warm() == 0.0

    def test_average_warm_ignores_cold_runs(self) -> None:
        """Test that average_warm ignores cold runs."""
        splitter = ColdWarmBenchmarkSplitter()
        splitter.record("cold-1", warm=False, duration_ms=1000.0)  # Should not affect
        splitter.record("warm-1", warm=True, duration_ms=40.0)
        splitter.record("warm-2", warm=True, duration_ms=60.0)
        assert splitter.average_warm() == 50.0

    def test_full_workflow(self) -> None:
        """Test a complete workflow with mixed runs and averaging."""
        splitter = ColdWarmBenchmarkSplitter()
        # Record cold runs
        splitter.record("cold-1", warm=False, duration_ms=250.0)
        splitter.record("cold-2", warm=False, duration_ms=350.0)
        # Record warm runs
        splitter.record("warm-1", warm=True, duration_ms=75.0)
        splitter.record("warm-2", warm=True, duration_ms=125.0)

        assert len(splitter.cold_runs()) == 2
        assert len(splitter.warm_runs()) == 2
        assert splitter.average_cold() == 300.0
        assert splitter.average_warm() == 100.0
