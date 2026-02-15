"""Unit tests for CLI OBSERVE, MODELS, and miscellaneous commands.

Tests CLI argument parsing and delegation to underlying *_cmd functions.
Each test mocks the underlying implementation to isolate Typer argument wiring.

For functions imported at the TOP of thegent/main.py (e.g. drift_cmd, cockpit_cmd),
the patch target is ``thegent.main.<func>`` because the name is already bound in
that module namespace at import time.

For functions imported INLINE inside a command body (e.g. observe_summary_cmd),
the patch target is the source module (``thegent.cli.<func>``) because the import
executes at call time.
"""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# OBSERVE commands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestObserveSummary:
    """Tests for ``observe summary`` CLI command.

    ``observe_summary_cmd`` is imported inline in the command body, so we
    patch at ``thegent.cli.observe_summary_cmd``.
    """

    @patch("thegent.cli.observe_summary_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-061
        result = runner.invoke(app, ["observe", "summary"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            limit=500,
            drift_window=50,
            structural_budget=5.0,
            semantic_budget=10.0,
            provider=None,
            trend_samples=0,
            top_escalations=10,
            format=None,
        )

    @patch("thegent.cli.observe_summary_cmd")
    def test_with_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-062
        result = runner.invoke(app, ["observe", "summary", "--limit", "100"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()
        kwargs = mock_cmd.call_args[1]
        assert kwargs["limit"] == 100

    @patch("thegent.cli.observe_summary_cmd")
    def test_with_drift_window(self, mock_cmd) -> None:
        # @trace FR-CLI-063
        result = runner.invoke(app, ["observe", "summary", "--drift-window", "25"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["drift_window"] == 25

    @patch("thegent.cli.observe_summary_cmd")
    def test_with_provider(self, mock_cmd) -> None:
        # @trace FR-CLI-064
        result = runner.invoke(app, ["observe", "summary", "--provider", "gemini"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["provider"] == "gemini"

    @patch("thegent.cli.observe_summary_cmd")
    def test_with_trend_samples(self, mock_cmd) -> None:
        # @trace FR-CLI-065
        result = runner.invoke(app, ["observe", "summary", "--trend-samples", "5"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["trend_samples"] == 5

    @patch("thegent.cli.observe_summary_cmd")
    def test_with_format_json(self, mock_cmd) -> None:
        # @trace FR-CLI-066
        result = runner.invoke(app, ["observe", "summary", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["format"] == "json"


@pytest.mark.unit
class TestObserveKpis:
    """Tests for ``observe kpis`` CLI command (inline imports)."""

    @patch("thegent.contracts.telemetry.ContractTelemetry")
    @patch("thegent.config.ThegentSettings")
    def test_basic(self, mock_settings, mock_ct) -> None:
        # @trace FR-CLI-067
        mock_settings.return_value.session_dir = "/tmp/fake-sessions"
        mock_instance = MagicMock()
        mock_instance.get_fallback_kpis.return_value = {
            "total": 0,
            "fallback_rate": 0.0,
            "success_rate": 1.0,
            "avg_confidence": 0.0,
            "structural_drift_pct": 0.0,
            "semantic_drift_pct": 0.0,
            "by_provider": {},
        }
        mock_ct.return_value = mock_instance
        result = runner.invoke(app, ["observe", "kpis"])
        assert result.exit_code == 0
        mock_instance.get_fallback_kpis.assert_called_once_with(limit=500)

    @patch("thegent.contracts.telemetry.ContractTelemetry")
    @patch("thegent.config.ThegentSettings")
    def test_with_limit(self, mock_settings, mock_ct) -> None:
        # @trace FR-CLI-068
        mock_settings.return_value.session_dir = "/tmp/fake-sessions"
        mock_instance = MagicMock()
        mock_instance.get_fallback_kpis.return_value = {
            "total": 0,
            "fallback_rate": 0.0,
            "success_rate": 1.0,
            "avg_confidence": 0.0,
            "structural_drift_pct": 0.0,
            "semantic_drift_pct": 0.0,
            "by_provider": {},
        }
        mock_ct.return_value = mock_instance
        result = runner.invoke(app, ["observe", "kpis", "--limit", "200"])
        assert result.exit_code == 0
        mock_instance.get_fallback_kpis.assert_called_once_with(limit=200)

    @patch("thegent.contracts.telemetry.ContractTelemetry")
    @patch("thegent.config.ThegentSettings")
    def test_with_format_json(self, mock_settings, mock_ct) -> None:
        # @trace FR-CLI-069
        mock_settings.return_value.session_dir = "/tmp/fake-sessions"
        mock_instance = MagicMock()
        mock_instance.get_fallback_kpis.return_value = {
            "total": 5,
            "fallback_rate": 0.1,
            "success_rate": 0.9,
            "avg_confidence": 0.85,
            "structural_drift_pct": 1.0,
            "semantic_drift_pct": 2.0,
            "by_provider": {},
        }
        mock_ct.return_value = mock_instance
        result = runner.invoke(app, ["observe", "kpis", "--format", "json"])
        assert result.exit_code == 0
        # Source returns early for JSON format without printing output
        mock_instance.get_fallback_kpis.assert_called_once()


@pytest.mark.unit
class TestObserveDrift:
    """Tests for ``observe drift`` CLI command.

    ``drift_cmd`` is imported at top-level of main.py, so patch at
    ``thegent.main.drift_cmd``.
    """

    @patch("thegent.main.drift_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-070
        result = runner.invoke(app, ["observe", "drift"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            window=50,
            format=None,
            structural_budget=5.0,
            semantic_budget=10.0,
        )

    @patch("thegent.main.drift_cmd")
    def test_with_window(self, mock_cmd) -> None:
        # @trace FR-CLI-071
        result = runner.invoke(app, ["observe", "drift", "--window", "100"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["window"] == 100

    @patch("thegent.main.drift_cmd")
    def test_with_structural_budget(self, mock_cmd) -> None:
        # @trace FR-CLI-072
        result = runner.invoke(app, ["observe", "drift", "--structural-budget", "3.0"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["structural_budget"] == 3.0

    @patch("thegent.main.drift_cmd")
    def test_with_semantic_budget(self, mock_cmd) -> None:
        # @trace FR-CLI-073
        result = runner.invoke(app, ["observe", "drift", "--semantic-budget", "8.0"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["semantic_budget"] == 8.0

    @patch("thegent.main.drift_cmd")
    def test_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-074
        result = runner.invoke(app, ["observe", "drift", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["format"] == "json"


@pytest.mark.unit
class TestObserveTrend:
    """Tests for ``observe trend`` CLI command.

    ``session_contract_health_trend_cmd`` is imported at top-level of main.py.
    """

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-075
        result = runner.invoke(app, ["observe", "trend"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            payload_type="session_contract_health_report",
            all_sessions=False,
            owner=None,
            strict=False,
            limit=20,
            format=None,
        )

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_with_payload_type(self, mock_cmd) -> None:
        # @trace FR-CLI-076
        result = runner.invoke(app, ["observe", "trend", "--payload-type", "session_contract_health_gate"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["payload_type"] == "session_contract_health_gate"

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_with_all(self, mock_cmd) -> None:
        # @trace FR-CLI-077
        result = runner.invoke(app, ["observe", "trend", "--all"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["all_sessions"] is True

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_with_owner(self, mock_cmd) -> None:
        # @trace FR-CLI-078
        result = runner.invoke(app, ["observe", "trend", "--owner", "alice"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["owner"] == "alice"

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_with_limit(self, mock_cmd) -> None:
        # @trace FR-CLI-079
        result = runner.invoke(app, ["observe", "trend", "--limit", "5"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["limit"] == 5

    @patch("thegent.main.session_contract_health_trend_cmd")
    def test_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-080
        result = runner.invoke(app, ["observe", "trend", "--format", "md"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["format"] == "md"


@pytest.mark.unit
class TestCockpit:
    """Tests for ``cockpit`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.cockpit_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-081
        result = runner.invoke(app, ["cockpit"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()


@pytest.mark.unit
class TestFeedback:
    """Tests for ``feedback`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.feedback_cmd")
    def test_with_run_id_and_score(self, mock_cmd) -> None:
        # @trace FR-CLI-082
        result = runner.invoke(app, ["feedback", "run-abc", "0.95"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with("run-abc", 0.95, None)

    @patch("thegent.main.feedback_cmd")
    def test_with_note(self, mock_cmd) -> None:
        # @trace FR-CLI-083
        result = runner.invoke(app, ["feedback", "run-xyz", "0.5", "--note", "needs work"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with("run-xyz", 0.5, "needs work")


@pytest.mark.unit
class TestArchive:
    """Tests for ``archive`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.archive_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-084
        result = runner.invoke(app, ["archive"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(days=None, domain=None, tier=None)

    @patch("thegent.main.archive_cmd")
    def test_with_days(self, mock_cmd) -> None:
        # @trace FR-CLI-085
        result = runner.invoke(app, ["archive", "--days", "7"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["days"] == 7

    @patch("thegent.main.archive_cmd")
    def test_with_domain(self, mock_cmd) -> None:
        # @trace FR-CLI-086
        result = runner.invoke(app, ["archive", "--domain", "production"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["domain"] == "production"

    @patch("thegent.main.archive_cmd")
    def test_with_tier(self, mock_cmd) -> None:
        # @trace FR-CLI-087
        result = runner.invoke(app, ["archive", "--tier", "cold"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["tier"] == "cold"


@pytest.mark.unit
class TestOperations:
    """Tests for ``operations`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.operations_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-088
        result = runner.invoke(app, ["operations"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None, operation=None)

    @patch("thegent.main.operations_cmd")
    def test_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-089
        result = runner.invoke(app, ["operations", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["format"] == "json"

    @patch("thegent.main.operations_cmd")
    def test_with_operation(self, mock_cmd) -> None:
        # @trace FR-CLI-090
        result = runner.invoke(app, ["operations", "--operation", "govern"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["operation"] == "govern"


@pytest.mark.unit
class TestModes:
    """Tests for ``modes`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.modes_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-091
        result = runner.invoke(app, ["modes"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(format=None, mode=None)

    @patch("thegent.main.modes_cmd")
    def test_with_format(self, mock_cmd) -> None:
        # @trace FR-CLI-092
        result = runner.invoke(app, ["modes", "--format", "json"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["format"] == "json"

    @patch("thegent.main.modes_cmd")
    def test_with_mode(self, mock_cmd) -> None:
        # @trace FR-CLI-093
        result = runner.invoke(app, ["modes", "--mode", "parallel_consensus"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["mode"] == "parallel_consensus"


@pytest.mark.unit
class TestBenchmark:
    """Tests for ``benchmark`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.benchmark_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-094
        result = runner.invoke(app, ["benchmark"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()


@pytest.mark.unit
class TestClosurePack:
    """Tests for ``closure-pack`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.closure_pack_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-095
        result = runner.invoke(app, ["closure-pack"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None)

    @patch("thegent.main.closure_pack_cmd")
    def test_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-096
        result = runner.invoke(app, ["closure-pack", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        call_kwargs = mock_cmd.call_args[1]
        assert call_kwargs["cd"] == tmp_path


# ---------------------------------------------------------------------------
# MODELS commands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestListAgents:
    """Tests for ``list-agents`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.list_agents_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-097
        result = runner.invoke(app, ["list-agents"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()


@pytest.mark.unit
class TestListDroids:
    """Tests for ``list-droids`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.list_droids_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-098
        result = runner.invoke(app, ["list-droids"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(cd=None)

    @patch("thegent.main.list_droids_cmd")
    def test_with_cd(self, mock_cmd, tmp_path) -> None:
        # @trace FR-CLI-099
        result = runner.invoke(app, ["list-droids", "--cd", str(tmp_path)])
        assert result.exit_code == 0
        call_kwargs = mock_cmd.call_args[1]
        assert call_kwargs["cd"] == tmp_path


@pytest.mark.unit
class TestListModels:
    """Tests for ``list-models`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.list_models_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-100
        result = runner.invoke(app, ["list-models"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            provider=None,
            by_model=False,
            refresh=False,
            include_contract=False,
        )

    @patch("thegent.main.list_models_cmd")
    def test_with_provider(self, mock_cmd) -> None:
        # @trace FR-CLI-101
        result = runner.invoke(app, ["list-models", "claude"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["provider"] == "claude"

    @patch("thegent.main.list_models_cmd")
    def test_with_by_model(self, mock_cmd) -> None:
        # @trace FR-CLI-102
        result = runner.invoke(app, ["list-models", "--by-model"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["by_model"] is True

    @patch("thegent.main.list_models_cmd")
    def test_with_refresh(self, mock_cmd) -> None:
        # @trace FR-CLI-103
        result = runner.invoke(app, ["list-models", "--refresh"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["refresh"] is True

    @patch("thegent.main.list_models_cmd")
    def test_with_include_contract(self, mock_cmd) -> None:
        # @trace FR-CLI-104
        result = runner.invoke(app, ["list-models", "--include-contract"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["include_contract"] is True


@pytest.mark.unit
class TestResolveModelRoute:
    """Tests for ``resolve-model-route`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.resolve_model_route_cmd")
    def test_with_model(self, mock_cmd) -> None:
        # @trace FR-CLI-105
        result = runner.invoke(app, ["resolve-model-route", "gpt-4o"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(
            model="gpt-4o",
            provider=None,
            policy="prefer_direct",
        )

    @patch("thegent.main.resolve_model_route_cmd")
    def test_with_provider(self, mock_cmd) -> None:
        # @trace FR-CLI-106
        result = runner.invoke(app, ["resolve-model-route", "gpt-4o", "--provider", "codex"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["provider"] == "codex"

    @patch("thegent.main.resolve_model_route_cmd")
    def test_with_policy(self, mock_cmd) -> None:
        # @trace FR-CLI-107
        result = runner.invoke(app, ["resolve-model-route", "gpt-4o", "--policy", "prefer_proxy"])
        assert result.exit_code == 0
        kwargs = mock_cmd.call_args[1]
        assert kwargs["policy"] == "prefer_proxy"


@pytest.mark.unit
class TestModelsRefresh:
    """Tests for ``models refresh`` CLI command (inline import in main.py)."""

    @patch("thegent.models.invalidate_models_cache", return_value=True)
    def test_basic_invalidated(self, mock_invalidate) -> None:
        # @trace FR-CLI-108
        result = runner.invoke(app, ["models", "refresh"])
        assert result.exit_code == 0
        mock_invalidate.assert_called_once()
        assert "invalidated" in result.stdout.lower()

    @patch("thegent.models.invalidate_models_cache", return_value=False)
    def test_already_invalidated(self, mock_invalidate) -> None:
        # @trace FR-CLI-109
        result = runner.invoke(app, ["models", "refresh"])
        assert result.exit_code == 0
        assert "empty" in result.stdout.lower() or "already" in result.stdout.lower()


@pytest.mark.unit
class TestModelsContract:
    """Tests for ``models contract`` CLI command (inline import in main.py)."""

    @patch("thegent.cli.list_model_contract_schema_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-110
        result = runner.invoke(app, ["models", "contract"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once()


# ---------------------------------------------------------------------------
# OTHER commands
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestServe:
    """Tests for ``serve`` CLI command (inline import of thegent.mcp_server)."""

    @patch("thegent.mcp_server.run")
    def test_basic(self, mock_run) -> None:
        # @trace FR-CLI-111
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(host=None, port=None)

    @patch("thegent.mcp_server.run")
    def test_with_host(self, mock_run) -> None:
        # @trace FR-CLI-112
        result = runner.invoke(app, ["serve", "--host", "0.0.0.0"])
        assert result.exit_code == 0
        kwargs = mock_run.call_args[1]
        assert kwargs["host"] == "0.0.0.0"

    @patch("thegent.mcp_server.run")
    def test_with_port(self, mock_run) -> None:
        # @trace FR-CLI-113
        result = runner.invoke(app, ["serve", "--port", "9999"])
        assert result.exit_code == 0
        kwargs = mock_run.call_args[1]
        assert kwargs["port"] == 9999


@pytest.mark.unit
class TestInstallCmd:
    """Tests for ``install`` CLI command (inline imports in main.py)."""

    @patch("thegent.install.run_install")
    def test_basic(self, mock_run_install) -> None:
        # @trace FR-CLI-114
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install"])
        assert result.exit_code == 0
        mock_run_install.assert_called_once()
        kwargs = mock_run_install.call_args[1]
        assert kwargs["target"] == "all"
        assert kwargs["mode"] == "smart"

    @patch("thegent.install.run_install")
    def test_with_target(self, mock_run_install) -> None:
        # @trace FR-CLI-115
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install", "--target", "cursor"])
        assert result.exit_code == 0
        kwargs = mock_run_install.call_args[1]
        assert kwargs["target"] == "cursor"

    @patch("thegent.install.run_install")
    def test_with_editable(self, mock_run_install) -> None:
        # @trace FR-CLI-116
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install", "--editable"])
        assert result.exit_code == 0
        kwargs = mock_run_install.call_args[1]
        assert kwargs["mode"] == "editable"

    @patch("thegent.install.run_install")
    def test_with_force(self, mock_run_install) -> None:
        # @trace FR-CLI-117
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install", "--force"])
        assert result.exit_code == 0
        kwargs = mock_run_install.call_args[1]
        assert kwargs["mode"] == "force"

    @patch("thegent.install.run_wizard")
    def test_with_wizard(self, mock_wizard) -> None:
        # @trace FR-CLI-118
        result = runner.invoke(app, ["install", "--wizard"])
        assert result.exit_code == 0
        mock_wizard.assert_called_once()

    @patch("thegent.install.run_install")
    def test_with_dry_run(self, mock_run_install) -> None:
        # @trace FR-CLI-119
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install", "--dry-run"])
        assert result.exit_code == 0
        kwargs = mock_run_install.call_args[1]
        assert kwargs["dry_run"] is True

    @patch("thegent.install.run_install")
    def test_with_service(self, mock_run_install) -> None:
        # @trace FR-CLI-120
        mock_run_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["install", "--service"])
        assert result.exit_code == 0
        kwargs = mock_run_install.call_args[1]
        assert kwargs["install_service"] is True


@pytest.mark.unit
class TestInitCmd:
    """Tests for ``init`` CLI command (inline imports in main.py)."""

    @patch("thegent.install.run_wizard")
    def test_basic(self, mock_wizard) -> None:
        # @trace FR-CLI-121
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        mock_wizard.assert_called_once_with(url=None)

    @patch("thegent.install.run_install")
    def test_with_cli(self, mock_install) -> None:
        # @trace FR-CLI-122
        mock_install.return_value = {"copied": 0, "skipped": 0, "conflicts": 0}
        result = runner.invoke(app, ["init", "--cli"])
        assert result.exit_code == 0
        mock_install.assert_called_once()
        kwargs = mock_install.call_args[1]
        assert kwargs["mode"] == "smart"
        assert kwargs["install_service"] is True

    @patch("thegent.install.run_wizard")
    def test_with_url(self, mock_wizard) -> None:
        # @trace FR-CLI-123
        result = runner.invoke(app, ["init", "--url", "http://custom:8080/mcp"])
        assert result.exit_code == 0
        mock_wizard.assert_called_once_with(url="http://custom:8080/mcp")


@pytest.mark.unit
class TestHistory:
    """Tests for ``history`` CLI commands.

    ``history_cmd`` is imported at top-level; ``events_cmd`` is inline.
    """

    @patch("thegent.main.history_cmd")
    def test_default(self, mock_cmd) -> None:
        # @trace FR-CLI-124
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(limit=50, format=None)

    @patch("thegent.main.history_cmd")
    def test_history_list(self, mock_cmd) -> None:
        # @trace FR-CLI-125
        result = runner.invoke(app, ["history", "list"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(limit=50, format=None)

    @patch("thegent.cli.events_cmd")
    def test_history_events(self, mock_cmd) -> None:
        # @trace FR-CLI-126
        result = runner.invoke(app, ["history", "events"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with(run_id=None, limit=100, format=None)


@pytest.mark.unit
class TestLogin:
    """Tests for ``login`` CLI command (top-level import in main.py)."""

    @patch("thegent.main.cliproxy_login_cmd")
    def test_basic(self, mock_cmd) -> None:
        # @trace FR-CLI-127
        mock_cmd.return_value = None
        result = runner.invoke(app, ["login", "claude"])
        assert result.exit_code == 0
        mock_cmd.assert_called_once_with("claude")


@pytest.mark.unit
class TestMcpInstall:
    """Tests for ``mcp install`` CLI command (inline imports in main.py)."""

    @patch("thegent.mcp_manage.install_to_client", return_value=(True, "OK"))
    @patch("thegent.mcp_manage._get_mcp_url", return_value="http://127.0.0.1:3847/mcp")
    @patch("thegent.config.ThegentSettings")
    def test_with_client(self, mock_settings, mock_url, mock_install) -> None:
        # @trace FR-CLI-128
        result = runner.invoke(app, ["mcp", "install", "cursor"])
        assert result.exit_code == 0
        mock_install.assert_called_once()
        call_args = mock_install.call_args
        assert call_args[0][0] == "cursor"

    @patch("thegent.mcp_manage.install_to_client", return_value=(True, "OK"))
    @patch("thegent.mcp_manage._get_mcp_url", return_value="http://127.0.0.1:3847/mcp")
    @patch("thegent.config.ThegentSettings")
    def test_with_url(self, mock_settings, mock_url, mock_install) -> None:
        # @trace FR-CLI-129
        result = runner.invoke(app, ["mcp", "install", "cursor", "--url", "http://custom:9999/mcp"])
        assert result.exit_code == 0
        mock_install.assert_called_once()


@pytest.mark.unit
class TestMcpUp:
    """Tests for ``mcp up`` CLI command (inline imports in main.py)."""

    @patch("thegent.mcp_manage.mcp_up", return_value=(True, "Started"))
    def test_basic(self, mock_up) -> None:
        # @trace FR-CLI-130
        result = runner.invoke(app, ["mcp", "up"])
        assert result.exit_code == 0
        mock_up.assert_called_once()


@pytest.mark.unit
class TestMcpDown:
    """Tests for ``mcp down`` CLI command (inline imports in main.py)."""

    @patch("thegent.mcp_manage.mcp_down", return_value=(True, "Stopped"))
    def test_basic(self, mock_down) -> None:
        # @trace FR-CLI-131
        result = runner.invoke(app, ["mcp", "down"])
        assert result.exit_code == 0
        mock_down.assert_called_once()


@pytest.mark.unit
class TestMcpService:
    """Tests for ``mcp service`` CLI command (inline imports in main.py)."""

    @patch("thegent.mcp_manage.service_install", return_value=(True, "Installed"))
    @patch("thegent.config.ThegentSettings")
    def test_install_action(self, mock_settings, mock_svc) -> None:
        # @trace FR-CLI-132
        result = runner.invoke(app, ["mcp", "service", "install"])
        assert result.exit_code == 0
        mock_svc.assert_called_once()

    @patch("thegent.mcp_manage.service_start", return_value=(True, "Started"))
    @patch("thegent.config.ThegentSettings")
    def test_start_action(self, mock_settings, mock_svc) -> None:
        # @trace FR-CLI-133
        mock_settings.return_value.mcp_host = "127.0.0.1"
        mock_settings.return_value.mcp_port = 3847
        result = runner.invoke(app, ["mcp", "service", "start"])
        assert result.exit_code == 0
        mock_svc.assert_called_once()

    @patch("thegent.mcp_manage.service_stop", return_value=(True, "Stopped"))
    @patch("thegent.config.ThegentSettings")
    def test_stop_action(self, mock_settings, mock_svc) -> None:
        # @trace FR-CLI-134
        result = runner.invoke(app, ["mcp", "service", "stop"])
        assert result.exit_code == 0
        mock_svc.assert_called_once()

    @patch("thegent.mcp_manage.service_start", return_value=(True, "Started"))
    @patch("thegent.mcp_manage.service_stop", return_value=(True, "Stopped"))
    @patch("thegent.config.ThegentSettings")
    def test_restart_action(self, mock_settings, mock_stop, mock_start) -> None:
        # @trace FR-CLI-135
        mock_settings.return_value.mcp_host = "127.0.0.1"
        mock_settings.return_value.mcp_port = 3847
        result = runner.invoke(app, ["mcp", "service", "restart"])
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_start.assert_called_once()

    @patch("thegent.mcp_manage.service_status", return_value=(True, "Running"))
    @patch("thegent.config.ThegentSettings")
    def test_status_action(self, mock_settings, mock_svc) -> None:
        # @trace FR-CLI-136
        result = runner.invoke(app, ["mcp", "service", "status"])
        assert result.exit_code == 0
        mock_svc.assert_called_once()

    @patch("thegent.mcp_manage.service_uninstall", return_value=(True, "Uninstalled"))
    @patch("thegent.config.ThegentSettings")
    def test_uninstall_action(self, mock_settings, mock_svc) -> None:
        # @trace FR-CLI-137
        result = runner.invoke(app, ["mcp", "service", "uninstall"])
        assert result.exit_code == 0
        mock_svc.assert_called_once()

    @patch("thegent.config.ThegentSettings")
    def test_unknown_action(self, mock_settings) -> None:
        # @trace FR-CLI-138
        result = runner.invoke(app, ["mcp", "service", "bogus"])
        assert result.exit_code == 1
