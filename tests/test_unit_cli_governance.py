"""Unit tests for CLI governance commands."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.unit
class TestEscalateAddCommand:
    """Tests for `govern escalate add`."""

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-031
        result = runner.invoke(app, ["govern", "escalate", "add", "run-123", "policy violation"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            run_id="run-123",
            reason="policy violation",
            sla_minutes=30,
            owner=None,
            lane="standard",
        )

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add_with_sla(self, mock_cmd) -> None:
        # @trace FR-CLI-032
        result = runner.invoke(app, ["govern", "escalate", "add", "run-456", "timeout", "--sla", "60"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            run_id="run-456",
            reason="timeout",
            sla_minutes=60,
            owner=None,
            lane="standard",
        )

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add_with_owner(self, mock_cmd) -> None:
        # @trace FR-CLI-033
        result = runner.invoke(app, ["govern", "escalate", "add", "run-789", "blocked", "--owner", "alice"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            run_id="run-789",
            reason="blocked",
            sla_minutes=30,
            owner="alice",
            lane="standard",
        )

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add_with_lane(self, mock_cmd) -> None:
        # @trace FR-CLI-034
        result = runner.invoke(app, ["govern", "escalate", "add", "run-001", "drift", "--lane", "critical"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            run_id="run-001",
            reason="drift",
            sla_minutes=30,
            owner=None,
            lane="critical",
        )

    @patch("thegent.main.escalate_add_cmd")
    def test_escalate_add_all_options(self, mock_cmd) -> None:
        # @trace FR-CLI-035
        result = runner.invoke(
            app,
            [
                "govern",
                "escalate",
                "add",
                "run-all",
                "full options",
                "--sla",
                "15",
                "--owner",
                "bob",
                "--lane",
                "recovery",
            ],
        )
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            run_id="run-all",
            reason="full options",
            sla_minutes=15,
            owner="bob",
            lane="recovery",
        )


@pytest.mark.unit
class TestEscalateListCommand:
    """Tests for `govern escalate list`."""

    @patch("thegent.main.escalate_list_cmd")
    def test_escalate_list_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-036
        result = runner.invoke(app, ["govern", "escalate", "list"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(past_sla_only=False, limit=50, format=None)

    @patch("thegent.main.escalate_list_cmd")
    def test_escalate_list_past_sla(self, mock_cmd) -> None:
        # @trace FR-CLI-037
        result = runner.invoke(app, ["govern", "escalate", "list", "--past-sla"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(past_sla_only=True, limit=50, format=None)

    @patch("thegent.main.escalate_list_cmd")
    def test_escalate_list_with_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-038
        result = runner.invoke(app, ["govern", "escalate", "list", "--limit", "10"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(past_sla_only=False, limit=10, format=None)

    @patch("thegent.main.escalate_list_cmd")
    def test_escalate_list_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-039
        result = runner.invoke(app, ["govern", "escalate", "list", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(past_sla_only=False, limit=50, format="json")


@pytest.mark.unit
class TestEscalateResolveCommand:
    """Tests for `govern escalate resolve`."""

    @patch("thegent.main.escalate_resolve_cmd")
    def test_escalate_resolve_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-040
        result = runner.invoke(app, ["govern", "escalate", "resolve", "run-123"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(run_id="run-123", resolution="resolved")

    @patch("thegent.main.escalate_resolve_cmd")
    def test_escalate_resolve_with_resolution(self, mock_cmd) -> None:
        # @trace FR-CLI-041
        result = runner.invoke(app, ["govern", "escalate", "resolve", "run-456", "--resolution", "override-approved"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(run_id="run-456", resolution="override-approved")


@pytest.mark.unit
class TestSweepCommand:
    """Tests for `govern sweep`."""

    @patch("thegent.main.sweep_cmd")
    def test_sweep_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-042
        result = runner.invoke(app, ["govern", "sweep"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(drift_window=50, include_audit=False, format=None)

    @patch("thegent.main.sweep_cmd")
    def test_sweep_with_drift_window(self, mock_cmd) -> None:
        # @trace FR-CLI-043
        result = runner.invoke(app, ["govern", "sweep", "--drift-window", "100"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(drift_window=100, include_audit=False, format=None)

    @patch("thegent.main.sweep_cmd")
    def test_sweep_with_audit(self, mock_cmd) -> None:
        # @trace FR-CLI-044
        result = runner.invoke(app, ["govern", "sweep", "--audit"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(drift_window=50, include_audit=True, format=None)

    @patch("thegent.main.sweep_cmd")
    def test_sweep_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-045
        result = runner.invoke(app, ["govern", "sweep", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(drift_window=50, include_audit=False, format="json")


@pytest.mark.unit
class TestPurgeCommand:
    """Tests for `govern purge`."""

    @patch("thegent.main.purge_cmd")
    def test_purge_default_dry_run(self, mock_cmd) -> None:
        # @trace FR-CLI-046
        result = runner.invoke(app, ["govern", "purge"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(dry_run=True)

    @patch("thegent.main.purge_cmd")
    def test_purge_no_dry_run(self, mock_cmd) -> None:
        # @trace FR-CLI-047
        result = runner.invoke(app, ["govern", "purge", "--no-dry-run"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(dry_run=False)


@pytest.mark.unit
class TestDataProtectionCommand:
    """Tests for `govern data-protection`."""

    @patch("thegent.main.data_protection_cmd")
    def test_data_protection_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-048
        result = runner.invoke(app, ["govern", "data-protection"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None)

    @patch("thegent.main.data_protection_cmd")
    def test_data_protection_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-049
        result = runner.invoke(app, ["govern", "data-protection", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format="json")


@pytest.mark.unit
class TestContractsCommand:
    """Tests for `govern contracts`."""

    @patch("thegent.main.contracts_registry_cmd")
    def test_contracts_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-050
        result = runner.invoke(app, ["govern", "contracts"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None)

    @patch("thegent.main.contracts_registry_cmd")
    def test_contracts_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-051
        result = runner.invoke(app, ["govern", "contracts", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format="json")


@pytest.mark.unit
class TestConformanceCommand:
    """Tests for `govern conformance`."""

    @patch("thegent.main.contracts_conformance_cmd")
    def test_conformance_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-052
        result = runner.invoke(app, ["govern", "conformance"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None, check_drift=False, drift_window=50)

    @patch("thegent.main.contracts_conformance_cmd")
    def test_conformance_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-053
        result = runner.invoke(app, ["govern", "conformance", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format="json", check_drift=False, drift_window=50)

    @patch("thegent.main.contracts_conformance_cmd")
    def test_conformance_with_check_drift(self, mock_cmd) -> None:
        # @trace FR-CLI-054
        result = runner.invoke(app, ["govern", "conformance", "--check-drift"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None, check_drift=True, drift_window=50)

    @patch("thegent.main.contracts_conformance_cmd")
    def test_conformance_with_drift_window(self, mock_cmd) -> None:
        # @trace FR-CLI-055
        result = runner.invoke(app, ["govern", "conformance", "--drift-window", "200"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None, check_drift=False, drift_window=200)


@pytest.mark.unit
class TestMigrationCommand:
    """Tests for `govern migration`."""

    @patch("thegent.main.migration_cmd")
    def test_migration_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-056
        result = runner.invoke(app, ["govern", "migration", "csm", "csm-v1"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(contract_id="csm", version="csm-v1", format=None)

    @patch("thegent.main.migration_cmd")
    def test_migration_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-057
        result = runner.invoke(app, ["govern", "migration", "route", "v2", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(contract_id="route", version="v2", format="json")


@pytest.mark.unit
class TestAuditVerifyCommand:
    """Tests for `history verify` and `govern verify`."""

    @patch("thegent.main.audit_verify_cmd")
    def test_history_verify_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-058
        result = runner.invoke(app, ["history", "verify"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None)

    @patch("thegent.main.audit_verify_cmd")
    def test_history_verify_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-059
        result = runner.invoke(app, ["history", "verify", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format="json")

    @patch("thegent.main.audit_verify_cmd")
    def test_govern_verify_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-060
        result = runner.invoke(app, ["govern", "verify"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None)


@pytest.mark.unit
class TestPolicyShowCommand:
    """Tests for `policy show` and `govern show-policy`."""

    @patch("thegent.main.policy_show_cmd")
    def test_policy_show_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-031
        result = runner.invoke(app, ["policy", "show"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()

    @patch("thegent.main.policy_show_cmd")
    def test_govern_show_policy(self, mock_cmd) -> None:
        # @trace FR-CLI-032
        result = runner.invoke(app, ["govern", "show-policy"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()


@pytest.mark.unit
class TestSessionContractsCommand:
    """Tests for `session-contracts` and `govern session-contracts`."""

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-033
        result = runner.invoke(app, ["session-contracts"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            format=None,
            missing_only=False,
            summary_only=False,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_all(self, mock_cmd) -> None:
        # @trace FR-CLI-034
        result = runner.invoke(app, ["session-contracts", "--all"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=True,
            owner=None,
            format=None,
            missing_only=False,
            summary_only=False,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_owner(self, mock_cmd) -> None:
        # @trace FR-CLI-035
        result = runner.invoke(app, ["session-contracts", "--owner", "alice"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner="alice",
            format=None,
            missing_only=False,
            summary_only=False,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_format(self, mock_cmd) -> None:
        # @trace FR-CLI-036
        result = runner.invoke(app, ["session-contracts", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            format="json",
            missing_only=False,
            summary_only=False,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_missing_only(self, mock_cmd) -> None:
        # @trace FR-CLI-037
        result = runner.invoke(app, ["session-contracts", "--missing-only"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            format=None,
            missing_only=True,
            summary_only=False,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_summary_only(self, mock_cmd) -> None:
        # @trace FR-CLI-038
        result = runner.invoke(app, ["session-contracts", "--summary-only"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            format=None,
            missing_only=False,
            summary_only=True,
            strict=False,
        )

    @patch("thegent.main.session_contracts_cmd")
    def test_session_contracts_strict(self, mock_cmd) -> None:
        # @trace FR-CLI-039
        result = runner.invoke(app, ["session-contracts", "--strict"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            format=None,
            missing_only=False,
            summary_only=False,
            strict=True,
        )


@pytest.mark.unit
class TestSessionContractHealthGateCommand:
    """Tests for `session-contract-health-gate` and `govern health-gate`."""

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-040
        result = runner.invoke(app, ["session-contract-health-gate"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_all_sessions(self, mock_cmd) -> None:
        # @trace FR-CLI-041
        result = runner.invoke(app, ["session-contract-health-gate", "--all"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=True,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_strict(self, mock_cmd) -> None:
        # @trace FR-CLI-042
        result = runner.invoke(app, ["session-contract-health-gate", "--strict"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=True,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_min_healthy(self, mock_cmd) -> None:
        # @trace FR-CLI-043
        result = runner.invoke(app, ["session-contract-health-gate", "--min-healthy", "0.8"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=0.8,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_policy_profile(self, mock_cmd) -> None:
        # @trace FR-CLI-044
        result = runner.invoke(app, ["session-contract-health-gate", "--policy-profile", "strict_ci"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile="strict_ci",
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_no_worse_than_baseline(self, mock_cmd) -> None:
        # @trace FR-CLI-045
        result = runner.invoke(app, ["session-contract-health-gate", "--no-worse-than-baseline"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=True,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_regression_tolerance(self, mock_cmd) -> None:
        # @trace FR-CLI-046
        result = runner.invoke(app, ["session-contract-health-gate", "--regression-tolerance", "0.05"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.05,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_output(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-047
        out = tmp_path / "gate.json"
        result = runner.invoke(app, ["session-contract-health-gate", "--output", str(out)])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        call_kwargs = mock_cmd.call_args[1]
        assert call_kwargs["output"] == out

    @patch("thegent.main.session_contract_health_gate_cmd")
    def test_health_gate_export_format(self, mock_cmd) -> None:
        # @trace FR-CLI-048
        result = runner.invoke(app, ["session-contract-health-gate", "--export-format", "csv"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            min_healthy_ratio=1.0,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format="csv",
            overwrite=False,
        )


@pytest.mark.unit
class TestSessionContractHealthReportCommand:
    """Tests for `session-contract-health-report` and `govern health-report`."""

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-049
        result = runner.invoke(app, ["session-contract-health-report"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            top_blocked=25,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_all_sessions(self, mock_cmd) -> None:
        # @trace FR-CLI-050
        result = runner.invoke(app, ["session-contract-health-report", "--all"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=True,
            owner=None,
            strict=False,
            format=None,
            top_blocked=25,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_strict(self, mock_cmd) -> None:
        # @trace FR-CLI-051
        result = runner.invoke(app, ["session-contract-health-report", "--strict"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=True,
            format=None,
            top_blocked=25,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_top_blocked(self, mock_cmd) -> None:
        # @trace FR-CLI-052
        result = runner.invoke(app, ["session-contract-health-report", "--top-blocked", "10"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            top_blocked=10,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_policy_profile(self, mock_cmd) -> None:
        # @trace FR-CLI-053
        result = runner.invoke(app, ["session-contract-health-report", "--policy-profile", "prod_release"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            top_blocked=25,
            policy_profile="prod_release",
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_output(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-054
        out = tmp_path / "report.md"
        result = runner.invoke(app, ["session-contract-health-report", "--output", str(out)])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        call_kwargs = mock_cmd.call_args[1]
        assert call_kwargs["output"] == out

    @patch("thegent.main.session_contract_health_report_cmd")
    def test_health_report_export_format(self, mock_cmd) -> None:
        # @trace FR-CLI-055
        result = runner.invoke(app, ["session-contract-health-report", "--export-format", "jsonl"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            all_sessions=False,
            owner=None,
            strict=False,
            format=None,
            top_blocked=25,
            policy_profile=None,
            no_worse_than_baseline=False,
            regression_tolerance=0.0,
            output=None,
            export_format="jsonl",
            overwrite=False,
        )


@pytest.mark.unit
class TestSessionContractHealthTrendCommand:
    """Tests for `session-contract-health-trend` and `govern health-trend`."""

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-056
        result = runner.invoke(app, ["session-contract-health-trend"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_report",
            all_sessions=False,
            owner=None,
            strict=False,
            policy_profile=None,
            min_healthy_ratio=1.0,
            top_blocked=25,
            limit=20,
            format=None,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_payload_type(self, mock_cmd) -> None:
        # @trace FR-CLI-057
        result = runner.invoke(
            app,
            [
                "session-contract-health-trend",
                "--payload-type",
                "session_contract_health_gate",
            ],
        )
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_gate",
            all_sessions=False,
            owner=None,
            strict=False,
            policy_profile=None,
            min_healthy_ratio=1.0,
            top_blocked=25,
            limit=20,
            format=None,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_all_sessions(self, mock_cmd) -> None:
        # @trace FR-CLI-058
        result = runner.invoke(app, ["session-contract-health-trend", "--all"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_report",
            all_sessions=True,
            owner=None,
            strict=False,
            policy_profile=None,
            min_healthy_ratio=1.0,
            top_blocked=25,
            limit=20,
            format=None,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-059
        result = runner.invoke(app, ["session-contract-health-trend", "--limit", "5"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_report",
            all_sessions=False,
            owner=None,
            strict=False,
            policy_profile=None,
            min_healthy_ratio=1.0,
            top_blocked=25,
            limit=5,
            format=None,
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_format(self, mock_cmd) -> None:
        # @trace FR-CLI-060
        result = runner.invoke(app, ["session-contract-health-trend", "--format", "md"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_report",
            all_sessions=False,
            owner=None,
            strict=False,
            policy_profile=None,
            min_healthy_ratio=1.0,
            top_blocked=25,
            limit=20,
            format="md",
            output=None,
            export_format=None,
            overwrite=False,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_health_trend_output(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-031
        out = tmp_path / "trend.json"
        result = runner.invoke(app, ["session-contract-health-trend", "--output", str(out)])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        call_kwargs = mock_cmd.call_args[1]
        assert call_kwargs["output"] == out

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_govern_health_trend_alias(self, mock_cmd) -> None:
        # @trace FR-CLI-032
        result = runner.invoke(app, ["govern", "health-trend"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
