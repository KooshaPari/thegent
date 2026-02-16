"""Unit tests for main.py subcommand routing.

Verifies that every registered CLI path reaches the correct handler function.
Each test mocks the underlying *_cmd callable and confirms exit_code == 0.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Top-level commands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTopLevelRouting:
    """Verify top-level commands are routable on the root app."""

    @patch("thegent.main.run_cmd")
    def test_run_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-001
        result = runner.invoke(app, ["run", "hello", "claude"])
        assert result.exit_code == 0

    @patch("thegent.main.bg_cmd")
    def test_bg_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-002
        result = runner.invoke(app, ["bg", "hello", "claude"])
        assert result.exit_code == 0

    @patch("thegent.main.ps_cmd")
    def test_ps_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-003
        result = runner.invoke(app, ["ps"])
        assert result.exit_code == 0

    @patch("thegent.main.status_cmd")
    def test_status_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-004
        result = runner.invoke(app, ["status", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.inspect_cmd")
    def test_inspect_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-005
        result = runner.invoke(app, ["inspect"])
        assert result.exit_code == 0

    @patch("thegent.main.logs_cmd")
    def test_logs_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-006
        result = runner.invoke(app, ["logs", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.wait_cmd")
    def test_wait_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-007
        result = runner.invoke(app, ["wait", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.stop_cmd")
    def test_stop_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-008
        result = runner.invoke(app, ["stop", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.pause_cmd")
    def test_pause_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-009
        result = runner.invoke(app, ["pause", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.resume_cmd")
    def test_resume_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-010
        result = runner.invoke(app, ["resume", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.list_agents_cmd")
    def test_list_agents(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-011
        result = runner.invoke(app, ["list-agents"])
        assert result.exit_code == 0

    @patch("thegent.main.list_droids_cmd")
    def test_list_droids(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-012
        result = runner.invoke(app, ["list-droids"])
        assert result.exit_code == 0
        assert mock_cmd.called

    @patch("thegent.main.list_droids_cmd")
    def test_list_droids_with_cd(self, mock_cmd: MagicMock, tmp_path: Path) -> None:
        # @trace FR-MAIN-020
        """Explicit --cd is forwarded to list_droids_cmd."""
        result = runner.invoke(app, ["list-droids", f"--cd={tmp_path}"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=tmp_path)

    @patch("thegent.main.list_models_cmd")
    def test_list_models(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-013
        result = runner.invoke(app, ["list-models"])
        assert result.exit_code == 0

    @patch("thegent.main.resolve_model_route_cmd")
    def test_resolve_model_route(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-014
        result = runner.invoke(app, ["resolve-model-route", "gpt-4"])
        assert result.exit_code == 0

    @patch("thegent.main.cockpit_cmd")
    def test_cockpit_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-015
        result = runner.invoke(app, ["cockpit"])
        assert result.exit_code == 0

    @patch("thegent.main.feedback_cmd")
    def test_feedback_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-016
        result = runner.invoke(app, ["feedback", "run-1", "0.9"])
        assert result.exit_code == 0

    @patch("thegent.main.archive_cmd")
    def test_archive_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-017
        result = runner.invoke(app, ["archive"])
        assert result.exit_code == 0

    @patch("thegent.main.operations_cmd")
    def test_operations(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-018
        result = runner.invoke(app, ["operations"])
        assert result.exit_code == 0

    @patch("thegent.main.modes_cmd")
    def test_modes(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-019
        result = runner.invoke(app, ["modes"])
        assert result.exit_code == 0

    @patch("thegent.main.benchmark_cmd")
    def test_benchmark_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-020
        result = runner.invoke(app, ["benchmark"])
        assert result.exit_code == 0

    @patch("thegent.main.closure_pack_cmd")
    def test_closure_pack_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-021
        result = runner.invoke(app, ["closure-pack"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-022
        result = runner.invoke(app, ["session-contracts"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_session_contract_health_gate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-023
        result = runner.invoke(app, ["session-contract-health-gate"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_session_contract_health_report(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-024
        result = runner.invoke(app, ["session-contract-health-report"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_session_contract_health_trend(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-025
        result = runner.invoke(app, ["session-contract-health-trend"])
        assert result.exit_code == 0

    @patch("thegent.main.cliproxy_login_cmd")
    def test_login_top_level(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-026
        result = runner.invoke(app, ["login", "claude"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Orchestrate subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrateRouting:
    """Verify commands routed via `orchestrate` subgroup."""

    @patch("thegent.main.run_cmd")
    def test_run_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-027
        result = runner.invoke(app, ["orchestrate", "run", "hello", "claude"])
        assert result.exit_code == 0

    @patch("thegent.main.bg_cmd")
    def test_bg_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-028
        result = runner.invoke(app, ["orchestrate", "bg", "hello", "claude"])
        assert result.exit_code == 0

    @patch("thegent.main.ps_cmd")
    def test_ps_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-029
        result = runner.invoke(app, ["orchestrate", "ps"])
        assert result.exit_code == 0

    @patch("thegent.main.status_cmd")
    def test_status_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-030
        result = runner.invoke(app, ["orchestrate", "status", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.inspect_cmd")
    def test_inspect_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-031
        result = runner.invoke(app, ["orchestrate", "inspect"])
        assert result.exit_code == 0

    @patch("thegent.main.logs_cmd")
    def test_logs_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-032
        result = runner.invoke(app, ["orchestrate", "logs", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.wait_cmd")
    def test_wait_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-033
        result = runner.invoke(app, ["orchestrate", "wait", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.stop_cmd")
    def test_stop_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-034
        result = runner.invoke(app, ["orchestrate", "stop", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.pause_cmd")
    def test_pause_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-035
        result = runner.invoke(app, ["orchestrate", "pause", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.resume_cmd")
    def test_resume_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-036
        result = runner.invoke(app, ["orchestrate", "resume", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.cliproxy_login_cmd")
    def test_login_via_orchestrate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-037
        result = runner.invoke(app, ["orchestrate", "login", "claude"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Govern subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGovernRouting:
    """Verify commands routed via `govern` subgroup."""

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-038
        result = runner.invoke(app, ["govern", "escalate", "add", "run-1", "policy violation"])
        assert result.exit_code == 0

    @patch("thegent.main.escalate_list_cmd")
    def test_escalate_list(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-039
        result = runner.invoke(app, ["govern", "escalate", "list"])
        assert result.exit_code == 0

    @patch("thegent.main.escalate_resolve_cmd")
    def test_escalate_resolve(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-040
        result = runner.invoke(app, ["govern", "escalate", "resolve", "run-1"])
        assert result.exit_code == 0

    @patch("thegent.main.sweep_cmd")
    def test_govern_sweep(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-041
        result = runner.invoke(app, ["govern", "sweep"])
        assert result.exit_code == 0

    @patch("thegent.main.purge_cmd")
    def test_govern_purge(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-042
        result = runner.invoke(app, ["govern", "purge"])
        assert result.exit_code == 0

    @patch("thegent.main.data_protection_cmd")
    def test_govern_data_protection(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-043
        result = runner.invoke(app, ["govern", "data-protection"])
        assert result.exit_code == 0

    @patch("thegent.main.contracts_registry_cmd")
    def test_govern_contracts(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-044
        result = runner.invoke(app, ["govern", "contracts"])
        assert result.exit_code == 0

    @patch("thegent.main.contracts_conformance_cmd")
    def test_govern_conformance(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-045
        result = runner.invoke(app, ["govern", "conformance"])
        assert result.exit_code == 0

    @patch("thegent.main.migration_cmd")
    def test_govern_migration(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-046
        result = runner.invoke(app, ["govern", "migration", "csm", "csm-v1"])
        assert result.exit_code == 0

    @patch("thegent.main.audit_verify_cmd")
    def test_govern_verify(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-047
        result = runner.invoke(app, ["govern", "verify"])
        assert result.exit_code == 0

    @patch("thegent.main.policy_show_cmd")
    def test_govern_show_policy(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-048
        result = runner.invoke(app, ["govern", "show-policy"])
        assert result.exit_code == 0

    @patch("thegent.main.feedback_cmd")
    def test_govern_feedback(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-049
        result = runner.invoke(app, ["govern", "feedback", "run-1", "0.8"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_govern_health_gate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-050
        result = runner.invoke(app, ["govern", "health-gate"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_govern_health_report(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-051
        result = runner.invoke(app, ["govern", "health-report"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_govern_health_trend(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-052
        result = runner.invoke(app, ["govern", "health-trend"])
        assert result.exit_code == 0

    @patch("thegent.main.closure_pack_cmd")
    def test_govern_closure_pack(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-053
        result = runner.invoke(app, ["govern", "closure-pack"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contracts_cmd")
    def test_govern_session_contracts(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-054
        result = runner.invoke(app, ["govern", "session-contracts"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Recover subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRecoverRouting:
    """Verify commands routed via `recover` subgroup."""

    @patch("thegent.main.stop_cmd")
    def test_recover_stop(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-055
        result = runner.invoke(app, ["recover", "stop", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_reconcile_cmd")
    def test_recover_reconcile(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-056
        result = runner.invoke(app, ["recover", "reconcile"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_rollback_cmd")
    def test_recover_rollback(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-057
        result = runner.invoke(app, ["recover", "rollback", "ckpt-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_recover_cmd")
    def test_recover_dag_recover(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-058
        result = runner.invoke(app, ["recover", "dag-recover"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Observe subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestObserveRouting:
    """Verify commands routed via `observe` subgroup."""

    @patch("thegent.cli.observe_summary_cmd")
    def test_observe_summary(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-059
        result = runner.invoke(app, ["observe", "summary"])
        assert result.exit_code == 0

    @patch("thegent.main.drift_cmd")
    def test_observe_drift(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-060
        result = runner.invoke(app, ["observe", "drift"])
        assert result.exit_code == 0

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_observe_trend(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-061
        result = runner.invoke(app, ["observe", "trend"])
        assert result.exit_code == 0

    @patch("thegent.main.status_cmd")
    def test_observe_status(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-062
        result = runner.invoke(app, ["observe", "status", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.inspect_cmd")
    def test_observe_inspect(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-063
        result = runner.invoke(app, ["observe", "inspect"])
        assert result.exit_code == 0

    @patch("thegent.main.logs_cmd")
    def test_observe_logs(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-064
        result = runner.invoke(app, ["observe", "logs", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.wait_cmd")
    def test_observe_wait(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-065
        result = runner.invoke(app, ["observe", "wait", "sess-1"])
        assert result.exit_code == 0

    @patch("thegent.main.cockpit_cmd")
    def test_observe_cockpit(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-066
        result = runner.invoke(app, ["observe", "cockpit"])
        assert result.exit_code == 0

    @patch("thegent.main.archive_cmd")
    def test_observe_archive(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-067
        result = runner.invoke(app, ["observe", "archive"])
        assert result.exit_code == 0

    @patch("thegent.main.history_cmd")
    def test_observe_history(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-068
        result = runner.invoke(app, ["observe", "history"])
        assert result.exit_code == 0

    @patch("thegent.main.benchmark_cmd")
    def test_observe_benchmark(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-069
        result = runner.invoke(app, ["observe", "benchmark"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_probe_cmd")
    def test_observe_probe(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-070
        result = runner.invoke(app, ["observe", "probe"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Plan subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPlanRouting:
    """Verify commands routed via `plan` subgroup."""

    @patch("thegent.main.dag_list_cmd")
    def test_plan_list(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-071
        result = runner.invoke(app, ["plan", "list"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_validate_cmd")
    def test_plan_validate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-072
        result = runner.invoke(app, ["plan", "validate"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_add_cmd")
    def test_plan_add(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-073
        result = runner.invoke(app, ["plan", "add", "T-1", "claude", "do stuff"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_update_cmd")
    def test_plan_update(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-074
        result = runner.invoke(app, ["plan", "update", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_remove_cmd")
    def test_plan_remove(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-075
        result = runner.invoke(app, ["plan", "remove", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_cancel_cmd")
    def test_plan_cancel(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-076
        result = runner.invoke(app, ["plan", "cancel", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_ready_cmd")
    def test_plan_ready(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-077
        result = runner.invoke(app, ["plan", "ready"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_run_cmd")
    def test_plan_run(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-078
        result = runner.invoke(app, ["plan", "run"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_status_cmd")
    def test_plan_status(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-079
        result = runner.invoke(app, ["plan", "status"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_plan_checkpoint(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-080
        result = runner.invoke(app, ["plan", "checkpoint"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_rollback_cmd")
    def test_plan_rollback(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-081
        result = runner.invoke(app, ["plan", "rollback", "ckpt-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_checkpoints_cmd")
    def test_plan_checkpoints(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-082
        result = runner.invoke(app, ["plan", "checkpoints"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_probe_cmd")
    def test_plan_probe(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-083
        result = runner.invoke(app, ["plan", "probe"])
        assert result.exit_code == 0

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-084
        result = runner.invoke(app, ["plan", "analyze"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_sync_cmd")
    def test_plan_sync(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-085
        result = runner.invoke(app, ["plan", "sync"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# History subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHistoryRouting:
    """Verify commands routed via `history` subgroup."""

    @patch("thegent.main.history_cmd")
    def test_history_default(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-086
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0

    @patch("thegent.main.history_cmd")
    def test_history_list(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-087
        result = runner.invoke(app, ["history", "list"])
        assert result.exit_code == 0

    @patch("thegent.cli.events_cmd")
    def test_history_events(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-088
        result = runner.invoke(app, ["history", "events"])
        assert result.exit_code == 0

    @patch("thegent.main.audit_verify_cmd")
    def test_history_verify(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-089
        result = runner.invoke(app, ["history", "verify"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# DAG subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDagRouting:
    """Verify commands routed via `dag` subgroup."""

    @patch("thegent.main.dag_list_cmd")
    def test_dag_list(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-090
        result = runner.invoke(app, ["dag", "list"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_validate_cmd")
    def test_dag_validate(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-091
        result = runner.invoke(app, ["dag", "validate"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_add_cmd")
    def test_dag_add(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-092
        result = runner.invoke(app, ["dag", "add", "T-1", "claude", "do stuff"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-093
        result = runner.invoke(app, ["dag", "update", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_remove_cmd")
    def test_dag_remove(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-094
        result = runner.invoke(app, ["dag", "remove", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_cancel_cmd")
    def test_dag_cancel(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-095
        result = runner.invoke(app, ["dag", "cancel", "T-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_ready_cmd")
    def test_dag_ready(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-096
        result = runner.invoke(app, ["dag", "ready"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-097
        result = runner.invoke(app, ["dag", "run"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_status_cmd")
    def test_dag_status(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-098
        result = runner.invoke(app, ["dag", "status"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_sync_cmd")
    def test_dag_sync(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-099
        result = runner.invoke(app, ["dag", "sync"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_reconcile_cmd")
    def test_dag_reconcile(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-100
        result = runner.invoke(app, ["dag", "reconcile"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_dag_checkpoint(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-101
        result = runner.invoke(app, ["dag", "checkpoint"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_rollback_cmd")
    def test_dag_rollback(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-102
        result = runner.invoke(app, ["dag", "rollback", "ckpt-1"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_checkpoints_cmd")
    def test_dag_checkpoints(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-103
        result = runner.invoke(app, ["dag", "checkpoints"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-104
        result = runner.invoke(app, ["dag", "recover"])
        assert result.exit_code == 0

    @patch("thegent.main.dag_probe_cmd")
    def test_dag_probe(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-105
        result = runner.invoke(app, ["dag", "probe"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# MCP subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMcpRouting:
    """Verify commands routed via `mcp` subgroup."""

    @patch("thegent.mcp_manage.install_to_client", return_value=(True, "ok"))
    @patch("thegent.mcp_manage._get_mcp_url", return_value="http://127.0.0.1:3847/mcp")
    @patch("thegent.config.ThegentSettings")
    def test_mcp_install(self, mock_settings: MagicMock, mock_url: MagicMock, mock_install: MagicMock) -> None:
        # @trace FR-MAIN-106
        result = runner.invoke(app, ["mcp", "install", "cursor"])
        assert result.exit_code == 0

    @patch("thegent.mcp_manage.mcp_up", return_value=(True, "started"))
    def test_mcp_up(self, mock_up: MagicMock) -> None:
        # @trace FR-MAIN-107
        result = runner.invoke(app, ["mcp", "up"])
        assert result.exit_code == 0

    @patch("thegent.mcp_manage.mcp_down", return_value=(True, "stopped"))
    def test_mcp_down(self, mock_down: MagicMock) -> None:
        # @trace FR-MAIN-108
        result = runner.invoke(app, ["mcp", "down"])
        assert result.exit_code == 0

    @patch("thegent.mcp_manage.service_install", return_value=(True, "installed"))
    def test_mcp_service(self, mock_svc: MagicMock) -> None:
        # @trace FR-MAIN-109
        result = runner.invoke(app, ["mcp", "service", "install"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Models subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestModelsRouting:
    """Verify commands routed via `models` subgroup."""

    @patch("thegent.models.invalidate_models_cache", return_value=True)
    def test_models_refresh(self, mock_inv: MagicMock) -> None:
        # @trace FR-MAIN-110
        result = runner.invoke(app, ["models", "refresh"])
        assert result.exit_code == 0

    @patch("thegent.cli.list_model_contract_schema_cmd")
    def test_models_contract(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-111
        result = runner.invoke(app, ["models", "contract"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Cliproxy subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCliproxyRouting:
    """Verify commands routed via `cliproxy` subgroup."""

    @patch("thegent.agents.cliproxy_manager._ensure_config", return_value="/tmp/cfg")
    @patch("thegent.config.ThegentSettings")
    def test_cliproxy_ensure_config(self, mock_settings: MagicMock, mock_ensure: MagicMock) -> None:
        # @trace FR-MAIN-112
        result = runner.invoke(app, ["cliproxy", "ensure-config"])
        assert result.exit_code == 0

    @patch("thegent.main.cliproxy_login_cmd")
    def test_cliproxy_login(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-113
        result = runner.invoke(app, ["cliproxy", "login", "claude"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Policy subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPolicyRouting:
    """Verify commands routed via `policy` subgroup."""

    @patch("thegent.main.policy_show_cmd")
    def test_policy_show(self, mock_cmd: MagicMock) -> None:
        # @trace FR-MAIN-114
        result = runner.invoke(app, ["policy", "show"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Serve and install top-level
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestServeAndInstallRouting:
    """Verify serve and install commands."""

    @patch("thegent.mcp_server.run")
    def test_serve(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-115
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 0

    @patch("thegent.install.run_install", return_value={"copied": 1, "skipped": 0, "conflicts": 0})
    def test_install(self, mock_install: MagicMock) -> None:
        # @trace FR-MAIN-116
        result = runner.invoke(app, ["install"])
        assert result.exit_code == 0

    @patch("thegent.install.run_wizard")
    def test_init(self, mock_wizard: MagicMock) -> None:
        # @trace FR-MAIN-117
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Observe kpis (inline logic, needs deeper mocks)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestObserveKpisRouting:
    """Verify observe kpis command reaches the handler."""

    @patch("thegent.contracts.telemetry.ContractTelemetry")
    @patch("thegent.config.ThegentSettings")
    def test_observe_kpis(self, mock_settings: MagicMock, mock_ct_cls: MagicMock) -> None:
        # @trace FR-MAIN-118
        mock_ct = MagicMock()
        mock_ct.get_fallback_kpis.return_value = {
            "total": 0,
            "fallback_rate": 0.0,
            "success_rate": 1.0,
            "avg_confidence": 0.0,
            "structural_drift_pct": 0.0,
            "semantic_drift_pct": 0.0,
            "by_provider": {},
        }
        mock_ct_cls.return_value = mock_ct
        result = runner.invoke(app, ["observe", "kpis"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Coverage gaps: observe kpis with by_provider data (lines 451-465)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestObserveKpisWithProviders:
    """Tests for observe kpis when by_provider has data (lines 451-465)."""

    @patch("thegent.contracts.telemetry.ContractTelemetry")
    @patch("thegent.config.ThegentSettings")
    def test_observe_kpis_by_provider_table(self, mock_settings: MagicMock, mock_ct_cls: MagicMock) -> None:
        # @trace FR-MAIN-118
        """observe kpis renders by_provider table when data is present."""
        mock_ct = MagicMock()
        mock_ct.get_fallback_kpis.return_value = {
            "total": 10,
            "fallback_rate": 0.1,
            "success_rate": 0.9,
            "avg_confidence": 0.85,
            "structural_drift_pct": 1.0,
            "semantic_drift_pct": 2.0,
            "by_provider": {
                "gemini": {
                    "fallback_rate": 0.05,
                    "success_rate": 0.95,
                    "avg_confidence": 0.9,
                    "total": 5,
                },
                "claude": {
                    "fallback_rate": 0.15,
                    "success_rate": 0.85,
                    "avg_confidence": 0.8,
                    "total": 5,
                },
            },
        }
        mock_ct_cls.return_value = mock_ct
        result = runner.invoke(app, ["observe", "kpis"])
        assert result.exit_code == 0
        assert "gemini" in result.output
        assert "claude" in result.output


# ---------------------------------------------------------------------------
# Coverage gaps: history --events dispatches to events_cmd (lines 578-582)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHistoryEventsFlag:
    """Tests for history events subcommand and history-legacy --events (lines 264, 578-582)."""

    @patch("thegent.cli.events_cmd")
    def test_history_events_subcommand(self, mock_events: MagicMock) -> None:
        # @trace FR-MAIN-086
        """history events subcommand dispatches to events_cmd (line 264-265)."""
        result = runner.invoke(app, ["history", "events"])
        assert result.exit_code == 0
        mock_events.assert_called_once()

    @patch("thegent.cli.events_cmd")
    def test_history_legacy_events_flag(self, mock_events: MagicMock) -> None:
        # @trace FR-MAIN-086
        """history-legacy --events dispatches to events_cmd (lines 578-582)."""
        result = runner.invoke(app, ["history-legacy", "--events"])
        assert result.exit_code == 0
        mock_events.assert_called_once()


# ---------------------------------------------------------------------------
# Coverage gaps: dag sync --watch with time.sleep (line 1122)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDagSyncWatch:
    """Tests for dag sync --watch (line 1122)."""

    @patch("thegent.main.dag_sync_cmd")
    def test_dag_sync_watch_runs_loop(self, mock_sync: MagicMock) -> None:
        # @trace FR-MAIN-085
        """dag sync --watch calls dag_sync_cmd and sleeps."""
        call_count = 0

        def sync_side_effect(**kwargs) -> None:
            nonlocal call_count
            call_count += 1

        mock_sync.side_effect = sync_side_effect
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            runner.invoke(app, ["plan", "sync", "--watch", "--interval", "1"])
        # It ran at least once before the interrupt
        assert call_count >= 1


# ---------------------------------------------------------------------------
# Coverage gaps: mcp install --client all (lines 1207, 1219)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMcpInstallAllClients:
    """Tests for mcp install all clients branch (lines 1207, 1219)."""

    @patch("thegent.mcp_manage.install_to_client")
    @patch("thegent.mcp_manage._get_mcp_url", return_value="http://127.0.0.1:3847/mcp")
    @patch("thegent.config.ThegentSettings")
    def test_mcp_install_all(self, mock_settings: MagicMock, mock_url: MagicMock, mock_install: MagicMock) -> None:
        # @trace FR-MAIN-106
        """mcp install all installs to all clients."""
        mock_install.return_value = (True, "ok")
        result = runner.invoke(app, ["mcp", "install", "all"])
        assert result.exit_code == 0
        assert mock_install.call_count == 5  # cursor, claude-code, codex, claude-desktop, droid

    @patch("thegent.mcp_manage.install_to_client")
    @patch("thegent.mcp_manage._get_mcp_url", return_value="http://127.0.0.1:3847/mcp")
    @patch("thegent.config.ThegentSettings")
    def test_mcp_install_failure_prints_red(
        self, mock_settings: MagicMock, mock_url: MagicMock, mock_install: MagicMock
    ) -> None:
        # @trace FR-MAIN-106
        """mcp install prints red when client install fails."""
        mock_install.return_value = (False, "permission denied")
        result = runner.invoke(app, ["mcp", "install", "cursor"])
        assert result.exit_code == 0
        assert "permission denied" in result.output


# ---------------------------------------------------------------------------
# Coverage gaps: mcp up/down failure paths (lines 1235-1236, 1251-1252)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMcpUpDownFailure:
    """Tests for mcp up/down failure exit code (lines 1235-1236, 1251-1252)."""

    @patch("thegent.mcp_manage.mcp_up", return_value=(False, "port in use"))
    def test_mcp_up_failure_exit_1(self, mock_up: MagicMock) -> None:
        # @trace FR-MAIN-107
        """mcp up failure raises exit code 1."""
        result = runner.invoke(app, ["mcp", "up"])
        assert result.exit_code == 1
        assert "port in use" in result.output

    @patch("thegent.mcp_manage.mcp_down", return_value=(False, "nothing running"))
    def test_mcp_down_failure_exit_1(self, mock_down: MagicMock) -> None:
        # @trace FR-MAIN-108
        """mcp down failure raises exit code 1."""
        result = runner.invoke(app, ["mcp", "down"])
        assert result.exit_code == 1
        assert "nothing running" in result.output


# ---------------------------------------------------------------------------
# Coverage gaps: mcp service actions (lines 1303, 1314-1317)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMcpServiceActions:
    """Tests for mcp service action branches (lines 1303, 1314-1317)."""

    @patch("thegent.mcp_manage.service_install", return_value=(False, "Failed to install"))
    def test_mcp_service_install_failure_exit_1(self, mock_svc: MagicMock) -> None:
        # @trace FR-MAIN-109
        """mcp service install failure raises exit 1."""
        result = runner.invoke(app, ["mcp", "service", "install"])
        assert result.exit_code == 1

    def test_mcp_service_unknown_action_exit_1(self) -> None:
        # @trace FR-MAIN-109
        """mcp service unknown action raises exit 1."""
        result = runner.invoke(app, ["mcp", "service", "unknown-action"])
        assert result.exit_code == 1
        assert "Unknown action" in result.output

    def test_serve_import_error_exit_1(self) -> None:
        # @trace FR-MAIN-115
        """serve fails with exit 1 when fastmcp not installed (lines 1314-1317)."""
        import sys

        # Remove cached module so the import inside serve() actually fails
        saved = sys.modules.pop("thegent.mcp_server", None)
        try:
            with patch.dict(sys.modules, {"thegent.mcp_server": None}):
                result = runner.invoke(app, ["serve"])
                assert result.exit_code == 1
        finally:
            if saved is not None:
                sys.modules["thegent.mcp_server"] = saved


# ---------------------------------------------------------------------------
# Coverage gaps: install command (lines 1345, 1347, 1370-1372, 1379, 1383)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInstallCommandOutputPaths:
    """Tests for install command output formatting (lines 1345-1383)."""

    @patch("thegent.install.run_install")
    def test_install_undo_output(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-116
        """install --undo shows removed/restored/reverted counts."""
        mock_run.return_value = {"removed": 2, "restored": 1, "reverted": 3, "errors": 0}
        result = runner.invoke(app, ["install", "--undo"])
        assert result.exit_code == 0
        assert "Removed" in result.output
        assert "Restored" in result.output
        assert "Reverted" in result.output

    @patch("thegent.install.run_install")
    def test_install_undo_with_errors(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-116
        """install --undo with errors shows error count."""
        mock_run.return_value = {"removed": 1, "restored": 0, "reverted": 0, "errors": 2}
        result = runner.invoke(app, ["install", "--undo"])
        assert result.exit_code == 0
        assert "Errors" in result.output

    @patch("thegent.install.run_install")
    def test_install_interactive_mode(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-116
        """install --interactive sets mode to interactive."""
        mock_run.return_value = {"copied": 1, "skipped": 0, "conflicts": 0, "errors": 0}
        result = runner.invoke(app, ["install", "--interactive"])
        assert result.exit_code == 0
        assert "interactive" in result.output

    @patch("thegent.install.run_install")
    def test_install_force_mode(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-116
        """install --force sets mode to force."""
        mock_run.return_value = {"copied": 1, "skipped": 0, "conflicts": 0, "errors": 0}
        result = runner.invoke(app, ["install", "--force"])
        assert result.exit_code == 0
        assert "force" in result.output

    @patch("thegent.install.run_install")
    def test_install_bundle_flags_forwarded(self, mock_run: MagicMock) -> None:
        # @trace FR-MAIN-117
        """Bundle flags are passed through to install runner."""
        mock_run.return_value = {"copied": 1, "skipped": 0, "errors": 0, "conflicts": 0}
        result = runner.invoke(
            app,
            [
                "install",
                "--bundle",
                "web",
                "--bundle",
                "hooks",
                "--bundle-manifest",
                "/tmp/thegent-bundles.json",
            ],
        )
        assert result.exit_code == 0
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["bundles"] == ["web", "hooks"]
        assert kwargs["bundle_manifest"] == "/tmp/thegent-bundles.json"
