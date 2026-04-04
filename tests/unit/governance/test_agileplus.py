"""Tests for governance/agileplus.py - AgilePlus core loop orchestrator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.governance.agileplus import (
    AgilePlusLoop,
    CycleResult,
    CycleState,
)


class TestCycleState:
    """Tests for CycleState enum."""

    def test_all_states_exist(self):
        assert CycleState.IDLE.value == "idle"
        assert CycleState.SCANNING.value == "scanning"
        assert CycleState.ANALYZING.value == "analyzing"
        assert CycleState.PLANNING.value == "planning"
        assert CycleState.DEPLOYING.value == "deploying"
        assert CycleState.VERIFYING.value == "verifying"
        assert CycleState.COMMITTING.value == "committing"
        assert CycleState.ERROR.value == "error"

    def test_state_from_value(self):
        assert CycleState("idle") == CycleState.IDLE


class TestCycleResult:
    """Tests for CycleResult Pydantic model."""

    def test_default_values(self):
        result = CycleResult(cycle_id="test-1", state=CycleState.IDLE)
        assert result.cycle_id == "test-1"
        assert result.health_score == 0.0
        assert result.health_band == ""
        assert result.findings_count == 0
        assert result.tasks_planned == 0
        assert result.tasks_executed == 0
        assert result.tasks_verified == 0
        assert result.error == ""

    def test_with_values(self):
        result = CycleResult(
            cycle_id="test-2",
            state=CycleState.COMPLETING,
            health_score=95.5,
            health_band="green",
            findings_count=10,
            tasks_planned=5,
            tasks_executed=5,
            tasks_verified=4,
        )
        assert result.health_score == 95.5
        assert result.health_band == "green"

    def test_error_state(self):
        result = CycleResult(
            cycle_id="test-3",
            state=CycleState.ERROR,
            error="Something went wrong",
        )
        assert result.error == "Something went wrong"


class TestAgilePlusLoop:
    """Tests for AgilePlusLoop class."""

    @pytest.fixture
    def mock_components(self):
        """Mock all external components that AgilePlusLoop initializes."""
        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.CodebaseScanner") as mock_scanner, \
             patch("thegent.governance.agileplus.HealthScoreComputer") as mock_health_computer, \
             patch("thegent.governance.agileplus.HealthAnalyzer") as mock_analyzer, \
             patch("thegent.governance.agileplus.RemediationPlanner") as mock_planner, \
             patch("thegent.governance.agileplus.BacklogManager") as mock_backlog, \
             patch("thegent.governance.agileplus.CostController") as mock_cost, \
             patch("thegent.governance.agileplus.EvidenceLedger") as mock_ledger:

            # Configure mock settings
            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            # Configure scanner mock
            scanner_instance = MagicMock()
            scan_result = MagicMock()
            scan_result.dimensions = [1, 2, 3]
            scanner_instance.scan.return_value = scan_result
            mock_scanner.return_value = scanner_instance

            # Configure health computer mock
            health_result = MagicMock()
            health_result.score = 85.0
            health_result.band = MagicMock(value="yellow")
            mock_health_computer.return_value = HealthScoreComputerMock(85.0)

            # Configure analyzer mock
            mock_analyzer.return_value = AnalyzerMock([])

            # Configure planner mock
            plan_mock = MagicMock()
            plan_mock.tasks = []
            plan_mock.total_estimated_calls = 0
            mock_planner.return_value = PlannerMock(plan_mock)

            # Configure backlog mock
            mock_backlog.return_value = BacklogMock([])

            # Configure cost controller mock
            usage_mock = MagicMock()
            usage_mock.calls_limit = 1000
            usage_mock.calls_used = 100
            mock_cost.return_value = CostControllerMock(usage_mock)

            # Configure evidence ledger mock
            mock_ledger.return_value = EvidenceLedgerMock()

            yield {
                "settings": settings,
                "scanner": mock_scanner,
                "health_computer": mock_health_computer,
                "analyzer": mock_analyzer,
                "planner": mock_planner,
                "backlog": mock_backlog,
                "cost": mock_cost,
                "ledger": mock_ledger,
            }

    def test_init_default_values(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        loop = AgilePlusLoop(
            project_dir=tmp_path,
            health_targets_path=health_targets,
        )

        assert loop.project_dir == tmp_path
        assert loop.health_threshold == 90.0
        assert loop.max_tasks_per_cycle == 10
        assert loop.max_rerolls == 2
        assert loop.lifecycle_mode == "soft"
        assert loop.state == CycleState.IDLE

    def test_init_custom_values(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        loop = AgilePlusLoop(
            project_dir=tmp_path,
            health_targets_path=health_targets,
            health_threshold=80.0,
            max_tasks_per_cycle=20,
            max_rerolls=3,
            lifecycle_mode="hard",
        )

        assert loop.health_threshold == 80.0
        assert loop.max_tasks_per_cycle == 20
        assert loop.max_rerolls == 3
        assert loop.lifecycle_mode == "hard"

    def test_state_property(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")
        loop = AgilePlusLoop(tmp_path, health_targets)
        assert loop.state == CycleState.IDLE

    def test_cycle_id_property(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")
        loop = AgilePlusLoop(tmp_path, health_targets)
        assert loop.cycle_id == ""

    def test_shutdown_requested_property(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")
        loop = AgilePlusLoop(tmp_path, health_targets)
        assert loop.shutdown_requested is False

    def test_get_status(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")
        loop = AgilePlusLoop(tmp_path, health_targets)
        status = loop.get_status()
        assert status["state"] == "idle"
        assert status["cycle_id"] == ""
        assert status["shutdown_requested"] is False

    def test_request_shutdown(self, tmp_path, mock_components):
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")
        loop = AgilePlusLoop(tmp_path, health_targets)
        loop.request_shutdown()
        assert loop.shutdown_requested is True


class HealthScoreComputerMock:
    """Mock for HealthScoreComputer that returns a simple score."""

    def __init__(self, score: float):
        self.score = score

    def compute(self, scan_result):
        result = MagicMock()
        result.score = self.score
        result.band = MagicMock(value="green")
        return result


class AnalyzerMock:
    """Mock for HealthAnalyzer."""

    def __init__(self, findings):
        self.findings = findings

    def analyze(self, scan_result):
        return self.findings


class PlannerMock:
    """Mock for RemediationPlanner."""

    def __init__(self, plan):
        self.plan = plan

    def plan(self, findings, budget_remaining_calls):
        return self.plan


class BacklogMock:
    """Mock for BacklogManager."""

    def __init__(self, pending):
        self.pending = pending

    def get_pending(self):
        return self.pending

    def resolve(self, finding_id):
        pass

    def increment_attempt(self, finding_id):
        pass

    def defer(self, finding_id, reason):
        pass


class CostControllerMock:
    """Mock for CostController."""

    def __init__(self, usage):
        self.usage = usage

    def get_today_usage(self):
        return self.usage


class EvidenceLedgerMock:
    """Mock for EvidenceLedger."""

    def record(self, **kwargs):
        pass


class TestAgilePlusLoopStateTransitions:
    """Tests for AgilePlusLoop state transitions."""

    def test_state_transitions_idle_to_scanning_to_idle(self, tmp_path):
        """Test that health >= threshold returns to IDLE without changes."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.CodebaseScanner") as mock_scanner, \
             patch("thegent.governance.agileplus.HealthScoreComputer") as mock_health_computer, \
             patch("thegent.governance.agileplus.EvidenceLedger"):

            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            scanner_instance = MagicMock()
            scan_result = MagicMock()
            scan_result.dimensions = [1, 2, 3]
            scanner_instance.scan.return_value = scan_result
            mock_scanner.return_value = scanner_instance

            # Health score >= threshold (95.0 >= 90.0)
            mock_health_computer.return_value = HealthScoreComputerMock(95.0)

            loop = AgilePlusLoop(tmp_path, health_targets, health_threshold=90.0)
            result = loop.run_once()

            assert result.state == CycleState.IDLE
            assert result.health_score == 95.0

    def test_state_transitions_full_cycle(self, tmp_path):
        """Test full cycle through all states."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.CodebaseScanner") as mock_scanner, \
             patch("thegent.governance.agileplus.HealthScoreComputer") as mock_health_computer, \
             patch("thegent.governance.agileplus.HealthAnalyzer") as mock_analyzer, \
             patch("thegent.governance.agileplus.RemediationPlanner") as mock_planner, \
             patch("thegent.governance.agileplus.BacklogManager") as mock_backlog, \
             patch("thegent.governance.agileplus.CostController") as mock_cost, \
             patch("thegent.governance.agileplus.EvidenceLedger") as mock_ledger, \
             patch("thegent.governance.agileplus.AgentDeployer") as mock_deployer, \
             patch("thegent.governance.agileplus.VerificationGate") as mock_gate:

            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            scanner_instance = MagicMock()
            scan_result = MagicMock()
            scan_result.dimensions = [1]
            scanner_instance.scan.return_value = scan_result
            mock_scanner.return_value = scanner_instance

            # Health score < threshold triggers cycle
            mock_health_computer.return_value = HealthScoreComputerMock(75.0)

            # Empty findings
            mock_analyzer.return_value = AnalyzerMock([])

            # Empty plan
            plan_mock = MagicMock()
            plan_mock.tasks = []
            plan_mock.total_estimated_calls = 0
            mock_planner.return_value = PlannerMock(plan_mock)

            mock_backlog.return_value = BacklogMock([])

            usage_mock = MagicMock()
            usage_mock.calls_limit = 1000
            usage_mock.calls_used = 100
            mock_cost.return_value = CostControllerMock(usage_mock)

            mock_ledger.return_value = EvidenceLedgerMock()

            # Deployment result
            deploy_result = MagicMock()
            deploy_result.tasks_completed = 0
            deploy_result.executions = []
            deploy_result.tasks = []
            mock_deployer.return_value = DeployerMock(deploy_result)

            mock_gate.return_value = GateMock(0)

            loop = AgilePlusLoop(tmp_path, health_targets, health_threshold=90.0)
            result = loop.run_once()

            # Should complete without error
            assert result.error == ""


class DeployerMock:
    """Mock for AgentDeployer."""

    def __init__(self, result):
        self.result = result

    def deploy(self, plan, pre_scan, cycle_id):
        return self.result


class GateMock:
    """Mock for VerificationGate."""

    def __init__(self, verified_count):
        self.verified_count = verified_count

    def verify_task(self, task, execution, pre_scan):
        result = MagicMock()
        result.verdict = MagicMock(value="pass")
        return result

    def should_reroll(self, attempts):
        return False


class TestAgilePlusLoopErrorHandling:
    """Tests for AgilePlusLoop error handling."""

    def test_handles_scanner_error(self, tmp_path):
        """Test that scanner errors are caught and returned in result."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.CodebaseScanner") as mock_scanner, \
             patch("thegent.governance.agileplus.EvidenceLedger"):

            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            scanner_instance = MagicMock()
            scanner_instance.scan.side_effect = RuntimeError("Scanner failed")
            mock_scanner.return_value = scanner_instance

            mock_ledger.return_value = EvidenceLedgerMock()

            loop = AgilePlusLoop(tmp_path, health_targets, health_threshold=90.0)
            result = loop.run_once()

            assert result.state == CycleState.ERROR
            assert "Scanner failed" in result.error


class TestAgilePlusLoopContinuous:
    """Tests for AgilePlusLoop continuous mode."""

    def test_run_continuous_max_cycles(self, tmp_path):
        """Test run_continuous respects max_cycles."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        call_count = 0

        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.AgilePlusLoop.run_once") as mock_run_once:

            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            def run_once_side_effect():
                nonlocal call_count
                call_count += 1
                result = MagicMock()
                result.health_score = 95.0
                return result

            mock_run_once.side_effect = run_once_side_effect

            loop = AgilePlusLoop(tmp_path, health_targets)
            results = loop.run_continuous(interval_seconds=1, max_cycles=3)

            assert len(results) == 3
            assert call_count == 3

    def test_run_continuous_shutdown_requested(self, tmp_path):
        """Test run_continuous stops when shutdown is requested."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        call_count = 0

        with patch("thegent.governance.agileplus.ThegentSettings") as mock_settings, \
             patch("thegent.governance.agileplus.AgilePlusLoop.run_once") as mock_run_once:

            settings = MagicMock()
            settings.session_dir = Path("/tmp/session")
            mock_settings.return_value = settings

            def run_once_side_effect(self):
                nonlocal call_count
                call_count += 1
                if call_count >= 2:
                    self._shutdown_requested = True
                result = MagicMock()
                result.health_score = 95.0
                return result

            mock_run_once.side_effect = run_once_side_effect

            loop = AgilePlusLoop(tmp_path, health_targets)
            results = loop.run_continuous(interval_seconds=1, max_cycles=10)

            # Should stop after shutdown is requested
            assert call_count == 2


class TestAgilePlusSignalHandling:
    """Tests for AgilePlusLoop signal handling."""

    def test_signal_handler_sets_shutdown(self, tmp_path):
        """Test that signal handler sets shutdown_requested."""
        health_targets = tmp_path / "health-targets.json"
        health_targets.write_text("{}")

        with patch("thegent.governance.agileplus.ThegentSettings"):
            loop = AgilePlusLoop(tmp_path, health_targets)
            assert loop.shutdown_requested is False

            loop._signal_handler(15, None)  # SIGTERM

            assert loop.shutdown_requested is True
