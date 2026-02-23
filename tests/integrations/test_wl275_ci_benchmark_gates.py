"""Tests for thegent.integrations.ci_benchmark_gates — CI performance regression detection.

@trace WL-275
"""

from __future__ import annotations

import pytest

from thegent.integrations.ci_benchmark_gates import (
    BenchmarkGate,
    CIBenchmarkGates,
)


class TestBenchmarkGate:
    """Test BenchmarkGate dataclass. @trace WL-275"""

    @pytest.mark.requirement("WL-275")
    def test_create_without_result(self) -> None:
        """Can create BenchmarkGate without actual_ms."""
        gate = BenchmarkGate(name="api_latency", threshold_ms=100.0)

        assert gate.name == "api_latency"
        assert gate.threshold_ms == 100.0
        assert gate.actual_ms is None

    @pytest.mark.requirement("WL-275")
    def test_create_with_result(self) -> None:
        """Can create BenchmarkGate with actual_ms."""
        gate = BenchmarkGate(name="api_latency", threshold_ms=100.0, actual_ms=95.5)

        assert gate.name == "api_latency"
        assert gate.threshold_ms == 100.0
        assert gate.actual_ms == 95.5

    @pytest.mark.requirement("WL-275")
    def test_gate_fields(self) -> None:
        """BenchmarkGate has all required fields."""
        gate = BenchmarkGate(
            name="test_gate",
            threshold_ms=50.0,
            actual_ms=45.0,
        )

        assert hasattr(gate, "name")
        assert hasattr(gate, "threshold_ms")
        assert hasattr(gate, "actual_ms")


class TestCIBenchmarkGates:
    """Test CIBenchmarkGates operations. @trace WL-275"""

    @pytest.mark.requirement("WL-275")
    def test_init(self) -> None:
        """Can initialize CIBenchmarkGates."""
        gates = CIBenchmarkGates()
        assert gates._gates == {}

    @pytest.mark.requirement("WL-275")
    def test_add_gate_single(self) -> None:
        """Can add a single benchmark gate."""
        gates = CIBenchmarkGates()
        gate = gates.add_gate("api_latency", 100.0)

        assert gate.name == "api_latency"
        assert gate.threshold_ms == 100.0
        assert gate.actual_ms is None

    @pytest.mark.requirement("WL-275")
    def test_add_gate_multiple(self) -> None:
        """Can add multiple benchmark gates."""
        gates = CIBenchmarkGates()
        gates.add_gate("latency", 100.0)
        gates.add_gate("throughput", 500.0)
        gates.add_gate("memory", 1024.0)

        evaluate = gates.evaluate()
        assert len(evaluate) == 3

    @pytest.mark.requirement("WL-275")
    def test_add_gate_invalid_threshold(self) -> None:
        """Raises ValueError for invalid threshold."""
        gates = CIBenchmarkGates()

        with pytest.raises(ValueError, match=r"threshold_ms must be >= 1\.0"):
            gates.add_gate("test", 0.5)

    @pytest.mark.requirement("WL-275")
    def test_record_result_success(self) -> None:
        """Can record actual measurement for a gate."""
        gates = CIBenchmarkGates()
        gates.add_gate("latency", 100.0)
        gates.record_result("latency", 95.0)

        evaluate = gates.evaluate()
        assert evaluate[0].actual_ms == 95.0

    @pytest.mark.requirement("WL-275")
    def test_record_result_exact_threshold(self) -> None:
        """Can record result exactly at threshold."""
        gates = CIBenchmarkGates()
        gates.add_gate("latency", 100.0)
        gates.record_result("latency", 100.0)

        evaluate = gates.evaluate()
        assert evaluate[0].actual_ms == 100.0

    @pytest.mark.requirement("WL-275")
    def test_record_result_zero(self) -> None:
        """Can record zero milliseconds."""
        gates = CIBenchmarkGates()
        gates.add_gate("fast_op", 10.0)
        gates.record_result("fast_op", 0.0)

        evaluate = gates.evaluate()
        assert evaluate[0].actual_ms == 0.0

    @pytest.mark.requirement("WL-275")
    def test_record_result_nonexistent_gate(self) -> None:
        """Raises ValueError when recording for non-existent gate."""
        gates = CIBenchmarkGates()

        with pytest.raises(ValueError, match="Benchmark gate not found"):
            gates.record_result("nonexistent", 50.0)

    @pytest.mark.requirement("WL-275")
    def test_record_result_invalid_value(self) -> None:
        """Raises ValueError for negative actual_ms."""
        gates = CIBenchmarkGates()
        gates.add_gate("test", 100.0)

        with pytest.raises(ValueError, match=r"actual_ms must be >= 0\.0"):
            gates.record_result("test", -1.0)

    @pytest.mark.requirement("WL-275")
    def test_evaluate_empty(self) -> None:
        """evaluate() on empty gates returns empty list."""
        gates = CIBenchmarkGates()
        assert gates.evaluate() == []

    @pytest.mark.requirement("WL-275")
    def test_evaluate_all_gates(self) -> None:
        """evaluate() returns all gates including those without results."""
        gates = CIBenchmarkGates()
        gates.add_gate("gate1", 100.0)
        gates.add_gate("gate2", 200.0)
        gates.record_result("gate1", 95.0)

        evaluate = gates.evaluate()
        assert len(evaluate) == 2
        assert evaluate[0].actual_ms == 95.0
        assert evaluate[1].actual_ms is None

    @pytest.mark.requirement("WL-275")
    def test_failed_gates_none_below_threshold(self) -> None:
        """failed_gates() returns empty when all pass."""
        gates = CIBenchmarkGates()
        gates.add_gate("test1", 100.0)
        gates.add_gate("test2", 200.0)
        gates.record_result("test1", 95.0)
        gates.record_result("test2", 150.0)

        failed = gates.failed_gates()
        assert len(failed) == 0

    @pytest.mark.requirement("WL-275")
    def test_failed_gates_exceeds_threshold(self) -> None:
        """failed_gates() returns gates that exceeded threshold."""
        gates = CIBenchmarkGates()
        gates.add_gate("fast", 100.0)
        gates.add_gate("slow", 200.0)
        gates.record_result("fast", 95.0)
        gates.record_result("slow", 250.0)

        failed = gates.failed_gates()
        assert len(failed) == 1
        assert failed[0].name == "slow"

    @pytest.mark.requirement("WL-275")
    def test_failed_gates_no_results(self) -> None:
        """failed_gates() ignores gates without results."""
        gates = CIBenchmarkGates()
        gates.add_gate("gate1", 100.0)
        gates.add_gate("gate2", 200.0)
        gates.record_result("gate1", 150.0)

        failed = gates.failed_gates()
        assert len(failed) == 1
        assert failed[0].name == "gate1"

    @pytest.mark.requirement("WL-275")
    def test_failed_gates_multiple(self) -> None:
        """failed_gates() returns all gates exceeding thresholds."""
        gates = CIBenchmarkGates()
        gates.add_gate("gate1", 100.0)
        gates.add_gate("gate2", 200.0)
        gates.add_gate("gate3", 300.0)
        gates.record_result("gate1", 150.0)
        gates.record_result("gate2", 250.0)
        gates.record_result("gate3", 250.0)

        failed = gates.failed_gates()
        assert len(failed) == 2

        names = {g.name for g in failed}
        assert names == {"gate1", "gate2"}

    @pytest.mark.requirement("WL-275")
    def test_passed_all_gates_pass(self) -> None:
        """passed() returns True when all gates pass."""
        gates = CIBenchmarkGates()
        gates.add_gate("test1", 100.0)
        gates.add_gate("test2", 200.0)
        gates.record_result("test1", 95.0)
        gates.record_result("test2", 150.0)

        assert gates.passed() is True

    @pytest.mark.requirement("WL-275")
    def test_passed_one_gate_fails(self) -> None:
        """passed() returns False when any gate fails."""
        gates = CIBenchmarkGates()
        gates.add_gate("test1", 100.0)
        gates.add_gate("test2", 200.0)
        gates.record_result("test1", 95.0)
        gates.record_result("test2", 250.0)

        assert gates.passed() is False

    @pytest.mark.requirement("WL-275")
    def test_passed_no_results(self) -> None:
        """passed() returns True when no results recorded yet."""
        gates = CIBenchmarkGates()
        gates.add_gate("test1", 100.0)

        assert gates.passed() is True

    @pytest.mark.requirement("WL-275")
    def test_passed_empty(self) -> None:
        """passed() returns True for empty gates."""
        gates = CIBenchmarkGates()
        assert gates.passed() is True

    @pytest.mark.requirement("WL-275")
    def test_add_gate_overwrites(self) -> None:
        """Adding gate with same name overwrites previous."""
        gates = CIBenchmarkGates()
        gates.add_gate("test", 100.0)
        gates.add_gate("test", 200.0)

        evaluate = gates.evaluate()
        assert len(evaluate) == 1
        assert evaluate[0].threshold_ms == 200.0


class TestCIBenchmarkGatesIntegration:
    """Integration tests for CIBenchmarkGates. @trace WL-275"""

    @pytest.mark.requirement("WL-275")
    def test_complete_ci_workflow(self) -> None:
        """Complete CI workflow: add gates -> record results -> evaluate."""
        gates = CIBenchmarkGates()

        # Setup gates
        gates.add_gate("api_latency", 100.0)
        gates.add_gate("db_query", 500.0)
        gates.add_gate("cache_hit", 50.0)

        # Run benchmarks
        gates.record_result("api_latency", 95.0)
        gates.record_result("db_query", 480.0)
        gates.record_result("cache_hit", 45.0)

        # Verify all pass
        assert gates.passed() is True
        assert len(gates.failed_gates()) == 0

    @pytest.mark.requirement("WL-275")
    def test_regression_detection(self) -> None:
        """Detect performance regression."""
        gates = CIBenchmarkGates()

        gates.add_gate("request_latency", 100.0)
        gates.add_gate("response_time", 200.0)

        # First run (baseline)
        gates.record_result("request_latency", 95.0)
        gates.record_result("response_time", 150.0)
        assert gates.passed() is True

        # Simulate regression
        gates.record_result("request_latency", 105.0)
        gates.record_result("response_time", 220.0)

        # Should now fail
        assert gates.passed() is False
        failed = gates.failed_gates()
        assert len(failed) == 2

    @pytest.mark.requirement("WL-275")
    def test_partial_measurement(self) -> None:
        """Handle partial measurement results."""
        gates = CIBenchmarkGates()

        gates.add_gate("fast", 50.0)
        gates.add_gate("slow", 200.0)
        gates.add_gate("unknown", 100.0)

        # Only measure some gates
        gates.record_result("fast", 45.0)
        gates.record_result("slow", 210.0)

        # Check results
        assert gates.passed() is False
        failed = gates.failed_gates()
        assert len(failed) == 1
        assert failed[0].name == "slow"

    @pytest.mark.requirement("WL-275")
    def test_multiple_measurements_same_gate(self) -> None:
        """Recording result multiple times overwrites."""
        gates = CIBenchmarkGates()
        gates.add_gate("test", 100.0)

        gates.record_result("test", 95.0)
        assert gates.passed() is True

        gates.record_result("test", 150.0)
        assert gates.passed() is False

    @pytest.mark.requirement("WL-275")
    def test_floating_point_precision(self) -> None:
        """Handle floating point comparisons correctly."""
        gates = CIBenchmarkGates()

        gates.add_gate("precise", 100.5)
        gates.record_result("precise", 100.49999)

        # Should pass (below threshold)
        assert gates.passed() is True

        gates.record_result("precise", 100.50001)
        # Should fail (above threshold)
        assert gates.passed() is False

    @pytest.mark.requirement("WL-275")
    def test_large_gate_set(self) -> None:
        """Handle many benchmark gates."""
        gates = CIBenchmarkGates()

        # Add 50 gates
        for i in range(50):
            gates.add_gate(f"benchmark_{i}", 100.0 + i)

        # Record results
        for i in range(50):
            gates.record_result(f"benchmark_{i}", 50.0 + i)

        # All should pass
        assert gates.passed() is True
        assert len(gates.failed_gates()) == 0
        assert len(gates.evaluate()) == 50
