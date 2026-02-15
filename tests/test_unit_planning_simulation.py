"""Unit tests for planning simulation module (PERT, resource contention, continuity risk)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from thegent.planning.simulation import (
    ContentionResult,
    ContinuityRiskInput,
    ContinuityRiskResult,
    PERTNode,
    PERTResult,
    ResourceProfile,
    TaskResourceDemand,
    pert_forward_pass,
    score_continuity_risk,
    simulate_resource_contention,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# PERT Forward Pass
# ---------------------------------------------------------------------------


class TestPertForwardPass:
    """Tests for pert_forward_pass calculation."""

    def test_single_node_expected_duration(self) -> None:
        # @trace FR-PLN-001
        """PERT expected duration uses (O + 4M + P) / 6 formula."""
        node = PERTNode(
            task_id="A",
            optimistic_days=1.0,
            most_likely_days=3.0,
            pessimistic_days=5.0,
            predecessors=[],
        )
        results = pert_forward_pass([node])
        assert "A" in results
        # (1 + 4*3 + 5) / 6 = 18 / 6 = 3.0
        assert results["A"].expected_duration == pytest.approx(3.0)

    def test_single_node_variance(self) -> None:
        # @trace FR-PLN-001
        """PERT variance uses ((P - O) / 6)^2 formula."""
        node = PERTNode(
            task_id="A",
            optimistic_days=1.0,
            most_likely_days=3.0,
            pessimistic_days=7.0,
            predecessors=[],
        )
        results = pert_forward_pass([node])
        # ((7 - 1) / 6)^2 = 1.0
        assert results["A"].variance == pytest.approx(1.0)

    def test_multiple_nodes(self) -> None:
        # @trace FR-PLN-001
        """Multiple nodes each produce independent PERT results."""
        nodes = [
            PERTNode("A", 1, 2, 3, []),
            PERTNode("B", 2, 4, 12, ["A"]),
            PERTNode("C", 3, 6, 9, ["A"]),
        ]
        results = pert_forward_pass(nodes)
        assert len(results) == 3
        assert set(results.keys()) == {"A", "B", "C"}

    def test_empty_dag(self) -> None:
        # @trace FR-PLN-001
        """Empty node list returns empty results."""
        results = pert_forward_pass([])
        assert results == {}

    def test_symmetric_estimates_zero_variance(self) -> None:
        # @trace FR-PLN-001
        """When optimistic == pessimistic, variance is zero."""
        node = PERTNode("X", 5.0, 5.0, 5.0, [])
        results = pert_forward_pass([node])
        assert results["X"].variance == pytest.approx(0.0)
        assert results["X"].expected_duration == pytest.approx(5.0)

    def test_skewed_pessimistic(self) -> None:
        # @trace FR-PLN-001
        """Heavy pessimistic skew increases expected duration."""
        node = PERTNode("S", 1.0, 2.0, 20.0, [])
        results = pert_forward_pass([node])
        # (1 + 8 + 20) / 6 = 29/6 ~= 4.833
        assert results["S"].expected_duration == pytest.approx(29.0 / 6.0)
        # ((20 - 1) / 6)^2 = (19/6)^2 ~= 10.028
        assert results["S"].variance == pytest.approx((19.0 / 6.0) ** 2)

    def test_result_fields_populated(self) -> None:
        # @trace FR-PLN-001
        """All PERTResult fields are populated with initial values."""
        node = PERTNode("T", 2.0, 4.0, 6.0, [])
        results = pert_forward_pass([node])
        r = results["T"]
        assert r.task_id == "T"
        assert r.critical_path is False
        assert r.total_float == 0.0
        assert r.confidence_p50 == 0.5
        assert r.confidence_p90 == 0.9

    def test_predecessors_preserved_in_nodes(self) -> None:
        # @trace FR-PLN-001
        """PERTNode predecessors are set correctly (structural check)."""
        a = PERTNode("A", 1, 2, 3, [])
        b = PERTNode("B", 1, 2, 3, ["A"])
        c = PERTNode("C", 1, 2, 3, ["A", "B"])
        assert a.predecessors == []
        assert b.predecessors == ["A"]
        assert c.predecessors == ["A", "B"]

    def test_very_small_durations(self) -> None:
        # @trace FR-PLN-001
        """Near-zero durations produce valid results without division errors."""
        node = PERTNode("tiny", 0.001, 0.002, 0.003, [])
        results = pert_forward_pass([node])
        assert results["tiny"].expected_duration > 0.0
        assert results["tiny"].variance >= 0.0

    def test_large_dag_consistency(self) -> None:
        # @trace FR-PLN-001
        """A larger DAG processes all nodes and returns correct count."""
        nodes = [PERTNode(f"N{i}", 1.0, 2.0, 3.0, []) for i in range(100)]
        results = pert_forward_pass(nodes)
        assert len(results) == 100
        for i in range(100):
            assert results[f"N{i}"].expected_duration == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# PERTNode / PERTResult dataclass tests
# ---------------------------------------------------------------------------


class TestPertDataclasses:
    """Structural tests for PERT dataclasses."""

    def test_pert_node_fields(self) -> None:
        # @trace FR-PLN-001
        """PERTNode stores all required fields."""
        n = PERTNode("id1", 1.0, 2.0, 3.0, ["dep1"])
        assert n.task_id == "id1"
        assert n.optimistic_days == 1.0
        assert n.most_likely_days == 2.0
        assert n.pessimistic_days == 3.0
        assert n.predecessors == ["dep1"]

    def test_pert_result_fields(self) -> None:
        # @trace FR-PLN-001
        """PERTResult stores all analysis fields."""
        r = PERTResult("r1", 3.0, 0.5, True, 1.5, 0.5, 0.9)
        assert r.task_id == "r1"
        assert r.expected_duration == 3.0
        assert r.variance == 0.5
        assert r.critical_path is True
        assert r.total_float == 1.5


# ---------------------------------------------------------------------------
# Resource Contention (D2 stub)
# ---------------------------------------------------------------------------


class TestSimulateResourceContention:
    """Tests for simulate_resource_contention stub."""

    def test_returns_empty_list(self) -> None:
        # @trace FR-PLN-002
        """Stub always returns empty list."""
        result = simulate_resource_contention([], [], {})
        assert result == []

    def test_with_resources_still_empty(self) -> None:
        # @trace FR-PLN-002
        """Even with inputs, stub returns empty (unimplemented)."""
        resources = [ResourceProfile("cpu", 4.0, "cores")]
        result = simulate_resource_contention(
            [{"task_id": "t1"}],
            resources,
            {"t1": {"start": 0, "end": 5}},
        )
        assert result == []


# ---------------------------------------------------------------------------
# Continuity Risk (D3)
# ---------------------------------------------------------------------------


class TestScoreContinuityRisk:
    """Tests for score_continuity_risk."""

    def test_no_open_tasks_zero_risk(self) -> None:
        # @trace FR-PLN-003
        """Empty open_tasks yields zero risk."""
        inp = ContinuityRiskInput(
            open_tasks=[],
            handoff_windows=[],
            snapshot_freshness={},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score == 0.0
        assert result.factors == []
        assert result.high_risk_tasks == []
        assert result.recommendations == []

    def test_fresh_snapshots_no_risk(self) -> None:
        # @trace FR-PLN-003
        """Tasks with recent snapshots (< 24h) incur no risk."""
        now = datetime.now(UTC)
        inp = ContinuityRiskInput(
            open_tasks=[{"id": "t1"}],
            handoff_windows=[],
            snapshot_freshness={"t1": now - timedelta(hours=1)},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score == 0.0
        assert result.high_risk_tasks == []

    def test_stale_snapshot_increases_risk(self) -> None:
        # @trace FR-PLN-003
        """A snapshot older than 24h adds 0.2 risk and flags the task."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=48)
        inp = ContinuityRiskInput(
            open_tasks=[{"id": "t1"}],
            handoff_windows=[],
            snapshot_freshness={"t1": stale},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score == pytest.approx(0.2)
        assert "t1" in result.high_risk_tasks
        assert len(result.factors) == 1
        assert "Stale snapshot" in result.factors[0]

    def test_multiple_stale_snapshots_accumulate(self) -> None:
        # @trace FR-PLN-003
        """Multiple stale tasks accumulate risk up to 1.0."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=72)
        tasks = [{"id": f"t{i}"} for i in range(6)]
        freshness = {f"t{i}": stale for i in range(6)}
        inp = ContinuityRiskInput(
            open_tasks=tasks,
            handoff_windows=[],
            snapshot_freshness=freshness,
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        # 6 * 0.2 = 1.2, capped at 1.0
        assert result.risk_score == pytest.approx(1.0)
        assert len(result.high_risk_tasks) == 6

    def test_risk_capped_at_one(self) -> None:
        # @trace FR-PLN-003
        """Risk score never exceeds 1.0."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=100)
        tasks = [{"id": f"t{i}"} for i in range(10)]
        freshness = {f"t{i}": stale for i in range(10)}
        inp = ContinuityRiskInput(
            open_tasks=tasks,
            handoff_windows=[],
            snapshot_freshness=freshness,
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score <= 1.0

    def test_high_risk_triggers_recommendation(self) -> None:
        # @trace FR-PLN-003
        """Risk > 0.5 triggers 'Refresh snapshots before handoff' recommendation."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=200)
        tasks = [{"id": f"t{i}"} for i in range(4)]
        freshness = {f"t{i}": stale for i in range(4)}
        inp = ContinuityRiskInput(
            open_tasks=tasks,
            handoff_windows=[],
            snapshot_freshness=freshness,
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        # 4 * 0.2 = 0.8 > 0.5
        assert "Refresh snapshots before handoff" in result.recommendations

    def test_low_risk_no_recommendation(self) -> None:
        # @trace FR-PLN-003
        """Risk <= 0.5 does not trigger recommendations."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=48)
        tasks = [{"id": "t1"}, {"id": "t2"}]
        freshness = {"t1": stale, "t2": now - timedelta(hours=1)}
        inp = ContinuityRiskInput(
            open_tasks=tasks,
            handoff_windows=[],
            snapshot_freshness=freshness,
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        # Only t1 is stale: 0.2 <= 0.5, no recommendations
        assert result.recommendations == []

    def test_task_id_fallback_key(self) -> None:
        # @trace FR-PLN-003
        """Tasks using 'task_id' key instead of 'id' are handled."""
        now = datetime.now(UTC)
        stale = now - timedelta(hours=48)
        inp = ContinuityRiskInput(
            open_tasks=[{"task_id": "tx"}],
            handoff_windows=[],
            snapshot_freshness={"tx": stale},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert "tx" in result.high_risk_tasks

    def test_naive_datetime_handled(self) -> None:
        # @trace FR-PLN-003
        """Naive datetimes (no tzinfo) are treated as UTC."""
        # The code does age.replace(tzinfo=UTC) for naive datetimes
        stale_naive = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=48)
        inp = ContinuityRiskInput(
            open_tasks=[{"id": "naive_task"}],
            handoff_windows=[],
            snapshot_freshness={"naive_task": stale_naive},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score == pytest.approx(0.2)
        assert "naive_task" in result.high_risk_tasks

    def test_missing_snapshot_no_risk(self) -> None:
        # @trace FR-PLN-003
        """Tasks without entries in snapshot_freshness incur no risk."""
        inp = ContinuityRiskInput(
            open_tasks=[{"id": "orphan"}],
            handoff_windows=[],
            snapshot_freshness={},
            owner_coverage={},
        )
        result = score_continuity_risk(inp)
        assert result.risk_score == 0.0
        assert result.high_risk_tasks == []


# ---------------------------------------------------------------------------
# Dataclass structural tests for resource & continuity types
# ---------------------------------------------------------------------------


class TestResourceDataclasses:
    """Structural tests for resource and contention dataclasses."""

    def test_resource_profile_defaults(self) -> None:
        # @trace FR-PLN-002
        """ResourceProfile has sensible defaults for unit."""
        rp = ResourceProfile("cpu", 8.0)
        assert rp.unit == "concurrent"

    def test_task_resource_demand_fields(self) -> None:
        # @trace FR-PLN-002
        """TaskResourceDemand stores all required fields."""
        trd = TaskResourceDemand("t1", "cpu", 2.0, 0.0, 5.0)
        assert trd.task_id == "t1"
        assert trd.resource_id == "cpu"
        assert trd.demand == 2.0
        assert trd.start_float == 0.0
        assert trd.duration_float == 5.0

    def test_contention_result_fields(self) -> None:
        # @trace FR-PLN-002
        """ContentionResult stores all analysis fields."""
        cr = ContentionResult("cpu", (0.0, 5.0), 10.0, 8.0, 1.25, ["t1", "t2"])
        assert cr.resource_id == "cpu"
        assert cr.time_window == (0.0, 5.0)
        assert cr.peak_demand == 10.0
        assert cr.contention_ratio == 1.25
        assert cr.affected_tasks == ["t1", "t2"]

    def test_continuity_risk_result_fields(self) -> None:
        # @trace FR-PLN-003
        """ContinuityRiskResult stores all risk analysis fields."""
        crr = ContinuityRiskResult(0.6, ["factor1"], ["t1"], ["do X"])
        assert crr.risk_score == 0.6
        assert crr.factors == ["factor1"]
        assert crr.high_risk_tasks == ["t1"]
        assert crr.recommendations == ["do X"]
