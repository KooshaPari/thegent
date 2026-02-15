"""Unit tests for CLI DAG and plan-analyze commands."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.unit
class TestDagListCommand:
    """Tests for `dag list`."""

    @patch("thegent.main.dag_list_cmd")
    def test_dag_list_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-010
        result = runner.invoke(app, ["dag", "list"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format=None)

    @patch("thegent.main.dag_list_cmd")
    def test_dag_list_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-010
        result = runner.invoke(app, ["dag", "list", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        call_kwargs = mock_cmd.call_args
        assert call_kwargs.kwargs["cd"] == tmp_path

    @patch("thegent.main.dag_list_cmd")
    def test_dag_list_format_rich(self, mock_cmd) -> None:
        # @trace FR-CLI-010
        result = runner.invoke(app, ["dag", "list", "--format", "rich"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="rich")

    @patch("thegent.main.dag_list_cmd")
    def test_dag_list_format_md(self, mock_cmd) -> None:
        # @trace FR-CLI-010
        result = runner.invoke(app, ["dag", "list", "--format", "md"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="md")


@pytest.mark.unit
class TestDagValidateCommand:
    """Tests for `dag validate`."""

    @patch("thegent.main.dag_validate_cmd")
    def test_dag_validate_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-011
        result = runner.invoke(app, ["dag", "validate"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None)

    @patch("thegent.main.dag_validate_cmd")
    def test_dag_validate_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-011
        result = runner.invoke(app, ["dag", "validate", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagAddCommand:
    """Tests for `dag add`."""

    @patch("thegent.main.dag_add_cmd")
    def test_dag_add_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(app, ["dag", "add", "QA-A1", "claude", "Run tests"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            task_id="QA-A1",
            agent="claude",
            prompt="Run tests",
            cd=None,
            depends_on=None,
            contract_version=None,
        )

    @patch("thegent.main.dag_add_cmd")
    def test_dag_add_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(app, ["dag", "add", "QA-A2", "codex", "Lint code", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        call_kw = mock_cmd.call_args.kwargs
        assert call_kw["task_id"] == "QA-A2"
        assert call_kw["agent"] == "codex"
        assert call_kw["cd"] == tmp_path

    @patch("thegent.main.dag_add_cmd")
    def test_dag_add_with_depends_on(self, mock_cmd) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(
            app,
            ["dag", "add", "QA-A3", "claude", "Build", "--depends-on", "QA-A1,QA-A2"],
        )
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["depends_on"] == "QA-A1,QA-A2"

    @patch("thegent.main.dag_add_cmd")
    def test_dag_add_with_contract_version(self, mock_cmd) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(
            app,
            ["dag", "add", "QA-A4", "gemini", "Deploy", "--contract-version", "csm-v1"],
        )
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["contract_version"] == "csm-v1"

    def test_dag_add_missing_args(self) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(app, ["dag", "add"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestDagUpdateCommand:
    """Tests for `dag update`."""

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_status(self, mock_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update", "QA-A1", "--status", "done"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            task_id="QA-A1",
            cd=None,
            status="done",
            prompt=None,
            agent=None,
            depends_on=None,
            contract_version=None,
        )

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_prompt(self, mock_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update", "QA-A1", "--prompt", "New prompt text"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["prompt"] == "New prompt text"

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_agent(self, mock_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update", "QA-A1", "--agent", "codex"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["agent"] == "codex"

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_depends_on(self, mock_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update", "QA-A1", "--depends-on", "QA-A0"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["depends_on"] == "QA-A0"

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_contract_version(self, mock_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update", "QA-A1", "--contract-version", "csm-v2"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["contract_version"] == "csm-v2"

    @patch("thegent.main.dag_update_cmd")
    def test_dag_update_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(
            app,
            ["dag", "update", "QA-A1", "--status", "running", "--cd", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path

    def test_dag_update_missing_task_id(self) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["dag", "update"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestDagRemoveCommand:
    """Tests for `dag remove`."""

    @patch("thegent.main.dag_remove_cmd")
    def test_dag_remove_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-014
        result = runner.invoke(app, ["dag", "remove", "QA-A1"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(task_id="QA-A1", cd=None)

    @patch("thegent.main.dag_remove_cmd")
    def test_dag_remove_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-014
        result = runner.invoke(app, ["dag", "remove", "QA-A1", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path

    def test_dag_remove_missing_task_id(self) -> None:
        # @trace FR-CLI-014
        result = runner.invoke(app, ["dag", "remove"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestDagCancelCommand:
    """Tests for `dag cancel`."""

    @patch("thegent.main.dag_cancel_cmd")
    def test_dag_cancel_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-015
        result = runner.invoke(app, ["dag", "cancel", "QA-A1"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(task_id="QA-A1", cd=None)

    @patch("thegent.main.dag_cancel_cmd")
    def test_dag_cancel_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-015
        result = runner.invoke(app, ["dag", "cancel", "QA-A1", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagReadyCommand:
    """Tests for `dag ready`."""

    @patch("thegent.main.dag_ready_cmd")
    def test_dag_ready_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-016
        result = runner.invoke(app, ["dag", "ready"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format=None)

    @patch("thegent.main.dag_ready_cmd")
    def test_dag_ready_with_format_rich(self, mock_cmd) -> None:
        # @trace FR-CLI-016
        result = runner.invoke(app, ["dag", "ready", "--format", "rich"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="rich")

    @patch("thegent.main.dag_ready_cmd")
    def test_dag_ready_with_format_md(self, mock_cmd) -> None:
        # @trace FR-CLI-016
        result = runner.invoke(app, ["dag", "ready", "--format", "md"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="md")

    @patch("thegent.main.dag_ready_cmd")
    def test_dag_ready_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-016
        result = runner.invoke(app, ["dag", "ready", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagRunCommand:
    """Tests for `dag run`."""

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            cd=None,
            dry_run=False,
            task=None,
            max_parallel=None,
            lane=None,
            check_drift=False,
            contract_version=None,
        )

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_dry_run(self, mock_cmd) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run", "--dry-run"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["dry_run"] is True

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_with_task(self, mock_cmd) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run", "--task", "QA-A1"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["task"] == "QA-A1"

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_max_parallel(self, mock_cmd) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run", "--max-parallel", "4"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["max_parallel"] == 4

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_with_lane(self, mock_cmd) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run", "--lane", "critical"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["lane"] == "critical"

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_check_drift(self, mock_cmd) -> None:
        # @trace FR-CLI-018
        result = runner.invoke(app, ["dag", "run", "--check-drift"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["check_drift"] is True

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_contract_version(self, mock_cmd) -> None:
        # @trace FR-CLI-018
        result = runner.invoke(app, ["dag", "run", "--contract-version", "csm-v1"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["contract_version"] == "csm-v1"

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-017
        result = runner.invoke(app, ["dag", "run", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path

    @patch("thegent.main.dag_run_cmd")
    def test_dag_run_combined_flags(self, mock_cmd) -> None:
        # @trace FR-CLI-018
        result = runner.invoke(
            app,
            [
                "dag",
                "run",
                "--dry-run",
                "--task",
                "QA-B1",
                "--max-parallel",
                "2",
                "--lane",
                "recovery",
                "--check-drift",
                "--contract-version",
                "csm-v2",
            ],
        )
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["dry_run"] is True
        assert kw["task"] == "QA-B1"
        assert kw["max_parallel"] == 2
        assert kw["lane"] == "recovery"
        assert kw["check_drift"] is True
        assert kw["contract_version"] == "csm-v2"


@pytest.mark.unit
class TestDagStatusCommand:
    """Tests for `dag status`."""

    @patch("thegent.main.dag_status_cmd")
    def test_dag_status_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-019
        result = runner.invoke(app, ["dag", "status"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format=None)

    @patch("thegent.main.dag_status_cmd")
    def test_dag_status_with_format_rich(self, mock_cmd) -> None:
        # @trace FR-CLI-019
        result = runner.invoke(app, ["dag", "status", "--format", "rich"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="rich")

    @patch("thegent.main.dag_status_cmd")
    def test_dag_status_with_format_md(self, mock_cmd) -> None:
        # @trace FR-CLI-019
        result = runner.invoke(app, ["dag", "status", "--format", "md"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, format="md")

    @patch("thegent.main.dag_status_cmd")
    def test_dag_status_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-019
        result = runner.invoke(app, ["dag", "status", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagSyncCommand:
    """Tests for `dag sync` (non-watch mode only)."""

    @patch("thegent.main.dag_sync_cmd")
    def test_dag_sync_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-020
        result = runner.invoke(app, ["dag", "sync"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None)

    @patch("thegent.main.dag_sync_cmd")
    def test_dag_sync_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-020
        result = runner.invoke(app, ["dag", "sync", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagReconcileCommand:
    """Tests for `dag reconcile`."""

    @patch("thegent.main.dag_reconcile_cmd")
    def test_dag_reconcile_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-021
        result = runner.invoke(app, ["dag", "reconcile"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None)

    @patch("thegent.main.dag_reconcile_cmd")
    def test_dag_reconcile_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-021
        result = runner.invoke(app, ["dag", "reconcile", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestDagCheckpointCommand:
    """Tests for `dag checkpoint`."""

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_dag_checkpoint_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-022
        result = runner.invoke(app, ["dag", "checkpoint"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, reason="Manual checkpoint")

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_dag_checkpoint_with_reason(self, mock_cmd) -> None:
        # @trace FR-CLI-022
        result = runner.invoke(app, ["dag", "checkpoint", "--reason", "Before deploy"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, reason="Before deploy")

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_dag_checkpoint_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-022
        result = runner.invoke(app, ["dag", "checkpoint", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path

    @patch("thegent.main.dag_checkpoint_cmd")
    def test_dag_checkpoint_with_cd_and_reason(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-022
        result = runner.invoke(
            app,
            ["dag", "checkpoint", "--cd", str(tmp_path), "--reason", "Pre-release"],
        )
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["cd"] == tmp_path
        assert kw["reason"] == "Pre-release"


@pytest.mark.unit
class TestDagRollbackCommand:
    """Tests for `dag rollback`."""

    @patch("thegent.main.dag_rollback_cmd")
    def test_dag_rollback_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-023
        result = runner.invoke(app, ["dag", "rollback", "chk-001"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(checkpoint_id="chk-001", cd=None)

    @patch("thegent.main.dag_rollback_cmd")
    def test_dag_rollback_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-023
        result = runner.invoke(app, ["dag", "rollback", "chk-002", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["checkpoint_id"] == "chk-002"
        assert kw["cd"] == tmp_path

    def test_dag_rollback_missing_checkpoint_id(self) -> None:
        # @trace FR-CLI-023
        result = runner.invoke(app, ["dag", "rollback"])
        assert result.exit_code != 0


@pytest.mark.unit
class TestDagCheckpointsCommand:
    """Tests for `dag checkpoints`."""

    @patch("thegent.main.dag_checkpoints_cmd")
    def test_dag_checkpoints_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-024
        result = runner.invoke(app, ["dag", "checkpoints"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(limit=20)

    @patch("thegent.main.dag_checkpoints_cmd")
    def test_dag_checkpoints_with_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-024
        result = runner.invoke(app, ["dag", "checkpoints", "--limit", "5"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(limit=5)

    @patch("thegent.main.dag_checkpoints_cmd")
    def test_dag_checkpoints_with_large_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-024
        result = runner.invoke(app, ["dag", "checkpoints", "--limit", "100"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(limit=100)


@pytest.mark.unit
class TestDagRecoverCommand:
    """Tests for `dag recover`."""

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover_default_action(self, mock_cmd) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["dag", "recover"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, action="retry-failed")

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover_retry_failed(self, mock_cmd) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["dag", "recover", "retry-failed"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, action="retry-failed")

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover_clear_stuck(self, mock_cmd) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["dag", "recover", "clear-stuck"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, action="clear-stuck")

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover_reset_retries(self, mock_cmd) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["dag", "recover", "reset-retries"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, action="reset-retries")

    @patch("thegent.main.dag_recover_cmd")
    def test_dag_recover_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["dag", "recover", "retry-failed", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["action"] == "retry-failed"
        assert kw["cd"] == tmp_path


@pytest.mark.unit
class TestDagProbeCommand:
    """Tests for `dag probe`."""

    @patch("thegent.main.dag_probe_cmd")
    def test_dag_probe_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-026
        result = runner.invoke(app, ["dag", "probe"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, baseline_id=None)

    @patch("thegent.main.dag_probe_cmd")
    def test_dag_probe_with_baseline_id(self, mock_cmd) -> None:
        # @trace FR-CLI-026
        result = runner.invoke(app, ["dag", "probe", "--baseline-id", "chk-abc"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, baseline_id="chk-abc")

    @patch("thegent.main.dag_probe_cmd")
    def test_dag_probe_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-026
        result = runner.invoke(app, ["dag", "probe", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["cd"] == tmp_path

    @patch("thegent.main.dag_probe_cmd")
    def test_dag_probe_with_cd_and_baseline(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-026
        result = runner.invoke(
            app,
            ["dag", "probe", "--cd", str(tmp_path), "--baseline-id", "chk-xyz"],
        )
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["cd"] == tmp_path
        assert kw["baseline_id"] == "chk-xyz"


@pytest.mark.unit
class TestPlanAnalyzeCommand:
    """Tests for `plan analyze`."""

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-027
        result = runner.invoke(app, ["plan", "analyze"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, pert=False, resources=False, continuity=False, format=None)

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_pert(self, mock_cmd) -> None:
        # @trace FR-CLI-027
        result = runner.invoke(app, ["plan", "analyze", "--pert"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["pert"] is True

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_resources(self, mock_cmd) -> None:
        # @trace FR-CLI-028
        result = runner.invoke(app, ["plan", "analyze", "--resources"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["resources"] is True

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_continuity(self, mock_cmd) -> None:
        # @trace FR-CLI-028
        result = runner.invoke(app, ["plan", "analyze", "--continuity"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["continuity"] is True

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_format_json(self, mock_cmd) -> None:
        # @trace FR-CLI-029
        result = runner.invoke(app, ["plan", "analyze", "--format", "json"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None, pert=False, resources=False, continuity=False, format="json")

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_format_rich(self, mock_cmd) -> None:
        # @trace FR-CLI-029
        result = runner.invoke(app, ["plan", "analyze", "--format", "rich"])
        assert result.exit_code == 0
        assert mock_cmd.call_args.kwargs["format"] == "rich"

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_all_overlays(self, mock_cmd) -> None:
        # @trace FR-CLI-030
        result = runner.invoke(app, ["plan", "analyze", "--pert", "--resources", "--continuity"])
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["pert"] is True
        assert kw["resources"] is True
        assert kw["continuity"] is True

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-030
        result = runner.invoke(app, ["plan", "analyze", "--cd", str(tmp_path), "--pert"])
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["cd"] == tmp_path
        assert kw["pert"] is True

    @patch("thegent.main.plan_analyze_cmd")
    def test_plan_analyze_all_overlays_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-030
        result = runner.invoke(
            app,
            [
                "plan",
                "analyze",
                "--pert",
                "--resources",
                "--continuity",
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        kw = mock_cmd.call_args.kwargs
        assert kw["pert"] is True
        assert kw["resources"] is True
        assert kw["continuity"] is True
        assert kw["format"] == "json"
