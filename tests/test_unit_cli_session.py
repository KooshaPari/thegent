"""Unit tests for CLI session commands (run, bg, ps, status, inspect, logs, wait, stop, pause, resume)."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.unit
class TestRunCommand:
    """Tests for the `run` CLI command."""

    @patch("thegent.main.run_cmd")
    def test_run_basic(self, mock_run_cmd) -> None:
        # @trace FR-CLI-001
        result = runner.invoke(app, ["run", "hello world", "claude"])
        assert result.exit_code == 0
        mock_run_cmd.assert_called_once()
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["prompt"] == "hello world"
        assert kwargs["agent"] == "claude"

    @patch("thegent.main.run_cmd")
    def test_run_with_model(self, mock_run_cmd) -> None:
        # @trace FR-CLI-002
        result = runner.invoke(app, ["run", "do stuff", "claude", "--model", "gpt-4"])
        assert result.exit_code == 0
        mock_run_cmd.assert_called_once()
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["model"] == "gpt-4"

    @patch("thegent.main.run_cmd")
    def test_run_with_provider(self, mock_run_cmd) -> None:
        # @trace FR-CLI-003
        result = runner.invoke(app, ["run", "task", "claude", "--provider", "openai"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["provider"] == "openai"

    @patch("thegent.main.run_cmd")
    def test_run_with_cd(self, mock_run_cmd, tmp_path) -> None:
        # @trace FR-CLI-004
        result = runner.invoke(app, ["run", "task", "claude", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["cd"] == tmp_path

    @patch("thegent.main.run_cmd")
    def test_run_with_mode(self, mock_run_cmd) -> None:
        # @trace FR-CLI-005
        result = runner.invoke(app, ["run", "task", "claude", "--mode", "read-only"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["mode"] == "read-only"

    @patch("thegent.main.run_cmd")
    def test_run_with_timeout(self, mock_run_cmd) -> None:
        # @trace FR-CLI-006
        result = runner.invoke(app, ["run", "task", "claude", "--timeout", "120"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["timeout"] == 120

    @patch("thegent.main.run_cmd")
    def test_run_with_live(self, mock_run_cmd) -> None:
        # @trace FR-CLI-007
        result = runner.invoke(app, ["run", "task", "claude", "--live"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["live"] is True

    @patch("thegent.main.run_cmd")
    def test_run_with_failover(self, mock_run_cmd) -> None:
        # @trace FR-CLI-008
        result = runner.invoke(app, ["run", "task", "claude", "--failover"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["failover"] is True

    @patch("thegent.main.run_cmd")
    def test_run_with_routing(self, mock_run_cmd) -> None:
        # @trace FR-CLI-009
        result = runner.invoke(app, ["run", "task", "claude", "--routing", "prefer_proxy"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["routing"] == "prefer_proxy"

    @patch("thegent.main.run_cmd")
    def test_run_with_include_contract(self, mock_run_cmd) -> None:
        # @trace FR-CLI-010
        result = runner.invoke(app, ["run", "task", "claude", "--include-contract"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["include_contract"] is True

    @patch("thegent.main.run_cmd")
    def test_run_with_lane(self, mock_run_cmd) -> None:
        # @trace FR-CLI-011
        result = runner.invoke(app, ["run", "task", "claude", "--lane", "critical"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["lane"] == "critical"

    @patch("thegent.main.run_cmd")
    def test_run_with_confidence(self, mock_run_cmd) -> None:
        # @trace FR-CLI-012
        result = runner.invoke(app, ["run", "task", "claude", "--confidence", "0.85"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["confidence"] == 0.85

    @patch("thegent.main.run_cmd")
    def test_run_with_override(self, mock_run_cmd) -> None:
        # @trace FR-CLI-013
        result = runner.invoke(app, ["run", "task", "claude", "--override", "emergency"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["override_reason"] == "emergency"

    @patch("thegent.main.run_cmd")
    def test_run_with_domain(self, mock_run_cmd) -> None:
        # @trace FR-CLI-014
        result = runner.invoke(app, ["run", "task", "claude", "--domain", "finance"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["domain"] == "finance"

    @patch("thegent.main.run_cmd")
    def test_run_defaults(self, mock_run_cmd) -> None:
        # @trace FR-CLI-015
        result = runner.invoke(app, ["run", "task", "claude"])
        assert result.exit_code == 0
        kwargs = mock_run_cmd.call_args.kwargs
        assert kwargs["mode"] == "write"
        assert kwargs["timeout"] == 90
        assert kwargs["full"] is False
        assert kwargs["live"] is False
        assert kwargs["failover"] is False
        assert kwargs["include_contract"] is False
        assert kwargs["lane"] == "standard"
        assert kwargs["model"] is None
        assert kwargs["provider"] is None
        assert kwargs["routing"] is None
        assert kwargs["confidence"] is None
        assert kwargs["domain"] is None


@pytest.mark.unit
class TestBgCommand:
    """Tests for the `bg` CLI command."""

    @patch("thegent.main.bg_cmd")
    def test_bg_basic(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-020
        result = runner.invoke(app, ["bg", "do stuff", "claude"])
        assert result.exit_code == 0
        mock_bg_cmd.assert_called_once()
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["prompt"] == "do stuff"
        assert kwargs["agent"] == "claude"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_owner(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-021
        result = runner.invoke(app, ["bg", "task", "claude", "--owner", "alice:proj"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["owner"] == "alice:proj"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_model(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-022
        result = runner.invoke(app, ["bg", "task", "claude", "--model", "o1"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["model"] == "o1"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_continuation(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-023
        result = runner.invoke(app, ["bg", "continue", "claude", "--continuation", "sess-abc"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["continue_from"] == "sess-abc"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_idempotency_token(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-024
        result = runner.invoke(app, ["bg", "task", "claude", "--idempotency-token", "tok-123"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["idempotency_token"] == "tok-123"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_arbitration(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-025
        result = runner.invoke(app, ["bg", "task", "claude", "--arbitration", "leader"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["arbitration"] == "leader"

    @patch("thegent.main.bg_cmd")
    def test_bg_with_format(self, mock_bg_cmd) -> None:
        # @trace FR-CLI-026
        result = runner.invoke(app, ["bg", "task", "claude", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_bg_cmd.call_args.kwargs
        assert kwargs["output_format"] == "json"


@pytest.mark.unit
class TestPsCommand:
    """Tests for the `ps` CLI command."""

    @patch("thegent.main.ps_cmd")
    def test_ps_basic(self, mock_ps_cmd) -> None:
        # @trace FR-CLI-030
        result = runner.invoke(app, ["ps"])
        assert result.exit_code == 0
        mock_ps_cmd.assert_called_once()

    @patch("thegent.main.ps_cmd")
    def test_ps_with_all(self, mock_ps_cmd) -> None:
        # @trace FR-CLI-031
        result = runner.invoke(app, ["ps", "--all"])
        assert result.exit_code == 0
        kwargs = mock_ps_cmd.call_args.kwargs
        assert kwargs["all_sessions"] is True

    @patch("thegent.main.ps_cmd")
    def test_ps_with_owner(self, mock_ps_cmd) -> None:
        # @trace FR-CLI-032
        result = runner.invoke(app, ["ps", "--owner", "bob:myproj"])
        assert result.exit_code == 0
        kwargs = mock_ps_cmd.call_args.kwargs
        assert kwargs["owner"] == "bob:myproj"

    @patch("thegent.main.ps_cmd")
    def test_ps_with_format(self, mock_ps_cmd) -> None:
        # @trace FR-CLI-033
        result = runner.invoke(app, ["ps", "--format", "md"])
        assert result.exit_code == 0
        kwargs = mock_ps_cmd.call_args.kwargs
        assert kwargs["format"] == "md"

    @patch("thegent.main.ps_cmd")
    def test_ps_with_include_contract(self, mock_ps_cmd) -> None:
        # @trace FR-CLI-034
        result = runner.invoke(app, ["ps", "--include-contract"])
        assert result.exit_code == 0
        kwargs = mock_ps_cmd.call_args.kwargs
        assert kwargs["include_contract"] is True


@pytest.mark.unit
class TestStatusCommand:
    """Tests for the `status` CLI command."""

    @patch("thegent.main.status_cmd")
    def test_status_basic(self, mock_status_cmd) -> None:
        # @trace FR-CLI-040
        result = runner.invoke(app, ["status", "sess-123"])
        assert result.exit_code == 0
        mock_status_cmd.assert_called_once()
        kwargs = mock_status_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-123"

    @patch("thegent.main.status_cmd")
    def test_status_with_format(self, mock_status_cmd) -> None:
        # @trace FR-CLI-041
        result = runner.invoke(app, ["status", "sess-123", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_status_cmd.call_args.kwargs
        assert kwargs["format"] == "json"

    @patch("thegent.main.status_cmd")
    def test_status_with_include_contract(self, mock_status_cmd) -> None:
        # @trace FR-CLI-042
        result = runner.invoke(app, ["status", "sess-123", "--include-contract"])
        assert result.exit_code == 0
        kwargs = mock_status_cmd.call_args.kwargs
        assert kwargs["include_contract"] is True


@pytest.mark.unit
class TestInspectCommand:
    """Tests for the `inspect` CLI command."""

    @patch("thegent.main.inspect_cmd")
    def test_inspect_basic(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-050
        result = runner.invoke(app, ["inspect", "sess-abc"])
        assert result.exit_code == 0
        mock_inspect_cmd.assert_called_once()
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert "sess-abc" in kwargs["session_ids"]

    @patch("thegent.main.inspect_cmd")
    def test_inspect_multiple_sessions(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-051
        result = runner.invoke(app, ["inspect", "sess-1", "sess-2"])
        assert result.exit_code == 0
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert kwargs["session_ids"] == ["sess-1", "sess-2"]

    @patch("thegent.main.inspect_cmd")
    def test_inspect_with_owner(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-052
        result = runner.invoke(app, ["inspect", "--owner", "alice:proj"])
        assert result.exit_code == 0
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert kwargs["owner"] == "alice:proj"

    @patch("thegent.main.inspect_cmd")
    def test_inspect_with_tail(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-053
        result = runner.invoke(app, ["inspect", "sess-abc", "--tail", "100"])
        assert result.exit_code == 0
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert kwargs["tail"] == 100

    @patch("thegent.main.inspect_cmd")
    def test_inspect_with_stderr(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-054
        result = runner.invoke(app, ["inspect", "sess-abc", "--stderr"])
        assert result.exit_code == 0
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert kwargs["stderr"] is True

    @patch("thegent.main.inspect_cmd")
    def test_inspect_with_format(self, mock_inspect_cmd) -> None:
        # @trace FR-CLI-055
        result = runner.invoke(app, ["inspect", "sess-abc", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_inspect_cmd.call_args.kwargs
        assert kwargs["format"] == "json"


@pytest.mark.unit
class TestLogsCommand:
    """Tests for the `logs` CLI command."""

    @patch("thegent.main.logs_cmd")
    def test_logs_basic(self, mock_logs_cmd) -> None:
        # @trace FR-CLI-060
        result = runner.invoke(app, ["logs", "sess-xyz"])
        assert result.exit_code == 0
        mock_logs_cmd.assert_called_once()
        kwargs = mock_logs_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-xyz"

    @patch("thegent.main.logs_cmd")
    def test_logs_with_follow(self, mock_logs_cmd) -> None:
        # @trace FR-CLI-061
        result = runner.invoke(app, ["logs", "sess-xyz", "--follow"])
        assert result.exit_code == 0
        kwargs = mock_logs_cmd.call_args.kwargs
        assert kwargs["follow"] is True

    @patch("thegent.main.logs_cmd")
    def test_logs_with_stderr(self, mock_logs_cmd) -> None:
        # @trace FR-CLI-062
        result = runner.invoke(app, ["logs", "sess-xyz", "--stderr"])
        assert result.exit_code == 0
        kwargs = mock_logs_cmd.call_args.kwargs
        assert kwargs["stderr"] is True

    @patch("thegent.main.logs_cmd")
    def test_logs_with_tail(self, mock_logs_cmd) -> None:
        # @trace FR-CLI-063
        result = runner.invoke(app, ["logs", "sess-xyz", "--tail", "50"])
        assert result.exit_code == 0
        kwargs = mock_logs_cmd.call_args.kwargs
        assert kwargs["tail"] == 50

    @patch("thegent.main.logs_cmd")
    def test_logs_defaults(self, mock_logs_cmd) -> None:
        # @trace FR-CLI-064
        result = runner.invoke(app, ["logs", "sess-xyz"])
        assert result.exit_code == 0
        kwargs = mock_logs_cmd.call_args.kwargs
        assert kwargs["follow"] is False
        assert kwargs["stderr"] is False
        assert kwargs["tail"] == 200
        assert kwargs["timeout"] == 0


@pytest.mark.unit
class TestWaitCommand:
    """Tests for the `wait` CLI command."""

    @patch("thegent.main.wait_cmd")
    def test_wait_basic(self, mock_wait_cmd) -> None:
        # @trace FR-CLI-070
        result = runner.invoke(app, ["wait", "sess-xyz"])
        assert result.exit_code == 0
        mock_wait_cmd.assert_called_once()
        kwargs = mock_wait_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-xyz"
        assert kwargs["timeout"] == 0

    @patch("thegent.main.wait_cmd")
    def test_wait_with_timeout(self, mock_wait_cmd) -> None:
        # @trace FR-CLI-071
        result = runner.invoke(app, ["wait", "sess-xyz", "--timeout", "30"])
        assert result.exit_code == 0
        kwargs = mock_wait_cmd.call_args.kwargs
        assert kwargs["timeout"] == 30


@pytest.mark.unit
class TestStopCommand:
    """Tests for the `stop` CLI command."""

    @patch("thegent.main.stop_cmd")
    def test_stop_basic(self, mock_stop_cmd) -> None:
        # @trace FR-CLI-080
        result = runner.invoke(app, ["stop", "sess-xyz"])
        assert result.exit_code == 0
        mock_stop_cmd.assert_called_once()
        kwargs = mock_stop_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-xyz"
        assert kwargs["force"] is False
        assert kwargs["wind_down"] is False
        assert kwargs["grace"] == 20

    @patch("thegent.main.stop_cmd")
    def test_stop_with_force(self, mock_stop_cmd) -> None:
        # @trace FR-CLI-081
        result = runner.invoke(app, ["stop", "sess-xyz", "--force"])
        assert result.exit_code == 0
        kwargs = mock_stop_cmd.call_args.kwargs
        assert kwargs["force"] is True

    @patch("thegent.main.stop_cmd")
    def test_stop_with_wind_down(self, mock_stop_cmd) -> None:
        # @trace FR-CLI-082
        result = runner.invoke(app, ["stop", "sess-xyz", "--wind-down"])
        assert result.exit_code == 0
        kwargs = mock_stop_cmd.call_args.kwargs
        assert kwargs["wind_down"] is True

    @patch("thegent.main.stop_cmd")
    def test_stop_with_grace(self, mock_stop_cmd) -> None:
        # @trace FR-CLI-083
        result = runner.invoke(app, ["stop", "sess-xyz", "--grace", "60"])
        assert result.exit_code == 0
        kwargs = mock_stop_cmd.call_args.kwargs
        assert kwargs["grace"] == 60


@pytest.mark.unit
class TestPauseCommand:
    """Tests for the `pause` CLI command."""

    @patch("thegent.main.pause_cmd")
    def test_pause_basic(self, mock_pause_cmd) -> None:
        # @trace FR-CLI-090
        result = runner.invoke(app, ["pause", "sess-xyz"])
        assert result.exit_code == 0
        mock_pause_cmd.assert_called_once()
        kwargs = mock_pause_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-xyz"


@pytest.mark.unit
class TestResumeCommand:
    """Tests for the `resume` CLI command."""

    @patch("thegent.main.resume_cmd")
    def test_resume_basic(self, mock_resume_cmd) -> None:
        # @trace FR-CLI-100
        result = runner.invoke(app, ["resume", "sess-xyz"])
        assert result.exit_code == 0
        mock_resume_cmd.assert_called_once()
        kwargs = mock_resume_cmd.call_args.kwargs
        assert kwargs["session_id"] == "sess-xyz"
