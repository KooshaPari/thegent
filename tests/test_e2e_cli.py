"""E2E tests for thegent CLI (read-only, deterministic)."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


def _loads(s: str) -> dict[str, Any]:
    """Resilient JSON loading that skips non-JSON noise at the beginning (e.g. warnings)."""
    import re

    match = re.search(r"[\{\[]", s)
    if not match:
        return json.loads(s)
    return json.loads(s[match.start() :])


def _expected_trend_health_signature() -> tuple[dict[str, object], str]:
    policy = {
        "healthy_threshold": 95,
        "warning_threshold": 80,
        "degraded_threshold": 50,
        "min_coverage_pct": 80.0,
        "max_invalid_timestamps": 0,
        "coverage_penalty_per_pct": 1.25,
        "deficit_penalty_per_missing_sample": 15.0,
        "invalid_timestamp_penalty_per_event": 12.0,
        "stale_penalty": 8.0,
        "critical_penalty": 20.0,
        "unknown_or_future_penalty": 30.0,
        "gap_penalty": 10.0,
        "missing_baseline_penalty": 45.0,
    }
    signature = hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return policy, signature


@pytest.mark.e2e
class TestListAgents:
    """E2E tests for list-agents command."""

    def test_list_agents_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-agents exits 0."""
        result = runner.invoke(app, ["list-agents"])
        assert result.exit_code == 0

    def test_list_agents_contains_gemini(self) -> None:
        # @trace FR-CLI-001
        """Output contains gemini (deterministic)."""
        result = runner.invoke(app, ["list-agents"])
        assert "gemini" in result.stdout

    def test_list_agents_contains_all_expected(self) -> None:
        # @trace FR-CLI-001
        """Output contains all providers including minimax, glm, antigravity."""
        result = runner.invoke(app, ["list-agents"])
        for name in ["gemini", "codex", "copilot", "cursor", "claude", "antigravity", "minimax", "glm"]:
            assert name in result.stdout


@pytest.mark.e2e
class TestListDroids:
    """E2E tests for list-droids command."""

    def test_list_droids_exits_zero(self, project_root: Path) -> None:
        # @trace FR-CLI-001
        """list-droids exits 0 when droids exist."""
        # Use --cd=/path (Typer/Click parses path as command when space-separated)
        result = runner.invoke(app, ["list-droids", f"--cd={project_root}"])
        assert result.exit_code == 0

    def test_list_droids_contains_plan_orchestrator(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """Output contains plan-orchestrator when project has .factory/droids."""
        droids_dir = tmp_path / ".factory" / "droids"
        droids_dir.mkdir(parents=True)
        (droids_dir / "plan-orchestrator.md").write_text("# Plan Orchestrator\n")
        result = runner.invoke(app, ["list-droids", f"--cd={tmp_path}"])
        assert result.exit_code == 0
        assert "plan-orchestrator" in result.stdout


@pytest.mark.e2e
class TestClodeCommands:
    """E2E tests for clode shims and help text."""

    def test_clode_help_exits_zero(self) -> None:
        """`thegent clode --help` exits 0."""
        result = runner.invoke(app, ["clode", "--help"])
        assert result.exit_code == 0
        assert "thegent clode" in result.stdout
        assert "glm" in result.stdout

    def test_clode_no_subcommand_defaults_to_nim_interactive(self, monkeypatch) -> None:
        """`thegent clode` defaults to Nim-backed interactive session."""
        calls: list[str] = []

        def fake_run(provider: str) -> None:
            calls.append(provider)

        monkeypatch.setattr("thegent.clode_main._run_claude_interactive", fake_run)
        result = runner.invoke(app, ["clode"])
        assert result.exit_code == 0
        assert calls == ["nim"]

    def test_clode_install_links_force_rewrites_wrappers(self, tmp_path: Path) -> None:
        """`thegent clode install-links --force` creates expected shim files."""
        # Start with legacy files to ensure --force path is exercised.
        (tmp_path / "clode").write_text("legacy")
        (tmp_path / "claudeglm").write_text("legacy")
        (tmp_path / "claudemax").write_text("legacy")
        result = runner.invoke(
            app,
            [
                "clode",
                "install-links",
                f"--bin-dir={tmp_path}",
                "--force",
            ],
        )
        assert result.exit_code == 0
        for name in ("clode", "claudeglm", "claudemax"):
            wrapper = tmp_path / name
            assert wrapper.exists()
            assert wrapper.read_text(encoding="utf-8").startswith("#!/usr/bin/env sh")
            assert "exec" in wrapper.read_text(encoding="utf-8")


@pytest.mark.e2e
class TestRunAmbiguousCwd:
    """E2E tests for run with ambiguous cwd (no project indicators)."""

    def test_ambiguous_cwd_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Run from bare dir exits 1 with message."""
        bare = tmp_path / "bare"
        bare.mkdir()
        monkeypatch.chdir(bare)
        result = runner.invoke(app, ["run", "test", "gemini"])
        assert result.exit_code == 1
        assert "Ambiguous cwd" in result.stdout or "Provide --cd" in result.stdout


@pytest.mark.e2e
class TestRunWithExplicitCd:
    """E2E tests for run with explicit --cd (read-only)."""

    def test_unknown_agent_exits_one(self, project_root: Path) -> None:
        # @trace FR-CLI-001
        """Unknown agent exits 1 with message."""
        # Options first (Typer parses options-after-positionals as commands)
        result = runner.invoke(
            app,
            ["run", "-d", str(project_root), "test prompt", "nonexistent-agent-xyz"],
        )
        assert result.exit_code == 1
        assert "Unknown agent" in result.stdout or "nonexistent" in result.stdout.lower()

    def test_unknown_agent_suggests_agents_list(
        # @trace FR-CLI-001
        self,
        project_root: Path,
        tmp_path: Path,
    ) -> None:
        """Invoking unknown agent (e.g. plan-orchestrator) suggests agent list."""
        result = runner.invoke(
            app,
            ["run", "-d", str(tmp_path), "test prompt", "plan-orchestrator"],
        )
        assert result.exit_code == 1
        assert "Unknown agent" in result.stdout or "plan-orchestrator" in result.stdout
        assert "Agents:" in result.stdout or "minimax" in result.stdout


@pytest.mark.e2e
class TestSessionContractHealthGate:
    """E2E tests for session-contract-health-gate command."""

    def test_health_gate_exits_zero_with_empty_sessions(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Health gate exits 0 when no sessions (empty state passes)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate"])
        assert result.exit_code == 0

    def test_health_gate_format_json_has_schema(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Health gate --format json outputs schema_version and payload_type."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("schema_version") == "health-schema-v1"
        assert data.get("payload_type") == "session_contract_health_gate"
        assert "pass" in data
        assert "status" in data

    def test_health_gate_output_to_file(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Health gate --output writes artifact with --overwrite."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        out_path = tmp_path / "gate.json"
        result = runner.invoke(
            app,
            ["session-contract-health-gate", "--output", str(out_path), "--overwrite"],
        )
        assert result.exit_code == 0
        assert out_path.exists()
        data = json.loads(out_path.read_text())
        assert data.get("payload_type") == "session_contract_health_gate"


@pytest.mark.e2e
class TestSessionContractHealthReport:
    """E2E tests for session-contract-health-report command."""

    def test_health_report_exits_zero_with_empty_sessions(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Health report exits 0 when no sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report"])
        assert result.exit_code == 0

    def test_health_report_format_json_has_schema(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Health report --format json outputs schema_version and payload_type."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("schema_version") == "health-schema-v1"
        assert data.get("payload_type") == "session_contract_health_report"
        assert "status" in data
        assert "health" in data


@pytest.mark.e2e
class TestResolveModelRoute:
    """E2E tests for resolve-model-route command."""

    def test_resolve_known_model_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route gemini-3-flash exits 0."""
        result = runner.invoke(app, ["resolve-model-route", "gemini-3-flash"])
        assert result.exit_code == 0

    def test_resolve_known_model_output_has_route(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route output has route_found and resolved_route."""
        result = runner.invoke(app, ["resolve-model-route", "gemini-3-flash"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("route_found") is True
        assert "resolved_route" in data
        assert data["resolved_route"].get("provider") == "gemini"
        assert data["resolved_route"].get("schema_version") == 1

    def test_resolve_unknown_model_exits_one(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route unknown model exits 1."""
        result = runner.invoke(app, ["resolve-model-route", "unknown-model-xyz"])
        assert result.exit_code == 1


@pytest.mark.e2e
class TestListModels:
    """E2E tests for list-models command."""

    def test_list_models_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-models exits 0."""
        result = runner.invoke(app, ["list-models"])
        assert result.exit_code == 0

    def test_list_models_contains_gemini(self) -> None:
        # @trace FR-CLI-001
        """list-models output contains gemini."""
        result = runner.invoke(app, ["list-models"])
        assert "gemini" in result.stdout


@pytest.mark.e2e
class TestModelsContract:
    """E2E tests for models contract command."""

    def test_models_contract_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """models contract exits 0."""
        result = runner.invoke(app, ["models", "contract"])
        assert result.exit_code == 0

    def test_models_contract_output_has_schema_version(self) -> None:
        # @trace FR-CLI-001
        """models contract output has schema_version."""
        result = runner.invoke(app, ["models", "contract"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("schema_version") == 1
        assert "backend_types" in data
        assert "policy_names" in data


@pytest.mark.e2e
class TestHistory:
    """E2E tests for history command."""

    def test_history_exits_zero_with_empty_registry(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """History exits 0 when run registry is empty."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
        assert "No runs" in result.stdout or "No execution history" in result.stdout

    def test_history_format_json_with_empty_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """History --format json with empty registry exits 0 (early return or [])."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "--format", "json"])
        assert result.exit_code == 0
        # Empty registry: either early-return "No runs" or JSON []
        if result.stdout.strip().startswith("["):
            data = _loads(result.stdout)
            assert isinstance(data, list)
            assert len(data) == 0
        else:
            assert "No runs" in result.stdout or "No execution history" in result.stdout


@pytest.mark.e2e
class TestPs:
    """E2E tests for ps command."""

    def test_ps_exits_zero_with_empty_sessions(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps exits 0 when no sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout

    def test_ps_format_json_with_empty_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --format json with empty sessions exits 0 (early return or [])."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--format", "json"])
        assert result.exit_code == 0
        # Empty: either early-return "No sessions" or JSON []
        if result.stdout.strip().startswith("["):
            data = _loads(result.stdout)
            assert isinstance(data, list)
            assert len(data) == 0
        else:
            assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestSessionContracts:
    """E2E tests for session-contracts command."""

    def test_session_contracts_exits_zero_with_empty(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts exits 0 when no sessions match."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestStatusLogsWaitStop:
    """E2E tests for status, logs, wait, stop with unknown session."""

    def test_status_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """status with unknown session_id exits 2 with Session not found."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["status", "session_unknown_e2e_123"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_logs_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """logs with unknown session_id exits 2 with Session not found."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["logs", "session_unknown_e2e_456"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr or "Log file missing" in result.stderr

    def test_wait_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """wait with unknown session_id exits 2 with Session not found."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["wait", "session_unknown_e2e_789"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_stop_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """stop with unknown session_id exits 2 with Session not found."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["stop", "session_unknown_e2e_999"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestInspect:
    """E2E tests for inspect command."""

    def test_inspect_with_owner_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """inspect --owner when no sessions exits 0 with No sessions found."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["inspect", "--owner", "e2e_test_owner_xyz"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestDagList:
    """E2E tests for dag list command."""

    def test_dag_list_no_dag_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag list with --cd to dir without .factory/dag-session.md exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()  # project indicator
        result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert result.exit_code == 1
        assert "DAG session not found" in result.stdout or "DAG session not found" in result.stderr

    def test_dag_list_empty_dag_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag list with empty dag-session.md exits 0 with No tasks."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        (factory / "dag-session.md").write_text(dag_content)
        result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert result.exit_code == 0
        assert "No tasks" in result.stdout

    def test_dag_list_ambiguous_cwd_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag list from bare dir without --cd exits 1 with Ambiguous cwd."""
        bare = tmp_path / "bare"
        bare.mkdir()
        monkeypatch.chdir(bare)
        result = runner.invoke(app, ["dag", "list"])
        assert result.exit_code == 1
        assert "Ambiguous cwd" in result.stdout or "Provide --cd" in result.stdout


@pytest.mark.e2e
class TestDagValidate:
    """E2E tests for dag validate command."""

    def test_dag_validate_no_dag_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag validate with --cd to dir without dag-session.md exits 2."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        result = runner.invoke(app, ["dag", "validate", "--cd", str(project)])
        assert result.exit_code == 2
        assert "DAG session not found" in result.stdout or "DAG session not found" in result.stderr

    def test_dag_validate_valid_empty_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag validate with valid empty dag-session.md exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        (factory / "dag-session.md").write_text(dag_content)
        result = runner.invoke(app, ["dag", "validate", "--cd", str(project)])
        assert result.exit_code == 0
        assert "DAG valid" in result.stdout


@pytest.mark.e2e
class TestSessionContractHealthTrend:
    """E2E tests for session-contract-health-trend command."""

    def test_health_trend_exits_zero_with_empty_snapshots(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend exits 0 when no snapshots."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend"])
        assert result.exit_code == 0

    def test_health_trend_format_json_has_schema(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --format json has schema fields."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "schema_version" in data or "payload_type" in data
        assert "snapshot_count" in data or "trend_payload_type" in data


@pytest.mark.e2e
class TestPolicyProfile:
    """E2E tests for --policy-profile on health gate and report."""

    def test_health_gate_policy_profile_strict_ci(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --policy-profile strict_ci exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["session-contract-health-gate", "--policy-profile", "strict_ci"],
        )
        assert result.exit_code == 0
        assert "policy_profile" in result.stdout or "strict_ci" in result.stdout

    def test_health_report_policy_profile_warn_only(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --policy-profile warn_only exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["session-contract-health-report", "--policy-profile", "warn_only"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestModelsRefresh:
    """E2E tests for models refresh command."""

    def test_models_refresh_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """models refresh exits 0 (cache empty or invalidated)."""
        result = runner.invoke(app, ["models", "refresh"])
        assert result.exit_code == 0
        assert "cache" in result.stdout.lower()


@pytest.mark.e2e
class TestDagStatusReadySync:
    """E2E tests for dag status, ready, sync commands."""

    def _empty_dag_project(self, tmp_path: Path) -> Path:
        """Create project with empty valid dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        (factory / "dag-session.md").write_text(dag_content)
        return project

    def test_dag_status_no_dag_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag status with no dag-session.md exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        result = runner.invoke(app, ["dag", "status", "--cd", str(project)])
        assert result.exit_code == 1
        assert "DAG session not found" in result.stdout or "DAG session not found" in result.stderr

    def test_dag_status_empty_dag_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag status with empty DAG exits 0 with No tasks with session_id."""
        project = self._empty_dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "status", "--cd", str(project)])
        assert result.exit_code == 0
        assert "No tasks with session_id" in result.stdout

    def test_dag_ready_no_dag_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag ready with no dag-session.md exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        result = runner.invoke(app, ["dag", "ready", "--cd", str(project)])
        assert result.exit_code == 1
        assert "DAG session not found" in result.stdout or "DAG session not found" in result.stderr

    def test_dag_ready_empty_dag_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag ready with empty DAG exits 0 with No ready tasks."""
        project = self._empty_dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "ready", "--cd", str(project)])
        assert result.exit_code == 0
        assert "No ready tasks" in result.stdout

    def test_dag_sync_no_dag_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag sync with no dag-session.md exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        result = runner.invoke(app, ["dag", "sync", "--cd", str(project)])
        assert result.exit_code == 1
        assert "DAG session not found" in result.stdout or "DAG session not found" in result.stderr

    def test_dag_sync_empty_dag_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag sync with empty DAG exits 0 (no running sessions to sync)."""
        project = self._empty_dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "sync", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestListModelsIncludeContract:
    """E2E tests for list-models --include-contract."""

    def test_list_models_include_contract_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-models --include-contract exits 0."""
        result = runner.invoke(app, ["list-models", "--include-contract"])
        assert result.exit_code == 0

    def test_list_models_include_contract_output_has_schema(self) -> None:
        # @trace FR-CLI-001
        """list-models --include-contract outputs JSON with schema_version and routes."""
        result = runner.invoke(app, ["list-models", "--include-contract"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "schema_version" in data
        assert "routes" in data or "contract" in data


@pytest.mark.e2e
class TestResolveModelRoutePolicy:
    """E2E tests for resolve-model-route with different --policy values."""

    def test_resolve_model_route_policy_prefer_proxy(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route --policy prefer_proxy exits 0 with route."""
        result = runner.invoke(app, ["resolve-model-route", "gemini-3-flash", "--policy", "prefer_proxy"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("route_found") is True
        assert data.get("policy") == "prefer_proxy"

    def test_resolve_model_route_policy_failover(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route --policy failover exits 0 with available_routes."""
        result = runner.invoke(app, ["resolve-model-route", "gemini-3-flash", "--policy", "failover"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "available_routes" in data or data.get("route_found") is True


@pytest.mark.e2e
class TestNoWorseThanBaseline:
    """E2E tests for --no-worse-than-baseline on health gate and report."""

    def test_health_gate_no_worse_than_baseline_empty_baseline(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Gate with --no-worse-than-baseline and no baseline exits 0 (pass)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            ["session-contract-health-gate", "--no-worse-than-baseline"],
        )
        assert result.exit_code == 0

    def test_health_report_no_worse_than_baseline_empty_baseline(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Report with --no-worse-than-baseline and no baseline exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            ["session-contract-health-report", "--no-worse-than-baseline"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagAdd:
    """E2E tests for dag add command."""

    def test_dag_add_then_list(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
    ) -> None:
        """dag add creates task; dag list shows it."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        (factory / "dag-session.md").write_text(dag_content)

        add_result = runner.invoke(
            app,
            ["dag", "add", "T1", "gemini", "test prompt", "--cd", str(project)],
        )
        assert add_result.exit_code == 0
        assert "Added task T1" in add_result.stdout

        list_result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "T1" in list_result.stdout
        assert "gemini" in list_result.stdout

    def test_dag_add_duplicate_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag add with existing task_id exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n| T1 | gemini | p1 | — | pending |\n"
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(
            app,
            ["dag", "add", "T1", "gemini", "other prompt", "--cd", str(project)],
        )
        assert result.exit_code == 1
        assert "already exists" in result.stdout or "already exists" in result.stderr


@pytest.mark.e2e
class TestDagRemoveUpdateCancel:
    """E2E tests for dag remove, update, cancel commands."""

    def _project_with_task(self, tmp_path: Path, task_id: str = "T1") -> Path:
        """Create project with single task."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            f"| {task_id} | gemini | test | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)
        return project

    def test_dag_remove_then_list(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag remove removes task; dag list shows No tasks."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["dag", "remove", "T1", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Removed task T1" in result.stdout

        list_result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "No tasks" in list_result.stdout

    def test_dag_remove_nonexistent_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag remove with nonexistent task_id exits 1."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["dag", "remove", "T99", "--cd", str(project)])
        assert result.exit_code == 1
        assert "not found" in result.stdout or "not found" in result.stderr

    def test_dag_update_status_then_list(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag update --status done updates task; dag list shows done."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["dag", "update", "T1", "--status", "done", "--cd", str(project)])
        assert result.exit_code == 0

        list_result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "done" in list_result.stdout

    def test_dag_cancel_then_list(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag cancel sets status cancelled; dag list shows cancelled."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["dag", "cancel", "T1", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Cancelled task T1" in result.stdout

        list_result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "cancelled" in list_result.stdout


@pytest.mark.e2e
class TestDagListFormat:
    """E2E tests for dag list --format md."""

    def test_dag_list_format_md_has_table(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag list --format md outputs markdown table with task."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "list", "--format", "md", "--cd", str(project)])
        assert result.exit_code == 0
        assert "## DAG Session" in result.stdout
        assert "| id |" in result.stdout
        assert "T1" in result.stdout


@pytest.mark.e2e
class TestSessionContractsFormat:
    """E2E tests for session-contracts --format json."""

    def test_session_contracts_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --format json exits 0 (empty: No sessions; non-empty: rows+summary)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--format", "json"])
        assert result.exit_code == 0
        # Empty sessions: early return with "No sessions" text
        if result.stdout.strip().startswith("{"):
            data = _loads(result.stdout)
            assert "rows" in data
            assert "summary" in data
        else:
            assert "No sessions" in result.stdout or "contract" in result.stdout.lower()


@pytest.mark.e2e
class TestResolveModelRouteInvalidPolicy:
    """E2E tests for resolve-model-route with invalid policy."""

    def test_resolve_model_route_invalid_policy_exits_one(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route with invalid --policy exits 1."""
        result = runner.invoke(app, ["resolve-model-route", "gemini-3-flash", "--policy", "invalid_policy_xyz"])
        assert result.exit_code == 1
        assert "Invalid" in result.stdout or "policy" in result.stdout.lower() or "prefer_direct" in result.stdout


@pytest.mark.e2e
class TestDagValidationErrors:
    """E2E tests for dag add/update validation errors."""

    def _project_with_task(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | test | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)
        return project

    def test_dag_add_invalid_depends_on_exits_two(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag add with --depends-on referencing nonexistent task exits 2."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(
            app,
            ["dag", "add", "T2", "gemini", "prompt", "--depends-on", "T99", "--cd", str(project)],
        )
        assert result.exit_code == 2
        assert "does not exist" in result.stdout or "does not exist" in result.stderr

    def test_dag_update_invalid_status_exits_two(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag update with invalid --status exits 2."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(
            app,
            ["dag", "update", "T1", "--status", "invalid_status", "--cd", str(project)],
        )
        assert result.exit_code == 2
        assert "Invalid status" in result.stdout or "Invalid status" in result.stderr


@pytest.mark.e2e
class TestDagRunDryRun:
    """E2E tests for dag run --dry-run."""

    def test_dag_run_dry_run_no_ready_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run with no ready tasks exits 0 with No ready tasks."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "run", "--dry-run", "--cd", str(project)])
        assert result.exit_code == 0
        assert "No ready tasks" in result.stdout

    def test_dag_run_dry_run_with_ready_shows_would_run(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run with ready task shows Would run."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello world | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "run", "--dry-run", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Would run" in result.stdout
        assert "T1" in result.stdout
        assert "gemini" in result.stdout


@pytest.mark.e2e
class TestListModelsByModel:
    """E2E tests for list-models --by-model."""

    def test_list_models_by_model_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-models --by-model exits 0."""
        result = runner.invoke(app, ["list-models", "--by-model"])
        assert result.exit_code == 0
        assert "Models by model ID" in result.stdout or "gemini" in result.stdout


@pytest.mark.e2e
class TestResolveModelRouteProvider:
    """E2E tests for resolve-model-route with --provider."""

    def test_resolve_model_route_with_provider_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route with --provider exits 0 with resolved route."""
        result = runner.invoke(
            app,
            ["resolve-model-route", "gemini-3-flash", "--provider", "gemini"],
        )
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert data.get("route_found") is True
        assert data.get("resolved_route", {}).get("provider") == "gemini"


@pytest.mark.e2e
class TestDagAddDependsOn:
    """E2E tests for dag add with --depends-on."""

    def test_dag_add_with_depends_on_then_list(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag add T2 with --depends-on T1; both appear in list."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | first | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(
            app,
            ["dag", "add", "T2", "gemini", "second", "--depends-on", "T1", "--cd", str(project)],
        )
        assert result.exit_code == 0
        assert "Added task T2" in result.stdout

        list_result = runner.invoke(app, ["dag", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "T1" in list_result.stdout
        assert "T2" in list_result.stdout


@pytest.mark.e2e
class TestDagReadyWithDeps:
    """E2E tests for dag ready with dependency chain."""

    def test_dag_ready_shows_t1_when_t2_depends_on_t1(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """When T2 depends on T1, only T1 is ready (T1 pending, T2 blocked)."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | first | — | pending |\n"
            "| T2 | gemini | second | T1 | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "ready", "--cd", str(project)])
        assert result.exit_code == 0
        assert "T1" in result.stdout
        assert "T2" not in result.stdout or "No ready" in result.stdout

    def test_dag_ready_shows_t2_after_t1_done(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """When T1 is done, T2 becomes ready."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | first | — | done |\n"
            "| T2 | gemini | second | T1 | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "ready", "--cd", str(project)])
        assert result.exit_code == 0
        assert "T2" in result.stdout


@pytest.mark.e2e
class TestListModelsProvider:
    """E2E tests for list-models with provider filter."""

    def test_list_models_provider_gemini_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-models gemini exits 0."""
        result = runner.invoke(app, ["list-models", "gemini"])
        assert result.exit_code == 0
        assert "gemini" in result.stdout.lower()


@pytest.mark.e2e
class TestDagValidateInvalid:
    """E2E tests for dag validate with invalid DAG."""

    def test_dag_validate_unknown_agent_exits_two(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag validate with unknown agent in task exits 2."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | unknown-agent-xyz | test | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "validate", "--cd", str(project)])
        assert result.exit_code == 2
        assert "Unknown agent" in result.stdout or "unknown-agent" in result.stdout

    def test_dag_validate_cycle_exits_two(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag validate with cycle (T1->T2->T1) exits 2."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | first | T2 | pending |\n"
            "| T2 | gemini | second | T1 | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "validate", "--cd", str(project)])
        assert result.exit_code == 2
        assert "cycle" in result.stdout.lower() or "Cycle" in result.stdout


@pytest.mark.e2e
class TestSessionContractsOptions:
    """E2E tests for session-contracts --missing-only and --summary-only."""

    def test_session_contracts_missing_only_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --missing-only exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--missing-only"])
        assert result.exit_code == 0

    def test_session_contracts_summary_only_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --summary-only exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--summary-only"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHelp:
    """E2E tests for --help."""

    def test_app_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """thegent --help exits 0."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "thegent" in result.stdout or "Usage" in result.stdout

    def test_dag_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """thegent dag --help exits 0."""
        result = runner.invoke(app, ["dag", "--help"])
        assert result.exit_code == 0
        assert "dag" in result.stdout.lower() or "list" in result.stdout


@pytest.mark.e2e
class TestHistoryLimit:
    """E2E tests for history --limit."""

    def test_history_limit_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history --limit 5 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestSessionContractsStrict:
    """E2E tests for session-contracts --strict."""

    def test_session_contracts_strict_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --strict exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--strict"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPsAll:
    """E2E tests for ps --all."""

    def test_ps_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--all"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestHealthTrendPayloadType:
    """E2E tests for session-contract-health-trend --payload-type."""

    def test_health_trend_payload_type_gate_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --payload-type session_contract_health_gate exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            ["session-contract-health-trend", "--payload-type", "session_contract_health_gate"],
        )
        assert result.exit_code == 0
        assert "gate" in result.stdout.lower() or "trend" in result.stdout.lower()


@pytest.mark.e2e
class TestStatusFormat:
    """E2E tests for status --format and --include-contract."""

    def test_status_format_json_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """status unknown_session --format json exits 2 (option parses correctly)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["status", "session_unknown_e2e_format", "--format", "json"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_status_include_contract_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """status unknown_session --include-contract exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["status", "session_unknown_e2e_inc", "--include-contract"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestDagRunDryRunWithTask:
    """E2E tests for dag run --dry-run --task."""

    def test_dag_run_dry_run_task_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run --task T1 with T1 ready shows Would run T1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello world | — | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "run", "--dry-run", "--task", "T1", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Would run" in result.stdout
        assert "T1" in result.stdout

    def test_dag_run_dry_run_task_not_ready_exits_one(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run --task T2 when T2 depends on T1 (pending) exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        dag_content = (
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | step 1 | — | pending |\n"
            "| T2 | gemini | step 2 | T1 | pending |\n"
        )
        (factory / "dag-session.md").write_text(dag_content)

        result = runner.invoke(app, ["dag", "run", "--dry-run", "--task", "T2", "--cd", str(project)])
        assert result.exit_code == 1
        assert "not ready" in result.stdout or "not ready" in result.stderr


@pytest.mark.e2e
class TestRegressionTolerance:
    """E2E tests for gate/report --regression-tolerance."""

    def test_gate_regression_tolerance_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --regression-tolerance 0.1 exits 0 with no sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-gate",
                "--regression-tolerance",
                "0.1",
            ],
        )
        assert result.exit_code == 0

    def test_report_regression_tolerance_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --regression-tolerance 0.05 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-report",
                "--regression-tolerance",
                "0.05",
            ],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestModelsHelp:
    """E2E tests for models subcommand help."""

    def test_models_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """models --help exits 0."""
        result = runner.invoke(app, ["models", "--help"])
        assert result.exit_code == 0
        assert "Model catalog" in result.stdout or "refresh" in result.stdout


@pytest.mark.e2e
class TestDagCheckpoint:
    """E2E tests for dag checkpoint, checkpoints, recover, probe, rollback."""

    def test_dag_checkpoint_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag checkpoint exits 0 and creates checkpoint."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["dag", "checkpoint", "--cd", str(project), "--reason", "E2E test"])
        assert result.exit_code == 0

    def test_dag_checkpoints_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag checkpoints exits 0 (no checkpoints or lists them)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["dag", "checkpoints", "--limit", "5"])
        assert result.exit_code == 0
        assert "No checkpoints" in result.stdout or "Checkpoint" in result.stdout

    def test_dag_recover_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag recover exits 0 with DAG."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["dag", "recover", "retry-failed", "--cd", str(project)])
        assert result.exit_code == 0

    def test_dag_probe_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag probe exits 0 with DAG (no baseline or shows message)."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["dag", "probe", "--cd", str(project)])
        assert result.exit_code == 0
        assert "baseline" in result.stdout.lower() or "regression" in result.stdout.lower()

    def test_dag_rollback_unknown_checkpoint_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag rollback with unknown checkpoint_id exits 1."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["dag", "rollback", "ckpt_unknown_e2e", "--cd", str(project)])
        assert result.exit_code == 1
        assert "Checkpoint not found" in result.stdout or "Checkpoint not found" in result.stderr


@pytest.mark.e2e
class TestReportOutput:
    """E2E tests for session-contract-health-report --output."""

    def test_report_output_writes_artifact(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --output writes artifact with --overwrite."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        out_path = tmp_path / "report.json"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-report",
                "--output",
                str(out_path),
                "--overwrite",
            ],
        )
        assert result.exit_code == 0
        assert out_path.exists()


@pytest.mark.e2e
class TestDagRecoverActions:
    """E2E tests for dag recover clear-stuck and reset-retries."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_dag_recover_clear_stuck_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag recover clear-stuck exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "recover", "clear-stuck", "--cd", str(project)])
        assert result.exit_code == 0

    def test_dag_recover_reset_retries_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag recover reset-retries exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "recover", "reset-retries", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagFormatOptions:
    """E2E tests for dag status and dag ready --format."""

    def test_dag_status_format_md_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag status --format md exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["dag", "status", "--cd", str(project), "--format", "md"])
        assert result.exit_code == 0

    def test_dag_ready_format_md_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag ready --format md exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["dag", "ready", "--cd", str(project), "--format", "md"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestMcpHelp:
    """E2E tests for mcp subcommand help."""

    def test_mcp_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp --help exits 0."""
        result = runner.invoke(app, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "install" in result.stdout or "MCP" in result.stdout


@pytest.mark.e2e
class TestInspectFormat:
    """E2E tests for inspect --format json."""

    def test_inspect_format_json_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """inspect --owner --format json with no sessions exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["inspect", "--owner", "e2e_inspect_format", "--format", "json"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout or "[]" in result.stdout


@pytest.mark.e2e
class TestLoginServeHelp:
    """E2E tests for login and serve --help."""

    def test_login_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """login --help exits 0."""
        result = runner.invoke(app, ["login", "--help"])
        assert result.exit_code == 0
        assert "provider" in result.stdout.lower() or "OAuth" in result.stdout

    def test_serve_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """serve --help exits 0."""
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "host" in result.stdout.lower() or "port" in result.stdout


@pytest.mark.e2e
class TestDagProbeBaselineId:
    """E2E tests for dag probe --baseline-id."""

    def test_dag_probe_unknown_baseline_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """dag probe --baseline-id unknown exits 1."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["dag", "probe", "--baseline-id", "ckpt_unknown_e2e", "--cd", str(project)])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()


@pytest.mark.e2e
class TestHealthTrendReportPayload:
    """E2E tests for session-contract-health-trend --payload-type report."""

    def test_health_trend_payload_type_report_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --payload-type session_contract_health_report exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            [
                "session-contract-health-trend",
                "--payload-type",
                "session_contract_health_report",
            ],
        )
        assert result.exit_code == 0
        assert "report" in result.stdout.lower() or "trend" in result.stdout.lower()


@pytest.mark.e2e
class TestGateExportFormat:
    """E2E tests for session-contract-health-gate --export-format."""

    def test_gate_export_format_md_writes_file(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --output with --export-format md writes markdown."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        out_path = tmp_path / "gate.md"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-gate",
                "--output",
                str(out_path),
                "--export-format",
                "md",
                "--overwrite",
            ],
        )
        assert result.exit_code == 0
        assert out_path.exists()
        content = out_path.read_text()
        assert "pass" in content.lower() or "blocked" in content.lower() or "status" in content.lower()


@pytest.mark.e2e
class TestHistoryVerify:
    """E2E tests for history verify command."""

    def test_history_verify_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history verify exits 0 with empty registry."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "verify"])
        assert result.exit_code == 0
        assert "Audit" in result.stdout or "verified" in result.stdout.lower() or "empty" in result.stdout.lower()

    def test_history_verify_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history verify --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "verify", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "status" in data


@pytest.mark.e2e
class TestPolicyShow:
    """E2E tests for policy show command."""

    def test_policy_show_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """policy show exits 0."""
        result = runner.invoke(app, ["policy", "show"])
        assert result.exit_code == 0
        assert "Policy" in result.stdout or "Governance" in result.stdout


@pytest.mark.e2e
class TestCliproxyHelp:
    """E2E tests for cliproxy subcommand help."""

    def test_cliproxy_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """cliproxy --help exits 0."""
        result = runner.invoke(app, ["cliproxy", "--help"])
        assert result.exit_code == 0
        assert "login" in result.stdout


@pytest.mark.e2e
class TestMcpInstallHelp:
    """E2E tests for mcp install --help."""

    def test_mcp_install_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp install --help exits 0."""
        result = runner.invoke(app, ["mcp", "install", "--help"])
        assert result.exit_code == 0
        assert "client" in result.stdout.lower() or "cursor" in result.stdout.lower()


@pytest.mark.e2e
class TestReportExportOptions:
    """E2E tests for session-contract-health-report export and top-blocked options."""

    def test_report_export_format_csv_writes_file(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --output with --export-format csv writes CSV."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        out_path = tmp_path / "report.csv"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-report",
                "--output",
                str(out_path),
                "--export-format",
                "csv",
                "--overwrite",
            ],
        )
        assert result.exit_code == 0
        assert out_path.exists()

    def test_report_top_blocked_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --top-blocked 10 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["session-contract-health-report", "--top-blocked", "10"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestCockpit:
    """E2E tests for cockpit command."""

    def test_cockpit_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """cockpit exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["cockpit"])
        assert result.exit_code == 0
        assert "Sessions" in result.stdout or "Orchestration" in result.stdout


@pytest.mark.e2e
class TestHistoryEventsList:
    """E2E tests for history events and history list."""

    def test_history_events_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "events", "--limit", "5"])
        assert result.exit_code == 0

    def test_history_list_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history list exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "list", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestStopOptions:
    """E2E tests for stop --force and --wind-down options."""

    def test_stop_force_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """stop --force unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["stop", "--force", "session_unknown_e2e_stop_force"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_stop_wind_down_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """stop --wind-down unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["stop", "--wind-down", "session_unknown_e2e_wind_down"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestMcpServiceHelp:
    """E2E tests for mcp service --help."""

    def test_mcp_service_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp service --help exits 0."""
        result = runner.invoke(app, ["mcp", "service", "--help"])
        assert result.exit_code == 0
        assert "action" in result.stdout.lower() or "install" in result.stdout.lower()


@pytest.mark.e2e
class TestLogsWaitOptions:
    """E2E tests for logs and wait option parsing."""

    def test_logs_tail_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """logs --tail 10 unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["logs", "session_unknown_e2e_logs_tail", "--tail", "10"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr or "Log file missing" in result.stderr

    def test_wait_timeout_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """wait --timeout 5 unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["wait", "session_unknown_e2e_wait_to", "--timeout", "5"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestHealthTrendOutput:
    """E2E tests for session-contract-health-trend --output and --limit."""

    def test_health_trend_output_writes_file(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --output writes artifact."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        out_path = tmp_path / "trend.json"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            [
                "session-contract-health-trend",
                "--output",
                str(out_path),
                "--overwrite",
            ],
        )
        assert result.exit_code == 0
        assert out_path.exists()

    def test_health_trend_limit_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --limit 5 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPsFormat:
    """E2E tests for ps --format json."""

    def test_ps_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --format json exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--format", "json"])
        assert result.exit_code == 0
        out = result.stdout.strip()
        assert "No sessions" in out or (out.startswith(("[", "{")))


@pytest.mark.e2e
class TestInspectTail:
    """E2E tests for inspect --tail option."""

    def test_inspect_tail_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """inspect --owner --tail 20 with no sessions exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["inspect", "--owner", "e2e_inspect_tail", "--tail", "20"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestDagRunOptions:
    """E2E tests for dag run --max-parallel and --lane."""

    def test_dag_run_dry_run_max_parallel_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run --max-parallel 2 exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(
            app,
            ["dag", "run", "--dry-run", "--max-parallel", "2", "--cd", str(project)],
        )
        assert result.exit_code == 0
        assert "Would run" in result.stdout or "No ready" in result.stdout

    def test_dag_run_dry_run_lane_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag run --dry-run --lane standard exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(
            app,
            ["dag", "run", "--dry-run", "--lane", "standard", "--cd", str(project)],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHistoryEventsRunId:
    """E2E tests for history events --run-id."""

    def test_history_events_run_id_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events --run-id some_id exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "events", "--run-id", "run_e2e_xyz", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHealthTrendFormat:
    """E2E tests for session-contract-health-trend --format."""

    def test_health_trend_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "snapshots" in data or "trend_payload_type" in data


@pytest.mark.e2e
class TestPolicyHelp:
    """E2E tests for policy subcommand help."""

    def test_policy_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """policy --help exits 0."""
        result = runner.invoke(app, ["policy", "--help"])
        assert result.exit_code == 0
        assert "show" in result.stdout


@pytest.mark.e2e
class TestOperations:
    """E2E tests for operations command (universal operation taxonomy)."""

    def test_operations_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations exits 0."""
        result = runner.invoke(app, ["operations"])
        assert result.exit_code == 0
        assert "orchestrate" in result.stdout or "govern" in result.stdout

    def test_operations_format_json(self) -> None:
        # @trace FR-CLI-001
        """operations --format json exits 0 with valid JSON."""
        result = runner.invoke(app, ["operations", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "orchestrate" in data
        assert "govern" in data
        assert "recover" in data
        assert "observe" in data
        assert "plan" in data

    def test_operations_filter_orchestrate(self) -> None:
        # @trace FR-CLI-001
        """operations --operation orchestrate exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "orchestrate"])
        assert result.exit_code == 0
        assert "run" in result.stdout or "bg" in result.stdout


@pytest.mark.e2e
class TestFeedback:
    """E2E tests for feedback command."""

    def test_feedback_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """feedback run_id score exits 0 and records feedback."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["feedback", "run_e2e_feedback_xyz", "0.85", "--note", "E2E test"])
        assert result.exit_code == 0
        assert "Feedback recorded" in result.stdout

    def test_feedback_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """feedback --help exits 0."""
        result = runner.invoke(app, ["feedback", "--help"])
        assert result.exit_code == 0
        assert "run_id" in result.stdout or "score" in result.stdout


@pytest.mark.e2e
class TestHistoryHelp:
    """E2E tests for history subcommand help."""

    def test_history_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """history --help exits 0."""
        result = runner.invoke(app, ["history", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout or "verify" in result.stdout


@pytest.mark.e2e
class TestInspectStderr:
    """E2E tests for inspect --stderr option."""

    def test_inspect_stderr_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """inspect --owner --stderr with no sessions exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["inspect", "--owner", "e2e_inspect_stderr", "--stderr"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestStopGrace:
    """E2E tests for stop --grace option."""

    def test_stop_grace_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """stop --grace 10 unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["stop", "--grace", "10", "session_unknown_e2e_grace"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestLogsStderr:
    """E2E tests for logs --stderr option."""

    def test_logs_stderr_unknown_session_exits_two(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """logs --stderr unknown_session exits 2."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["logs", "session_unknown_e2e_logs_stderr", "--stderr"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr or "Log file missing" in result.stderr


@pytest.mark.e2e
class TestRunBgHelp:
    """E2E tests for run and bg --help."""

    def test_run_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """run --help exits 0."""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "prompt" in result.stdout.lower() or "agent" in result.stdout.lower()

    def test_bg_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """bg --help exits 0."""
        result = runner.invoke(app, ["bg", "--help"])
        assert result.exit_code == 0
        assert "prompt" in result.stdout.lower() or "owner" in result.stdout.lower()


@pytest.mark.e2e
class TestListAgentsHelp:
    """E2E tests for list-agents --help."""

    def test_list_agents_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-agents --help exits 0."""
        result = runner.invoke(app, ["list-agents", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHealthTrendAll:
    """E2E tests for session-contract-health-trend --all."""

    def test_health_trend_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--all"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestSessionContractsAll:
    """E2E tests for session-contracts --all."""

    def test_session_contracts_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--all"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGateExportJsonl:
    """E2E tests for session-contract-health-gate --export-format jsonl."""

    def test_gate_export_format_jsonl_writes_file(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --output with --export-format jsonl writes file."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        out_path = tmp_path / "gate.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "session-contract-health-gate",
                "--output",
                str(out_path),
                "--export-format",
                "jsonl",
                "--overwrite",
            ],
        )
        assert result.exit_code == 0
        assert out_path.exists()


@pytest.mark.e2e
class TestListModelsDroidsHelp:
    """E2E tests for list-models and list-droids --help."""

    def test_list_models_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-models --help exits 0."""
        result = runner.invoke(app, ["list-models", "--help"])
        assert result.exit_code == 0

    def test_list_droids_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """list-droids --help exits 0."""
        result = runner.invoke(app, ["list-droids", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestCliproxyEnsureConfig:
    """E2E tests for cliproxy ensure-config."""

    def test_cliproxy_ensure_config_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """cliproxy ensure-config exits 0 and refreshes config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))
        result = runner.invoke(app, ["cliproxy", "ensure-config"])
        assert result.exit_code == 0
        assert "Config" in result.stdout or "config" in result.stdout.lower()


@pytest.mark.e2e
class TestResolveModelRouteHelp:
    """E2E tests for resolve-model-route --help."""

    def test_resolve_model_route_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """resolve-model-route --help exits 0."""
        result = runner.invoke(app, ["resolve-model-route", "--help"])
        assert result.exit_code == 0
        assert "model" in result.stdout.lower()


@pytest.mark.e2e
class TestGateMinHealthy:
    """E2E tests for session-contract-health-gate --min-healthy-ratio."""

    def test_gate_min_healthy_ratio_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --min-healthy-ratio 0.9 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["session-contract-health-gate", "--min-healthy", "0.9"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHealthTrendOwner:
    """E2E tests for session-contract-health-trend --owner."""

    def test_health_trend_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --owner e2e_owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--owner", "e2e_owner_xyz"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagReconcile:
    """E2E tests for dag reconcile command."""

    def test_dag_reconcile_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag reconcile exits 0 with valid DAG."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["dag", "reconcile", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagAddValidateHelp:
    """E2E tests for dag add and dag validate --help."""

    def test_dag_add_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag add --help exits 0."""
        result = runner.invoke(app, ["dag", "add", "--help"])
        assert result.exit_code == 0
        assert "task_id" in result.stdout or "agent" in result.stdout

    def test_dag_validate_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag validate --help exits 0."""
        result = runner.invoke(app, ["dag", "validate", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestReportFormatMd:
    """E2E tests for session-contract-health-report --format md."""

    def test_report_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --format md exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report", "--format", "md"])
        assert result.exit_code == 0
        assert "##" in result.stdout or "blocked" in result.stdout.lower()


@pytest.mark.e2e
class TestInspectIncludeContract:
    """E2E tests for inspect --include-contract."""

    def test_inspect_include_contract_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """inspect --owner --include-contract with no sessions exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["inspect", "--owner", "e2e_inspect_inc_contract", "--include-contract"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestArchiveBenchmark:
    """E2E tests for archive and benchmark commands."""

    def test_archive_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """archive exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["archive", "--days", "30"])
        assert result.exit_code == 0

    def test_archive_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """archive --help exits 0."""
        result = runner.invoke(app, ["archive", "--help"])
        assert result.exit_code == 0
        assert "days" in result.stdout.lower()

    def test_benchmark_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """benchmark exits 0 (no runs or shows metrics)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["benchmark"])
        assert result.exit_code == 0
        assert "No runs" in result.stdout or "Benchmark" in result.stdout or "runs" in result.stdout.lower()

    def test_benchmark_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """benchmark --help exits 0."""
        result = runner.invoke(app, ["benchmark", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHistoryListFormatMd:
    """E2E tests for history list --format md."""

    def test_history_list_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history list --format md exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "list", "--format", "md", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGateFormatRich:
    """E2E tests for session-contract-health-gate --format rich."""

    def test_gate_format_rich_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --format rich exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate", "--format", "rich"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGateReportOwner:
    """E2E tests for gate and report --owner."""

    def test_gate_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate", "--owner", "e2e_gate_owner"])
        assert result.exit_code == 0

    def test_report_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report", "--owner", "e2e_report_owner"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagRemoveUpdateCancelHelp:
    """E2E tests for dag remove, update, cancel --help."""

    def test_dag_remove_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag remove --help exits 0."""
        result = runner.invoke(app, ["dag", "remove", "--help"])
        assert result.exit_code == 0

    def test_dag_update_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag update --help exits 0."""
        result = runner.invoke(app, ["dag", "update", "--help"])
        assert result.exit_code == 0

    def test_dag_cancel_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag cancel --help exits 0."""
        result = runner.invoke(app, ["dag", "cancel", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPsIncludeContract:
    """E2E tests for ps --include-contract."""

    def test_ps_include_contract_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --include-contract exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--include-contract"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout


@pytest.mark.e2e
class TestDagSyncListRunHelp:
    """E2E tests for dag sync, list, run --help."""

    def test_dag_sync_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag sync --help exits 0."""
        result = runner.invoke(app, ["dag", "sync", "--help"])
        assert result.exit_code == 0
        assert "watch" in result.stdout.lower() or "interval" in result.stdout.lower()

    def test_dag_list_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag list --help exits 0."""
        result = runner.invoke(app, ["dag", "list", "--help"])
        assert result.exit_code == 0

    def test_dag_run_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag run --help exits 0."""
        result = runner.invoke(app, ["dag", "run", "--help"])
        assert result.exit_code == 0
        assert "dry-run" in result.stdout or "task" in result.stdout


@pytest.mark.e2e
class TestHealthTrendFormatMd:
    """E2E tests for session-contract-health-trend --format md."""

    def test_health_trend_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --format md exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--format", "md"])
        assert result.exit_code == 0
        assert "##" in result.stdout or "trend" in result.stdout.lower()


@pytest.mark.e2e
class TestHealthTrendPolicyProfile:
    """E2E tests for session-contract-health-trend --policy-profile."""

    def test_health_trend_policy_profile_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --policy-profile strict_ci exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            ["session-contract-health-trend", "--policy-profile", "strict_ci"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagCheckpointRollbackRecoverProbeCheckpointsHelp:
    """E2E tests for dag checkpoint, rollback, recover, probe, checkpoints --help."""

    def test_dag_checkpoint_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag checkpoint --help exits 0."""
        result = runner.invoke(app, ["dag", "checkpoint", "--help"])
        assert result.exit_code == 0
        assert "reason" in result.stdout.lower()

    def test_dag_rollback_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag rollback --help exits 0."""
        result = runner.invoke(app, ["dag", "rollback", "--help"])
        assert result.exit_code == 0

    def test_dag_recover_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag recover --help exits 0."""
        result = runner.invoke(app, ["dag", "recover", "--help"])
        assert result.exit_code == 0
        assert "retry-failed" in result.stdout or "clear-stuck" in result.stdout

    def test_dag_probe_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag probe --help exits 0."""
        result = runner.invoke(app, ["dag", "probe", "--help"])
        assert result.exit_code == 0
        assert "baseline" in result.stdout.lower()

    def test_dag_checkpoints_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag checkpoints --help exits 0."""
        result = runner.invoke(app, ["dag", "checkpoints", "--help"])
        assert result.exit_code == 0
        assert "limit" in result.stdout.lower()


@pytest.mark.e2e
class TestGateAllStrict:
    """E2E tests for session-contract-health-gate --all and --strict."""

    def test_gate_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate", "--all"])
        assert result.exit_code == 0

    def test_gate_strict_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-gate --strict exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-gate", "--strict"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestSessionContractsOwnerFormatMd:
    """E2E tests for session-contracts --owner and --format md."""

    def test_session_contracts_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--owner", "e2e_contracts_owner"])
        assert result.exit_code == 0

    def test_session_contracts_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contracts --format md exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contracts", "--format", "md"])
        assert result.exit_code == 0
        assert "##" in result.stdout or "No sessions" in result.stdout


@pytest.mark.e2e
class TestReportAllStrict:
    """E2E tests for session-contract-health-report --all and --strict."""

    def test_report_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report", "--all"])
        assert result.exit_code == 0

    def test_report_strict_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-report --strict exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["session-contract-health-report", "--strict"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHealthTrendStrictTopBlocked:
    """E2E tests for session-contract-health-trend --strict and --top-blocked."""

    def test_health_trend_strict_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --strict exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--strict"])
        assert result.exit_code == 0

    def test_health_trend_top_blocked_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """session-contract-health-trend --top-blocked 15 exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["session-contract-health-trend", "--top-blocked", "15"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHistoryEventsFormat:
    """E2E tests for history events --format json and --format md."""

    def test_history_events_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "events", "--format", "json", "--limit", "5"])
        assert result.exit_code == 0

    def test_history_events_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events --format md exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "events", "--format", "md", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPsFormatMdOwner:
    """E2E tests for ps --format md and --owner."""

    def test_ps_format_md_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --format md exits 0 with empty sessions."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--format", "md"])
        assert result.exit_code == 0

    def test_ps_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """ps --owner e2e_owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["ps", "--owner", "e2e_ps_owner"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestStatusLogsWaitStopHelp:
    """E2E tests for status, logs, wait, stop --help."""

    def test_status_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """status --help exits 0."""
        result = runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0

    def test_logs_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """logs --help exits 0."""
        result = runner.invoke(app, ["logs", "--help"])
        assert result.exit_code == 0

    def test_wait_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """wait --help exits 0."""
        result = runner.invoke(app, ["wait", "--help"])
        assert result.exit_code == 0

    def test_stop_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """stop --help exits 0."""
        result = runner.invoke(app, ["stop", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestInspectHelp:
    """E2E tests for inspect --help."""

    def test_inspect_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """inspect --help exits 0."""
        result = runner.invoke(app, ["inspect", "--help"])
        assert result.exit_code == 0
        assert "owner" in result.stdout.lower() or "session" in result.stdout.lower()


@pytest.mark.e2e
class TestSessionContractsGateReportTrendHelp:
    """E2E tests for session-contracts, gate, report, trend --help."""

    def test_session_contracts_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """session-contracts --help exits 0."""
        result = runner.invoke(app, ["session-contracts", "--help"])
        assert result.exit_code == 0

    def test_session_contract_health_gate_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """session-contract-health-gate --help exits 0."""
        result = runner.invoke(app, ["session-contract-health-gate", "--help"])
        assert result.exit_code == 0

    def test_session_contract_health_report_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """session-contract-health-report --help exits 0."""
        result = runner.invoke(app, ["session-contract-health-report", "--help"])
        assert result.exit_code == 0

    def test_session_contract_health_trend_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """session-contract-health-trend --help exits 0."""
        result = runner.invoke(app, ["session-contract-health-trend", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestDagStatusReadyHelp:
    """E2E tests for dag status and dag ready --help."""

    def test_dag_status_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag status --help exits 0."""
        result = runner.invoke(app, ["dag", "status", "--help"])
        assert result.exit_code == 0

    def test_dag_ready_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """dag ready --help exits 0."""
        result = runner.invoke(app, ["dag", "ready", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOperations:
    """E2E tests for operations command."""

    def test_operations_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations exits 0."""
        result = runner.invoke(app, ["operations"])
        assert result.exit_code == 0
        assert "orchestrate" in result.stdout.lower() or "Operation" in result.stdout

    def test_operations_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --help exits 0."""
        result = runner.invoke(app, ["operations", "--help"])
        assert result.exit_code == 0

    def test_operations_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --format json exits 0 and outputs dict-shaped JSON."""
        result = runner.invoke(app, ["operations", "--format", "json"])
        assert result.exit_code == 0
        assert "orchestrate" in result.stdout
        assert "govern" in result.stdout

    def test_operations_operation_filter_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation orchestrate exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "orchestrate"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestClosurePack:
    """E2E tests for closure-pack command."""

    def test_closure_pack_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """closure-pack exits 0 with valid DAG."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        result = runner.invoke(app, ["closure-pack", "--cd", str(project)])
        assert result.exit_code == 0

    def test_closure_pack_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """closure-pack --help exits 0."""
        result = runner.invoke(app, ["closure-pack", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPsCockpitHelp:
    """E2E tests for ps and cockpit --help."""

    def test_ps_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """ps --help exits 0."""
        result = runner.invoke(app, ["ps", "--help"])
        assert result.exit_code == 0

    def test_cockpit_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """cockpit --help exits 0."""
        result = runner.invoke(app, ["cockpit", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestMcpUpDownHelp:
    """E2E tests for mcp up and mcp down --help."""

    def test_mcp_up_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp up --help exits 0."""
        result = runner.invoke(app, ["mcp", "up", "--help"])
        assert result.exit_code == 0

    def test_mcp_down_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp down --help exits 0."""
        result = runner.invoke(app, ["mcp", "down", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestModelsSubcommandHelp:
    """E2E tests for models subcommand --help."""

    def test_models_refresh_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """models refresh --help exits 0."""
        result = runner.invoke(app, ["models", "refresh", "--help"])
        assert result.exit_code == 0

    def test_models_contract_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """models contract --help exits 0."""
        result = runner.invoke(app, ["models", "contract", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestTyperAppHelp:
    """E2E tests for orchestrate, govern, recover, observe, plan --help."""

    def test_orchestrate_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "--help"])
        assert result.exit_code == 0

    def test_govern_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern --help exits 0."""
        result = runner.invoke(app, ["govern", "--help"])
        assert result.exit_code == 0

    def test_recover_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """recover --help exits 0."""
        result = runner.invoke(app, ["recover", "--help"])
        assert result.exit_code == 0

    def test_observe_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe --help exits 0."""
        result = runner.invoke(app, ["observe", "--help"])
        assert result.exit_code == 0

    def test_plan_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan --help exits 0."""
        result = runner.invoke(app, ["plan", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestHistoryPolicyCliproxyHelp:
    """E2E tests for history subcommands, policy show, cliproxy login --help."""

    def test_history_list_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """history list --help exits 0."""
        result = runner.invoke(app, ["history", "list", "--help"])
        assert result.exit_code == 0

    def test_history_events_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """history events --help exits 0."""
        result = runner.invoke(app, ["history", "events", "--help"])
        assert result.exit_code == 0

    def test_history_verify_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """history verify --help exits 0."""
        result = runner.invoke(app, ["history", "verify", "--help"])
        assert result.exit_code == 0

    def test_policy_show_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """policy show --help exits 0."""
        result = runner.invoke(app, ["policy", "show", "--help"])
        assert result.exit_code == 0

    def test_cliproxy_login_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """cliproxy login --help exits 0."""
        result = runner.invoke(app, ["cliproxy", "login", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestCliproxyEnsureConfigHelp:
    """E2E tests for cliproxy ensure-config --help."""

    def test_cliproxy_ensure_config_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """cliproxy ensure-config --help exits 0."""
        result = runner.invoke(app, ["cliproxy", "ensure-config", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestLoginRooKiloE2E:
    """E2E tests for thegent login roo and thegent login kilo."""

    def test_login_roo_exits_zero_with_mock_cliproxy(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """thegent login roo exits 0 when CLIProxy binary accepts -roo-login."""
        mock_binary = tmp_path / "cli-proxy-api-plus"
        mock_binary.write_text('#!/bin/sh\nfor arg in "$@"; do\n  [ "$arg" = "-roo-login" ] && exit 0\ndone\nexit 1\n')
        mock_binary.chmod(0o755)
        config_path = tmp_path / "config.yaml"
        config_path.write_text("port: 8317\n")
        monkeypatch.setenv("THGENT_CLIPROXY_BINARY", str(mock_binary))
        monkeypatch.setenv("THGENT_CLIPROXY_CONFIG_PATH", str(config_path))
        result = runner.invoke(app, ["login", "roo"])
        assert result.exit_code == 0, result.stderr or result.stdout

    def test_login_kilo_exits_zero_with_mock_cliproxy(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """thegent login kilo exits 0 when CLIProxy binary accepts -kilo-login."""
        mock_binary = tmp_path / "cli-proxy-api-plus"
        mock_binary.write_text('#!/bin/sh\nfor arg in "$@"; do\n  [ "$arg" = "-kilo-login" ] && exit 0\ndone\nexit 1\n')
        mock_binary.chmod(0o755)
        config_path = tmp_path / "config.yaml"
        config_path.write_text("port: 8317\n")
        monkeypatch.setenv("THGENT_CLIPROXY_BINARY", str(mock_binary))
        monkeypatch.setenv("THGENT_CLIPROXY_CONFIG_PATH", str(config_path))
        result = runner.invoke(app, ["login", "kilo"])
        assert result.exit_code == 0, result.stderr or result.stdout

    def test_cliproxy_login_roo_exits_zero_with_mock(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """thegent cliproxy login roo exits 0 when CLIProxy accepts -roo-login."""
        mock_binary = tmp_path / "cli-proxy-api-plus"
        mock_binary.write_text('#!/bin/sh\nfor arg in "$@"; do\n  [ "$arg" = "-roo-login" ] && exit 0\ndone\nexit 1\n')
        mock_binary.chmod(0o755)
        config_path = tmp_path / "config.yaml"
        config_path.write_text("port: 8317\n")
        monkeypatch.setenv("THGENT_CLIPROXY_BINARY", str(mock_binary))
        monkeypatch.setenv("THGENT_CLIPROXY_CONFIG_PATH", str(config_path))
        result = runner.invoke(app, ["cliproxy", "login", "roo"])
        assert result.exit_code == 0, result.stderr or result.stdout


@pytest.mark.e2e
class TestTyperAliasHelp:
    """E2E tests for typer alias paths (orchestrate/govern/observe subcommands)."""

    def test_orchestrate_run_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate run --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "run", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_ps_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate ps --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "ps", "--help"])
        assert result.exit_code == 0

    def test_govern_verify_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern verify --help exits 0 (alias for history verify)."""
        result = runner.invoke(app, ["govern", "verify", "--help"])
        assert result.exit_code == 0

    def test_observe_cockpit_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe cockpit --help exits 0."""
        result = runner.invoke(app, ["observe", "cockpit", "--help"])
        assert result.exit_code == 0

    def test_observe_archive_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe archive --help exits 0."""
        result = runner.invoke(app, ["observe", "archive", "--help"])
        assert result.exit_code == 0

    def test_observe_benchmark_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe benchmark --help exits 0."""
        result = runner.invoke(app, ["observe", "benchmark", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestRecoverPlanGovernAliasHelp:
    """E2E tests for recover, plan, and govern alias paths --help."""

    def test_recover_reconcile_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """recover reconcile --help exits 0 (alias for dag reconcile)."""
        result = runner.invoke(app, ["recover", "reconcile", "--help"])
        assert result.exit_code == 0

    def test_plan_list_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan list --help exits 0 (alias for dag list)."""
        result = runner.invoke(app, ["plan", "list", "--help"])
        assert result.exit_code == 0

    def test_plan_validate_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan validate --help exits 0 (alias for dag validate)."""
        result = runner.invoke(app, ["plan", "validate", "--help"])
        assert result.exit_code == 0

    def test_plan_run_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan run --help exits 0 (alias for dag run)."""
        result = runner.invoke(app, ["plan", "run", "--help"])
        assert result.exit_code == 0

    def test_govern_closure_pack_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern closure-pack --help exits 0 (alias for closure-pack)."""
        result = runner.invoke(app, ["govern", "closure-pack", "--help"])
        assert result.exit_code == 0

    def test_govern_show_policy_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern show-policy --help exits 0 (alias for policy show)."""
        result = runner.invoke(app, ["govern", "show-policy", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOrchestrateRecoverObserveRemainingHelp:
    """E2E tests for remaining orchestrate, recover, observe alias --help."""

    def test_orchestrate_bg_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate bg --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "bg", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_inspect_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate inspect --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "inspect", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_logs_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate logs --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "logs", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_wait_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate wait --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "wait", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_stop_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate stop --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "stop", "--help"])
        assert result.exit_code == 0

    def test_recover_stop_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """recover stop --help exits 0 (alias for stop)."""
        result = runner.invoke(app, ["recover", "stop", "--help"])
        assert result.exit_code == 0

    def test_observe_status_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe status --help exits 0."""
        result = runner.invoke(app, ["observe", "status", "--help"])
        assert result.exit_code == 0

    def test_observe_logs_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe logs --help exits 0."""
        result = runner.invoke(app, ["observe", "logs", "--help"])
        assert result.exit_code == 0

    def test_observe_wait_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe wait --help exits 0."""
        result = runner.invoke(app, ["observe", "wait", "--help"])
        assert result.exit_code == 0

    def test_observe_inspect_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe inspect --help exits 0."""
        result = runner.invoke(app, ["observe", "inspect", "--help"])
        assert result.exit_code == 0

    def test_observe_history_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe history --help exits 0 (alias for history list)."""
        result = runner.invoke(app, ["observe", "history", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanSyncCheckpointAndOperationsFilters:
    """E2E tests for plan sync/checkpoint help and operations --operation filters."""

    def test_plan_sync_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan sync --help exits 0 (alias for dag sync)."""
        result = runner.invoke(app, ["plan", "sync", "--help"])
        assert result.exit_code == 0

    def test_plan_checkpoint_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan checkpoint --help exits 0 (alias for dag checkpoint)."""
        result = runner.invoke(app, ["plan", "checkpoint", "--help"])
        assert result.exit_code == 0

    def test_operations_operation_govern_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation govern exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "govern"])
        assert result.exit_code == 0

    def test_operations_operation_recover_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation recover exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "recover"])
        assert result.exit_code == 0

    def test_operations_operation_observe_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation observe exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "observe"])
        assert result.exit_code == 0

    def test_operations_operation_plan_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation plan exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "plan"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOperationsInvalidAndClosurePackNoDag:
    """E2E tests for operations invalid operation and closure-pack without DAG."""

    def test_operations_invalid_operation_exits_one(self) -> None:
        # @trace FR-CLI-001
        """operations --operation invalid_name exits 1 with message."""
        result = runner.invoke(app, ["operations", "--operation", "invalid_operation_xyz"])
        assert result.exit_code == 1
        assert "Unknown operation" in result.stdout or "invalid" in result.stdout.lower()

    def test_closure_pack_no_dag_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """closure-pack with project lacking .factory/dag-session.md exits 1."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".factory").mkdir()
        # No dag-session.md
        result = runner.invoke(app, ["closure-pack", "--cd", str(project)])
        assert result.exit_code == 1
        assert "DAG not found" in result.stdout or "dag" in result.stdout.lower()


@pytest.mark.e2e
class TestHistoryLegacy:
    """E2E tests for hidden history-legacy command."""

    def test_history_legacy_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """history-legacy --help exits 0."""
        result = runner.invoke(app, ["history-legacy", "--help"])
        assert result.exit_code == 0

    def test_history_legacy_empty_registry_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history-legacy with empty registry exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history-legacy", "--limit", "5"])
        assert result.exit_code == 0

    def test_history_legacy_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history-legacy --format json with empty registry exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history-legacy", "--format", "json", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernRemainingAliasHelp:
    """E2E tests for remaining govern alias paths --help."""

    def test_govern_contracts_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern contracts --help exits 0 (alias for session-contracts)."""
        result = runner.invoke(app, ["govern", "contracts", "--help"])
        assert result.exit_code == 0

    def test_govern_session_contracts_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern session-contracts --help exits 0."""
        result = runner.invoke(app, ["govern", "session-contracts", "--help"])
        assert result.exit_code == 0

    def test_govern_health_gate_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern health-gate --help exits 0 (alias for session-contract-health-gate)."""
        result = runner.invoke(app, ["govern", "health-gate", "--help"])
        assert result.exit_code == 0

    def test_govern_health_report_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern health-report --help exits 0 (alias for session-contract-health-report)."""
        result = runner.invoke(app, ["govern", "health-report", "--help"])
        assert result.exit_code == 0

    def test_govern_health_trend_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern health-trend --help exits 0 (alias for session-contract-health-trend)."""
        result = runner.invoke(app, ["govern", "health-trend", "--help"])
        assert result.exit_code == 0

    def test_govern_feedback_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern feedback --help exits 0."""
        result = runner.invoke(app, ["govern", "feedback", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernContractsExecution:
    """E2E tests for govern contracts (contract registry) execution."""

    def test_govern_contracts_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern contracts exits 0 and shows contract registry."""
        result = runner.invoke(app, ["govern", "contracts"])
        assert result.exit_code == 0
        assert "Contract" in result.stdout or "registry" in result.stdout.lower()

    def test_govern_contracts_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern contracts --format json exits 0."""
        result = runner.invoke(app, ["govern", "contracts", "--format", "json"])
        assert result.exit_code == 0
        # Output should look like JSON array (may have Rich/ANSI artifacts)
        assert "[" in result.stdout


@pytest.mark.e2e
class TestObservePlanAliasExecution:
    """E2E tests for observe and plan alias execution (not just --help)."""

    def test_observe_history_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe history exits 0 (alias for history list)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "history", "--limit", "5"])
        assert result.exit_code == 0

    def test_plan_list_empty_dag_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan list with empty DAG exits 0 (alias for dag list)."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        )
        result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestRecoverPlanAliasExecution:
    """E2E tests for recover and plan alias execution."""

    def _dag_project(self, tmp_path: Path, with_task: bool = True) -> Path:
        """Create project with dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        content = "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        if with_task:
            content += "| T1 | gemini | hello | — | pending |\n"
        (factory / "dag-session.md").write_text(content)
        return project

    def test_recover_reconcile_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """recover reconcile exits 0 with valid DAG (alias for dag reconcile)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["recover", "reconcile", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_validate_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan validate exits 0 with valid empty DAG (alias for dag validate)."""
        project = self._dag_project(tmp_path, with_task=False)
        result = runner.invoke(app, ["plan", "validate", "--cd", str(project)])
        assert result.exit_code == 0
        assert "DAG valid" in result.stdout

    def test_plan_sync_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan sync exits 0 with empty DAG (alias for dag sync)."""
        project = self._dag_project(tmp_path, with_task=False)
        result = runner.invoke(app, ["plan", "sync", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_checkpoint_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """plan checkpoint exits 0 with DAG (alias for dag checkpoint)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "checkpoint", "--cd", str(project), "--reason", "E2E test"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanRunDryRun:
    """E2E tests for plan run --dry-run (alias for dag run --dry-run)."""

    def _dag_project(self, tmp_path: Path, with_task: bool = True) -> Path:
        """Create project with dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        content = "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        if with_task:
            content += "| T1 | gemini | hello | — | pending |\n"
        (factory / "dag-session.md").write_text(content)
        return project

    def test_plan_run_dry_run_no_ready_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan run --dry-run with no ready tasks exits 0."""
        project = self._dag_project(tmp_path, with_task=False)
        result = runner.invoke(app, ["plan", "run", "--dry-run", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_run_dry_run_with_ready_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan run --dry-run with ready task exits 0 and shows would run."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "run", "--dry-run", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Would run" in result.stdout or "T1" in result.stdout


@pytest.mark.e2e
class TestObserveDriftTrendProbeHelp:
    """E2E tests for observe drift, trend, probe --help."""

    def test_observe_drift_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe drift --help exits 0."""
        result = runner.invoke(app, ["observe", "drift", "--help"])
        assert result.exit_code == 0

    def test_observe_trend_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe trend --help exits 0 (alias for session-contract-health-trend)."""
        result = runner.invoke(app, ["observe", "trend", "--help"])
        assert result.exit_code == 0

    def test_observe_probe_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe probe --help exits 0 (alias for dag probe)."""
        result = runner.invoke(app, ["observe", "probe", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernConformanceMigrationHelp:
    """E2E tests for govern conformance and migration --help."""

    def test_govern_conformance_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern conformance --help exits 0."""
        result = runner.invoke(app, ["govern", "conformance", "--help"])
        assert result.exit_code == 0

    def test_govern_migration_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern migration --help exits 0."""
        result = runner.invoke(app, ["govern", "migration", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestObserveDriftTrendExecution:
    """E2E tests for observe drift and observe trend execution."""

    def test_observe_drift_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe drift exits 0 with empty session dir."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "drift", "--window", "10"])
        assert result.exit_code == 0

    def test_observe_trend_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe trend exits 0 with empty snapshots (alias for session-contract-health-trend)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["observe", "trend", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanReadyStatusCheckpointsExecution:
    """E2E tests for plan ready, status, checkpoints execution (aliases for dag)."""

    def _dag_project(self, tmp_path: Path, with_task: bool = True) -> Path:
        """Create project with dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        content = "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n|----|-------|--------|------------|--------|\n"
        if with_task:
            content += "| T1 | gemini | hello | — | pending |\n"
        (factory / "dag-session.md").write_text(content)
        return project

    def test_plan_ready_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan ready exits 0 with empty DAG (alias for dag ready)."""
        project = self._dag_project(tmp_path, with_task=False)
        result = runner.invoke(app, ["plan", "ready", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_status_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan status exits 0 with empty DAG (alias for dag status)."""
        project = self._dag_project(tmp_path, with_task=False)
        result = runner.invoke(app, ["plan", "status", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_checkpoints_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """plan checkpoints exits 0 (alias for dag checkpoints)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["plan", "checkpoints", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanObserveProbeExecution:
    """E2E tests for plan probe and observe probe execution (aliases for dag probe)."""

    def _dag_project(self, tmp_path: Path) -> Path:
        """Create project with dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_probe_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan probe exits 0 with DAG (alias for dag probe)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "probe", "--cd", str(project)])
        assert result.exit_code == 0

    def test_observe_probe_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """observe probe exits 0 with DAG (alias for dag probe)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["observe", "probe", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestRecoverPlanRollbackAndPlanMutateHelp:
    """E2E tests for recover/plan rollback and plan add/remove/update/cancel --help."""

    def test_recover_rollback_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """recover rollback --help exits 0 (alias for dag rollback)."""
        result = runner.invoke(app, ["recover", "rollback", "--help"])
        assert result.exit_code == 0

    def test_plan_rollback_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan rollback --help exits 0 (alias for dag rollback)."""
        result = runner.invoke(app, ["plan", "rollback", "--help"])
        assert result.exit_code == 0

    def test_plan_add_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan add --help exits 0 (alias for dag add)."""
        result = runner.invoke(app, ["plan", "add", "--help"])
        assert result.exit_code == 0

    def test_plan_remove_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan remove --help exits 0 (alias for dag remove)."""
        result = runner.invoke(app, ["plan", "remove", "--help"])
        assert result.exit_code == 0

    def test_plan_update_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan update --help exits 0 (alias for dag update)."""
        result = runner.invoke(app, ["plan", "update", "--help"])
        assert result.exit_code == 0

    def test_plan_cancel_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan cancel --help exits 0 (alias for dag cancel)."""
        result = runner.invoke(app, ["plan", "cancel", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanAddExecution:
    """E2E tests for plan add execution (alias for dag add)."""

    def test_plan_add_then_list_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan add creates task; plan list shows it."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG Session\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
        )

        add_result = runner.invoke(
            app,
            ["plan", "add", "T1", "gemini", "test prompt", "--cd", str(project)],
        )
        assert add_result.exit_code == 0
        assert "Added task T1" in add_result.stdout

        list_result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "T1" in list_result.stdout
        assert "gemini" in list_result.stdout


@pytest.mark.e2e
class TestPlanRemoveUpdateCancelExecution:
    """E2E tests for plan remove, update, cancel execution (aliases for dag)."""

    def _project_with_task(self, tmp_path: Path, task_id: str = "T1") -> Path:
        """Create project with single task."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG Session\n\n## Tasks\n\n"
            "| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            f"| {task_id} | gemini | test | — | pending |\n"
        )
        return project

    def test_plan_remove_then_list_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan remove removes task; plan list shows No tasks."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["plan", "remove", "T1", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Removed task T1" in result.stdout

        list_result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "No tasks" in list_result.stdout

    def test_plan_update_status_then_list_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan update --status done updates task; plan list shows done."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["plan", "update", "T1", "--status", "done", "--cd", str(project)])
        assert result.exit_code == 0

        list_result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "done" in list_result.stdout

    def test_plan_cancel_then_list_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan cancel sets status cancelled; plan list shows cancelled."""
        project = self._project_with_task(tmp_path)
        result = runner.invoke(app, ["plan", "cancel", "T1", "--cd", str(project)])
        assert result.exit_code == 0
        assert "Cancelled task T1" in result.stdout

        list_result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert list_result.exit_code == 0
        assert "cancelled" in list_result.stdout


@pytest.mark.e2e
class TestRecoverPlanRollbackExecution:
    """E2E tests for recover rollback and plan rollback execution (aliases for dag rollback)."""

    def _dag_project(self, tmp_path: Path) -> Path:
        """Create project with dag-session.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_checkpoint_then_rollback_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """plan checkpoint creates checkpoint; plan rollback restores DAG."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        project = self._dag_project(tmp_path)

        ckpt_result = runner.invoke(
            app,
            ["plan", "checkpoint", "--cd", str(project), "--reason", "E2E rollback test"],
        )
        assert ckpt_result.exit_code == 0
        match = re.search(r"ckpt_[a-f0-9]+", ckpt_result.stdout)
        assert match, "Checkpoint ID should be printed"
        ckpt_id = match.group(0)

        rollback_result = runner.invoke(app, ["plan", "rollback", ckpt_id, "--cd", str(project)])
        assert rollback_result.exit_code == 0
        assert "rolled back" in rollback_result.stdout.lower()

    def test_recover_rollback_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """recover rollback restores DAG to checkpoint (alias for dag rollback)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        project = self._dag_project(tmp_path)

        ckpt_result = runner.invoke(
            app,
            ["plan", "checkpoint", "--cd", str(project), "--reason", "E2E recover rollback"],
        )
        assert ckpt_result.exit_code == 0
        match = re.search(r"ckpt_[a-f0-9]+", ckpt_result.stdout)
        assert match, "Checkpoint ID should be printed"
        ckpt_id = match.group(0)

        rollback_result = runner.invoke(app, ["recover", "rollback", ckpt_id, "--cd", str(project)])
        assert rollback_result.exit_code == 0
        assert "rolled back" in rollback_result.stdout.lower()


@pytest.mark.e2e
class TestGovernAliasExecution:
    """E2E tests for govern alias execution (session-contracts, health-gate, health-report)."""

    def test_govern_session_contracts_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern session-contracts exits 0 with empty sessions (alias for session-contracts)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "session-contracts"])
        assert result.exit_code == 0

    def test_govern_health_gate_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern health-gate exits 0 with empty sessions (alias for session-contract-health-gate)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "health-gate"])
        assert result.exit_code == 0

    def test_govern_health_report_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern health-report exits 0 with empty sessions (alias for session-contract-health-report)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "health-report"])
        assert result.exit_code == 0

    def test_govern_health_trend_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern health-trend exits 0 with empty snapshots (alias for session-contract-health-trend)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["govern", "health-trend", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestObserveAliasExecution:
    """E2E tests for observe alias execution (cockpit, archive, benchmark)."""

    def test_observe_cockpit_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe cockpit exits 0 (alias for cockpit)."""
        result = runner.invoke(app, ["observe", "cockpit"])
        assert result.exit_code == 0

    def test_observe_archive_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe archive exits 0 (alias for archive)."""
        result = runner.invoke(app, ["observe", "archive", "--days", "7"])
        assert result.exit_code == 0

    def test_observe_benchmark_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """observe benchmark exits 0 (alias for benchmark)."""
        result = runner.invoke(app, ["observe", "benchmark"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOrchestrateGovernAliasExecution:
    """E2E tests for orchestrate ps and govern migration execution."""

    def test_orchestrate_ps_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate ps exits 0 with empty sessions (alias for ps)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "ps"])
        assert result.exit_code == 0

    def test_govern_migration_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern migration csm csm-v1 exits 0 (evaluates known contract version)."""
        result = runner.invoke(app, ["govern", "migration", "csm", "csm-v1"])
        assert result.exit_code == 0
        assert "active" in result.stdout.lower() or "allowed" in result.stdout.lower()

    def test_govern_migration_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern migration --format json exits 0."""
        result = runner.invoke(app, ["govern", "migration", "csm", "csm-v1", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "allowed" in data
        assert "status" in data


@pytest.mark.e2e
class TestOrchestrateObserveRecoverStatusLogsWaitStopAlias:
    """E2E tests for orchestrate/observe/recover alias execution (status, logs, wait, stop)."""

    def test_orchestrate_status_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate status with unknown session exits 2 (alias for status)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "status", "session_unknown_e2e_orch"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_observe_status_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe status with unknown session exits 2 (alias for status)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "status", "session_unknown_e2e_obs"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_orchestrate_logs_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate logs with unknown session exits 2 (alias for logs)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "logs", "session_unknown_e2e_logs"])
        assert result.exit_code == 2

    def test_orchestrate_wait_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate wait with unknown session exits 2 (alias for wait)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "wait", "session_unknown_e2e_wait"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr

    def test_recover_stop_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """recover stop with unknown session exits 2 (alias for stop)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["recover", "stop", "session_unknown_e2e_stop"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestOrchestrateObserveInspectAlias:
    """E2E tests for orchestrate inspect and observe inspect alias execution."""

    def test_orchestrate_inspect_owner_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate inspect --owner with no sessions exits 0 (alias for inspect)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "inspect", "--owner", "e2e_orch_inspect_xyz"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout

    def test_observe_inspect_owner_no_sessions_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe inspect --owner with no sessions exits 0 (alias for inspect)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "inspect", "--owner", "e2e_obs_inspect_xyz"])
        assert result.exit_code == 0
        assert "No sessions" in result.stdout

    def test_observe_logs_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe logs with unknown session exits 2 (alias for logs)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "logs", "session_unknown_e2e_obs_logs"])
        assert result.exit_code == 2

    def test_observe_wait_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe wait with unknown session exits 2 (alias for wait)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "wait", "session_unknown_e2e_obs_wait"])
        assert result.exit_code == 2
        assert "Session not found" in result.stderr


@pytest.mark.e2e
class TestGovernConformanceExecution:
    """E2E tests for govern conformance execution (adapter conformance suite)."""

    def test_govern_conformance_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern conformance runs adapter conformance suite and exits 0 when all pass."""
        result = runner.invoke(app, ["govern", "conformance"])
        assert result.exit_code == 0
        assert "PASS" in result.stdout or "Passed" in result.stdout or "passed" in result.stdout

    def test_govern_conformance_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern conformance --format json exits 0 when all pass."""
        result = runner.invoke(app, ["govern", "conformance", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "passed" in data
        assert "total" in data
        assert "results" in data


@pytest.mark.e2e
class TestPlanAnalyzeExecution:
    """E2E tests for plan analyze execution."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_analyze_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """plan analyze --help exits 0."""
        result = runner.invoke(app, ["plan", "analyze", "--help"])
        assert result.exit_code == 0

    def test_plan_analyze_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_analyze_pert_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --pert with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--pert", "--cd", str(project)])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernVerifyShowPolicyFeedbackExecution:
    """E2E tests for govern verify, show-policy, feedback, closure-pack."""

    def test_govern_verify_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern verify exits 0 (alias for history verify)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "verify"])
        assert result.exit_code == 0

    def test_govern_verify_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern verify --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "verify", "--format", "json"])
        assert result.exit_code == 0

    def test_govern_show_policy_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern show-policy exits 0 (alias for policy show)."""
        result = runner.invoke(app, ["govern", "show-policy"])
        assert result.exit_code == 0

    def test_govern_feedback_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern feedback records feedback and exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["govern", "feedback", "e2e_feedback_run_xyz", "1.0", "--note", "E2E"],
        )
        assert result.exit_code == 0

    def test_govern_closure_pack_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern closure-pack --help exits 0."""
        result = runner.invoke(app, ["govern", "closure-pack", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestObserveKpisModesOperationsExecution:
    """E2E tests for observe kpis, modes, operations."""

    def test_observe_kpis_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe kpis exits 0 with empty session dir."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "kpis", "--limit", "10"])
        assert result.exit_code == 0

    def test_observe_kpis_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe kpis --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "kpis", "--format", "json"])
        assert result.exit_code == 0

    def test_modes_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """modes exits 0."""
        result = runner.invoke(app, ["modes"])
        assert result.exit_code == 0

    def test_operations_operation_plan_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation plan exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "plan"])
        assert result.exit_code == 0

    def test_operations_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --format json exits 0."""
        result = runner.invoke(app, ["operations", "--format", "json"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOrchestratePauseResumeAlias:
    """E2E tests for orchestrate pause/resume with unknown session."""

    def test_orchestrate_pause_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate pause with unknown session exits nonzero."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "pause", "session_unknown_e2e_pause"])
        assert result.exit_code != 0
        assert "Session not found" in result.stderr or "not found" in result.stderr.lower()

    def test_orchestrate_resume_unknown_session_exits_nonzero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate resume with unknown session exits nonzero."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["orchestrate", "resume", "session_unknown_e2e_resume"])
        assert result.exit_code != 0
        assert "Session not found" in result.stderr or "not found" in result.stderr.lower()


@pytest.mark.e2e
class TestOrchestrateRunBgHelpAndUnknownAgent:
    """E2E tests for orchestrate run/bg help and unknown agent."""

    def test_orchestrate_run_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate run --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "run", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_bg_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate bg --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "bg", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_run_unknown_agent_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate run with unknown agent exits 1."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        monkeypatch.chdir(project)
        result = runner.invoke(
            app,
            ["orchestrate", "run", "test prompt", "nonexistent_agent_xyz", "-d", str(project)],
        )
        assert result.exit_code == 1

    def test_orchestrate_bg_unknown_agent_exits_nonzero_or_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """orchestrate bg with unknown agent exits 0 or 1 (bg may return before agent validation)."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.chdir(project)
        result = runner.invoke(
            app,
            ["orchestrate", "bg", "test prompt", "nonexistent_agent_xyz", "-d", str(project)],
        )
        # bg may exit 0 immediately (spawns background) or 1 if agent validated upfront
        assert result.exit_code in (0, 1)


@pytest.mark.e2e
class TestCliproxyMcpLoginHelpExecution:
    """E2E tests for cliproxy, mcp, login help."""

    def test_cliproxy_login_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """cliproxy login --help exits 0."""
        result = runner.invoke(app, ["cliproxy", "login", "--help"])
        assert result.exit_code == 0

    def test_orchestrate_login_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """orchestrate login --help exits 0."""
        result = runner.invoke(app, ["orchestrate", "login", "--help"])
        assert result.exit_code == 0

    def test_mcp_install_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp install --help exits 0."""
        result = runner.invoke(app, ["mcp", "install", "--help"])
        assert result.exit_code == 0

    def test_mcp_up_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp up --help exits 0."""
        result = runner.invoke(app, ["mcp", "up", "--help"])
        assert result.exit_code == 0

    def test_mcp_down_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp down --help exits 0."""
        result = runner.invoke(app, ["mcp", "down", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanListFormatExecution:
    """E2E tests for plan list format execution."""

    def test_plan_list_format_md_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan list --format md with DAG exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
        )
        result = runner.invoke(app, ["plan", "list", "--format", "md", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_list_empty_dag_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan list with empty DAG exits 0."""
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
        )
        result = runner.invoke(app, ["plan", "list", "--cd", str(project)])
        assert result.exit_code == 0
        assert "No tasks" in result.stdout


@pytest.mark.e2e
class TestHistoryEventsAliasExecution:
    """E2E tests for history events and observe history alias."""

    def test_history_events_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "events", "--format", "json", "--limit", "3"])
        assert result.exit_code == 0

    def test_observe_history_limit_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe history --limit exits 0 (alias for history list)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "history", "--limit", "3"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestClosurePackArchiveExecution:
    """E2E tests for closure-pack and archive execution."""

    def test_closure_pack_no_dag_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """closure-pack --cd to dir without DAG exits 1."""
        bare = tmp_path / "bare"
        bare.mkdir()
        (bare / ".git").mkdir()
        monkeypatch.chdir(bare)
        result = runner.invoke(app, ["closure-pack", "--cd", str(bare)])
        assert result.exit_code == 1
        assert "DAG" in result.stdout or "DAG" in result.stderr

    def test_govern_closure_pack_no_dag_exits_one(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern closure-pack --cd to dir without DAG exits 1."""
        bare = tmp_path / "bare"
        bare.mkdir()
        (bare / ".git").mkdir()
        result = runner.invoke(app, ["govern", "closure-pack", "--cd", str(bare)])
        assert result.exit_code == 1

    def test_archive_days_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """archive --days 1 exits 0."""
        result = runner.invoke(app, ["archive", "--days", "1"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernDataProtectionExecution:
    """E2E tests for govern data-protection execution."""

    def test_govern_data_protection_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern data-protection exits 0."""
        result = runner.invoke(app, ["govern", "data-protection"])
        assert result.exit_code == 0

    def test_govern_data_protection_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern data-protection --format json exits 0."""
        result = runner.invoke(app, ["govern", "data-protection", "--format", "json"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "session_dir" in data or "permissions_restricted" in data


@pytest.mark.e2e
class TestPlanAnalyzeDeepOptions:
    """E2E tests for plan analyze --resources, --continuity, --format json."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_analyze_resources_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --resources with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--resources", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_analyze_continuity_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --continuity with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--continuity", "--cd", str(project)])
        assert result.exit_code == 0

    def test_plan_analyze_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --format json with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "pert" in data or "resources" in data or "continuity" in data or "tasks" in str(data).lower()


@pytest.mark.e2e
class TestObserveDriftDeepOptions:
    """E2E tests for observe drift --format json and custom budgets."""

    def test_observe_drift_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe drift --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "drift", "--format", "json", "--window", "10"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "issues" in data or "budget" in data

    def test_observe_drift_custom_budgets_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe drift with custom structural/semantic budget exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "observe",
                "drift",
                "--structural-budget",
                "10",
                "--semantic-budget",
                "15",
                "--window",
                "5",
            ],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestObserveSummaryCustom:
    """E2E tests for observe summary with richer operator options."""

    def test_observe_summary_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary --format json exits 0 in empty telemetry."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["observe", "summary", "--format", "json", "--limit", "20"])
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        assert payload["payload_type"] == "observe_summary"
        assert payload["payload_schema_version"] == "observe-summary-schema-v1"
        assert "kpis" in payload
        assert "drift" in payload
        assert "escalation" in payload

    def test_observe_summary_custom_budgets_provider_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary accepts custom budgets and provider filter."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            [
                "observe",
                "summary",
                "--format",
                "json",
                "--provider",
                "gemini",
                "--structural-budget",
                "6",
                "--semantic-budget",
                "9",
                "--top-escalations",
                "3",
                "--drift-window",
                "12",
            ],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        assert payload["payload_type"] == "observe_summary"
        assert payload["payload_schema_version"] == "observe-summary-schema-v1"
        assert payload["drift"]["structural_budget_pct"] == 6.0
        assert payload["drift"]["semantic_budget_pct"] == 9.0
        assert payload["escalation"]["provider"] == "gemini"

    def test_observe_summary_trend_samples_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary reports trend payload when trend samples are requested."""
        session_dir = tmp_path / "sessions"
        snapshot_file = tmp_path / "observe_summary_snapshots.jsonl"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_file))
        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "3", "--limit", "25"],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        assert payload["trend_summary"]["enabled"] is True
        assert payload["trend_summary"]["trend_samples_requested"] == 3
        assert payload["trend_summary"]["baseline_available"] in (True, False)
        assert "history_sample_count" in payload["trend_summary"]
        assert payload["generated_query"]["trend_samples"] == 3

    def test_observe_summary_trend_samples_rich_exposes_projection(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """observe summary --format rich exposes trend projection metadata."""
        session_dir = tmp_path / "sessions"
        snapshot_file = tmp_path / "observe_summary_snapshots.jsonl"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_file))
        if snapshot_file.exists():
            snapshot_file.unlink()
        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "rich", "--trend-samples", "2"],
        )
        assert result.exit_code == 0
        out = result.stdout.lower()
        assert "trend:" in out
        assert "trend_samples_requested=2" in out
        assert "trend_effective_samples=2" in out
        assert "generated_query=" in out

    def test_observe_summary_trend_samples_one_disables_trend(self) -> None:
        # @trace FR-CLI-001
        """observe summary treats --trend-samples 1 as disabled trend mode."""
        _, trend_health_signature = _expected_trend_health_signature()
        result = runner.invoke(app, ["observe", "summary", "--format", "json", "--trend-samples", "1"])
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is False
        assert trend["trend_samples_requested"] == 1
        assert trend["trend_effective_samples"] == 0
        assert trend["history_sample_count"] == 0
        assert payload["generated_query"]["trend_samples"] == 1
        assert trend["trend_snapshot_health"] == "disabled"
        assert trend["trend_snapshot_health_score"] is None
        assert trend["trend_snapshot_health_breakdown"]["policy_signature"] == trend_health_signature
        assert trend["trend_snapshot_health_breakdown"]["policy"]["healthy_threshold"] == 95
        assert trend["trend_snapshot_health_breakdown"]["policy"]["warning_threshold"] == 80
        assert trend["trend_snapshot_health_breakdown"]["policy"]["degraded_threshold"] == 50

    def test_observe_summary_trend_samples_two_reports_effective(self) -> None:
        # @trace FR-CLI-001
        """observe summary enables trend mode for --trend-samples 2."""
        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "2"],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is True
        assert trend["trend_samples_requested"] == 2
        assert trend["trend_effective_samples"] == 2
        assert payload["generated_query"]["trend_samples"] == 2

    def test_observe_summary_trend_samples_zero_disables_trend(self) -> None:
        # @trace FR-CLI-001
        """observe summary treats --trend-samples 0 as disabled trend mode."""
        _, trend_health_signature = _expected_trend_health_signature()
        result = runner.invoke(app, ["observe", "summary", "--format", "json", "--trend-samples", "0"])
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is False
        assert trend["trend_samples_requested"] == 0
        assert trend["trend_effective_samples"] == 0
        assert payload["generated_query"]["trend_samples"] == 0
        assert trend["trend_snapshot_health"] == "disabled"
        assert trend["trend_snapshot_health_breakdown"]["policy_signature"] == trend_health_signature

    def test_observe_summary_trend_samples_large_enables_and_tracks_effective_samples(self) -> None:
        # @trace FR-CLI-001
        """observe summary accepts large trend sample requests and reflects requested/effective."""
        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "9999"],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is True
        assert trend["trend_samples_requested"] == 9999
        assert trend["trend_effective_samples"] == 9999
        assert payload["generated_query"]["trend_samples"] == 9999

    def test_observe_summary_trend_enabled_without_baseline_keeps_stable_shape(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary with enabled trend but no history exposes stable null delta fields."""
        session_dir = tmp_path / "sessions"
        snapshot_file = tmp_path / "observe_summary_snapshots.jsonl"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_file))
        # Ensure no prior snapshots exist
        if snapshot_file.exists():
            snapshot_file.unlink()

        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "3"],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is True
        assert trend["trend_samples_requested"] == 3
        assert trend["trend_effective_samples"] == 3
        assert trend["history_sample_count"] == 0
        assert trend["baseline_available"] is False
        assert trend["baseline_captured_at_utc"] is None
        assert trend["total_events_delta"] is None
        assert trend["fallback_rate_delta"] is None
        assert trend["success_rate_delta"] is None
        assert trend["avg_confidence_delta"] is None
        assert trend["structural_drift_pct_delta"] is None
        assert trend["semantic_drift_pct_delta"] is None
        assert trend["drift_structural_rate_pct_delta"] is None
        assert trend["drift_semantic_rate_pct_delta"] is None
        assert trend["backlog_count_delta"] is None
        assert trend["past_sla_count_delta"] is None
        assert payload["generated_query"]["trend_samples"] == 3

    def test_observe_summary_trend_scope_signature_is_visible(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary exposes deterministic trend scope signature for query parity."""
        session_dir = tmp_path / "sessions"
        snapshot_file = tmp_path / "observe_summary_snapshots.jsonl"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_file))
        if snapshot_file.exists():
            snapshot_file.unlink()

        result = runner.invoke(
            app,
            [
                "observe",
                "summary",
                "--format",
                "json",
                "--trend-samples",
                "3",
                "--limit",
                "25",
                "--top-escalations",
                "7",
                "--provider",
                "cursor",
            ],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        scope = json.loads(trend["scope_key_json"])
        assert scope["provider"] == "cursor"
        assert scope["limit"] == 25
        assert scope["top_escalations"] == 7
        assert trend["scope_signature"]
        assert payload["generated_query"]["trend_scope_signature"] == trend["scope_signature"]
        assert trend["trend_snapshot_ids"] == []
        assert trend["trend_snapshot_ids_csv"] == ""
        assert trend["trend_snapshot_window_seconds"] is None

    def test_observe_summary_invalid_trend_samples_is_rejected_by_cli(self) -> None:
        # @trace FR-CLI-001
        """observe summary rejects non-integer --trend-samples via CLI validation."""
        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "abc"],
        )
        assert result.exit_code != 0

    def test_observe_summary_trend_history_metadata_replayed_from_snapshots(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe summary replays trend timing and coverage metadata from prior snapshots."""
        trend_health_policy = {
            "healthy_threshold": 95,
            "warning_threshold": 80,
            "degraded_threshold": 50,
            "min_coverage_pct": 80.0,
            "max_invalid_timestamps": 0,
            "coverage_penalty_per_pct": 1.25,
            "deficit_penalty_per_missing_sample": 15.0,
            "invalid_timestamp_penalty_per_event": 12.0,
            "stale_penalty": 8.0,
            "critical_penalty": 20.0,
            "unknown_or_future_penalty": 30.0,
            "gap_penalty": 10.0,
            "missing_baseline_penalty": 45.0,
        }
        trend_health_signature = hashlib.sha256(
            json.dumps(trend_health_policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        session_dir = tmp_path / "sessions"
        snapshot_file = tmp_path / "observe_summary_snapshots.jsonl"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_file))

        scope = {
            "payload_type": "observe_summary",
            "provider": None,
            "drift_window": 50,
            "structural_budget_pct": 5.0,
            "semantic_budget_pct": 10.0,
            "limit": 500,
            "top_escalations": 10,
        }
        scope_json = json.dumps(scope, sort_keys=True, separators=(",", ":"))
        scope_signature = hashlib.sha256(scope_json.encode("utf-8")).hexdigest()

        snapshot_records = [
            {
                "record_type": "observe_summary_snapshot",
                "captured_at_utc": "2026-01-01T00:00:00+00:00",
                "scope_key": scope,
                "scope_signature": scope_signature,
                "scope_key_json": scope_json,
                "trend_scope_signature": scope_signature,
                "trend_previous_samples_requested": 2,
                "trend_snapshot_expected_count": 2,
                "trend_snapshot_deficit": 0,
                "trend_snapshot_interval_seconds_avg": 86400,
                "trend_snapshot_interval_seconds_min": 86400,
                "trend_snapshot_interval_seconds_max": 86400,
                "trend_snapshot_gap_count": 1,
                "trend_snapshot_invalid_timestamps": 0,
                "trend_snapshot_coverage_pct": 100.0,
                "trend_snapshot_freshness_bucket": "critical",
                "trend_snapshot_freshness_seconds": 86400,
                "schema_version": "observe-summary-schema-v1",
                "payload_type": "observe_summary",
                "status": "healthy",
                "total_events": 5,
                "fallback_rate": 0.0,
                "success_rate": 1.0,
                "avg_confidence": 0.9,
                "structural_drift_pct": 0.0,
                "semantic_drift_pct": 0.0,
                "drift_structural_rate_pct": 0.0,
                "drift_semantic_rate_pct": 0.0,
                "backlog_count": 0,
                "past_sla_count": 0,
                "provider": None,
                "drift_structural_budget_pct": 5.0,
                "drift_semantic_budget_pct": 10.0,
            },
            {
                "record_type": "observe_summary_snapshot",
                "captured_at_utc": "2026-01-02T00:00:00+00:00",
                "scope_key": scope,
                "scope_signature": scope_signature,
                "scope_key_json": scope_json,
                "trend_scope_signature": scope_signature,
                "trend_previous_samples_requested": 2,
                "trend_snapshot_expected_count": 2,
                "trend_snapshot_deficit": 0,
                "trend_snapshot_interval_seconds_avg": 86400,
                "trend_snapshot_interval_seconds_min": 86400,
                "trend_snapshot_interval_seconds_max": 86400,
                "trend_snapshot_gap_count": 1,
                "trend_snapshot_invalid_timestamps": 0,
                "trend_snapshot_coverage_pct": 100.0,
                "trend_snapshot_freshness_bucket": "critical",
                "trend_snapshot_freshness_seconds": 0,
                "schema_version": "observe-summary-schema-v1",
                "payload_type": "observe_summary",
                "status": "healthy",
                "total_events": 8,
                "fallback_rate": 0.0,
                "success_rate": 1.0,
                "avg_confidence": 0.9,
                "structural_drift_pct": 0.0,
                "semantic_drift_pct": 0.0,
                "drift_structural_rate_pct": 0.0,
                "drift_semantic_rate_pct": 0.0,
                "backlog_count": 0,
                "past_sla_count": 0,
                "provider": None,
                "drift_structural_budget_pct": 5.0,
                "drift_semantic_budget_pct": 10.0,
            },
        ]
        snapshot_file.write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in snapshot_records),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["observe", "summary", "--format", "json", "--trend-samples", "3"],
        )
        assert result.exit_code == 0
        payload = _loads(result.stdout)
        trend = payload["trend_summary"]
        assert trend["enabled"] is True
        assert trend["trend_samples_requested"] == 3
        assert trend["trend_effective_samples"] == 3
        assert trend["trend_snapshot_ids"] == [
            "2026-01-02T00:00:00+00:00",
            "2026-01-01T00:00:00+00:00",
        ]
        assert trend["trend_snapshot_window_seconds"] == 86400
        assert trend["trend_snapshot_interval_seconds_avg"] == 86400
        assert trend["trend_snapshot_interval_seconds_min"] == 86400
        assert trend["trend_snapshot_interval_seconds_max"] == 86400
        assert trend["trend_snapshot_gap_count"] == 1
        assert trend["trend_snapshot_invalid_timestamps"] == 0
        assert trend["trend_snapshot_coverage_pct"] == 100.0
        assert trend["trend_snapshot_freshness_bucket"] in {"fresh", "warm", "stale", "critical"}
        assert trend["trend_snapshot_health"] in {"good", "warning", "degraded", "critical"}
        assert trend["trend_snapshot_health_breakdown"]["policy_signature"] == trend_health_signature
        assert trend["trend_snapshot_health_breakdown"]["policy"]["healthy_threshold"] == 95
        assert trend["trend_snapshot_health_breakdown"]["policy"]["warning_threshold"] == 80
        assert trend["trend_snapshot_health_breakdown"]["policy"]["degraded_threshold"] == 50
        assert trend["trend_snapshot_health_breakdown"]["policy"]["min_coverage_pct"] == 80.0
        assert trend["trend_snapshot_health_breakdown"]["policy"]["max_invalid_timestamps"] == 0
        assert trend["trend_snapshot_health_score"] is not None
        assert isinstance(trend["trend_snapshot_health_score"], int)
        assert isinstance(trend["trend_snapshot_recommendations"], list)
        assert trend["trend_snapshot_deficit"] == 0
        assert trend["trend_snapshot_expected_count"] == 2
        assert trend["trend_sampling_mode"] == "enabled"
        assert trend["trend_snapshot_freshness_seconds"] is not None
        assert trend["trend_snapshot_freshness_seconds"] >= 0


@pytest.mark.e2e
class TestGovernConformanceCheckDrift:
    """E2E tests for govern conformance --check-drift."""

    def test_govern_conformance_check_drift_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern conformance --check-drift with empty session dir exits 0 or 1."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "conformance", "--check-drift"])
        # May exit 0 (all pass, no drift) or 1 (drift detected)
        assert result.exit_code in (0, 1)


@pytest.mark.e2e
class TestDagPlanReadyFormatJson:
    """E2E tests for dag ready and plan ready --format json."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_dag_ready_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag ready --format json with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "ready", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "ready_task_ids" in data

    def test_plan_ready_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan ready --format json with DAG exits 0 (alias for dag ready)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "ready", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "ready_task_ids" in data


@pytest.mark.e2e
class TestPlanDagListStatusFormatJson:
    """E2E tests for plan/dag list and status --format json."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_dag_list_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag list --format json with DAG exits 0 and returns tasks array."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "list", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) >= 1

    def test_plan_list_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan list --format json with DAG exits 0 (alias for dag list)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "list", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_dag_status_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag status --format json with DAG exits 0 (tasks may be empty if no session_id)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "status", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_plan_status_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan status --format json with DAG exits 0 (alias for dag status)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "status", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)


@pytest.mark.e2e
class TestHistoryEventsRunId:
    """E2E tests for history events --run-id."""

    def test_history_events_run_id_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history events --run-id with non-existent run exits 0 (empty result)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(
            app,
            ["history", "events", "--run-id", "e2e_nonexistent_run_xyz", "--limit", "5"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestMcpServiceHelp:
    """E2E tests for mcp service --help."""

    def test_mcp_service_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """mcp service --help exits 0."""
        result = runner.invoke(app, ["mcp", "service", "--help"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestArchiveDomainOption:
    """E2E tests for archive --domain option."""

    def test_archive_domain_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """archive --domain with --days exits 0."""
        result = runner.invoke(app, ["archive", "--domain", "e2e_test", "--days", "1"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestOperationsRecoverFilter:
    """E2E tests for operations --operation recover."""

    def test_operations_operation_recover_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation recover exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "recover"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestObserveTrendDeepOptions:
    """E2E tests for observe trend --payload-type, --format json, --all."""

    def test_observe_trend_payload_type_gate_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe trend --payload-type session_contract_health_gate exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            [
                "observe",
                "trend",
                "--payload-type",
                "session_contract_health_gate",
                "--limit",
                "5",
            ],
        )
        assert result.exit_code == 0

    def test_observe_trend_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe trend --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["observe", "trend", "--format", "json", "--limit", "5"])
        assert result.exit_code == 0
        # Output may have ANSI/control chars; assert JSON-like structure present
        assert "{" in result.stdout or "[" in result.stdout

    def test_observe_trend_all_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe trend --all exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(app, ["observe", "trend", "--all", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernMigrationAllContracts:
    """E2E tests for govern migration with task-tool and zen contracts."""

    def test_govern_migration_task_tool_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern migration task-tool task-tool-18 exits 0."""
        result = runner.invoke(app, ["govern", "migration", "task-tool", "task-tool-18"])
        assert result.exit_code == 0

    def test_govern_migration_zen_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern migration zen zen-rich-v1 exits 0."""
        result = runner.invoke(app, ["govern", "migration", "zen", "zen-rich-v1"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernEscalateListExecution:
    """E2E tests for govern escalate list."""

    def test_govern_escalate_list_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern escalate list --help exits 0."""
        result = runner.invoke(app, ["govern", "escalate", "list", "--help"])
        assert result.exit_code == 0

    def test_govern_escalate_list_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern escalate list exits 0 with empty queue."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "escalate", "list", "--limit", "5"])
        assert result.exit_code == 0

    def test_govern_escalate_list_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern escalate list --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "escalate", "list", "--format", "json", "--limit", "5"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert isinstance(data, list) or "items" in str(data).lower()


@pytest.mark.e2e
class TestHistoryListFormatJson:
    """E2E tests for history list --format json."""

    def test_history_list_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """history list --format json exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["history", "list", "--format", "json", "--limit", "5"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert isinstance(data, list)


@pytest.mark.e2e
class TestObserveTrendOwnerOption:
    """E2E tests for observe trend --owner."""

    def test_observe_trend_owner_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """observe trend --owner exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        snapshot_path = tmp_path / "health-snapshots.jsonl"
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        monkeypatch.setenv("THGENT_HEALTH_SNAPSHOT_PATH", str(snapshot_path))
        result = runner.invoke(
            app,
            ["observe", "trend", "--owner", "e2e_trend_owner_xyz", "--limit", "5"],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestModesFormatJson:
    """E2E tests for modes --format json and --mode filter."""

    def test_modes_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """modes --format json exits 0."""
        result = runner.invoke(app, ["modes", "--format", "json"])
        assert result.exit_code == 0
        # Output may have ANSI/control chars; assert JSON-like structure present
        assert "[" in result.stdout or "{" in result.stdout
        assert "mode" in result.stdout.lower()

    def test_modes_mode_filter_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """modes --mode sequential_delegation exits 0."""
        result = runner.invoke(app, ["modes", "--mode", "sequential_delegation"])
        assert result.exit_code == 0

    def test_modes_mode_filter_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """modes --mode parallel_consensus --format json exits 0."""
        result = runner.invoke(app, ["modes", "--mode", "parallel_consensus", "--format", "json"])
        assert result.exit_code == 0
        # Output may have ANSI/control chars; assert mode present
        assert "parallel_consensus" in result.stdout


@pytest.mark.e2e
class TestPlanAnalyzePertFormatJson:
    """E2E tests for plan analyze --pert --format json."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_analyze_pert_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --pert --format json with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(app, ["plan", "analyze", "--pert", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert isinstance(data, dict)


@pytest.mark.e2e
class TestDagListEmptyFormatJson:
    """E2E tests for dag list --format json with empty DAG."""

    def _empty_dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
        )
        return project

    def test_dag_list_empty_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """dag list --format json with empty DAG exits 0 and returns tasks: []."""
        project = self._empty_dag_project(tmp_path)
        result = runner.invoke(app, ["dag", "list", "--format", "json", "--cd", str(project)])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert "tasks" in data
        assert data["tasks"] == []


@pytest.mark.e2e
class TestGovernSweepFormatJson:
    """E2E tests for govern sweep --format json."""

    def test_govern_sweep_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern sweep --format json exits 0 with empty session dir."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "sweep", "--format", "json", "--drift-window", "10"])
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert isinstance(data, dict)


@pytest.mark.e2e
class TestOperationsOrchestrateFormatJson:
    """E2E tests for operations --operation orchestrate --format json."""

    def test_operations_orchestrate_format_json_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """operations --operation orchestrate --format json exits 0."""
        result = runner.invoke(app, ["operations", "--operation", "orchestrate", "--format", "json"])
        assert result.exit_code == 0
        # Output may have ANSI/control chars; assert JSON-like structure
        assert "{" in result.stdout or "[" in result.stdout
        assert "orchestrate" in result.stdout.lower()


@pytest.mark.e2e
class TestPlanAnalyzeCombinedOverlays:
    """E2E tests for plan analyze with combined overlays (--pert --resources)."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_analyze_pert_resources_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --pert --resources with DAG exits 0 (combined overlays)."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(
            app,
            [
                "plan",
                "analyze",
                "--pert",
                "--resources",
                "--cd",
                str(project),
            ],
        )
        assert result.exit_code == 0

    def test_plan_analyze_resources_continuity_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --resources --continuity with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(
            app,
            [
                "plan",
                "analyze",
                "--resources",
                "--continuity",
                "--cd",
                str(project),
            ],
        )
        assert result.exit_code == 0


@pytest.mark.e2e
class TestGovernEscalateAddResolve:
    """E2E tests for govern escalate add and resolve."""

    def test_govern_escalate_add_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern escalate add --help exits 0."""
        result = runner.invoke(app, ["govern", "escalate", "add", "--help"])
        assert result.exit_code == 0

    def test_govern_escalate_resolve_help_exits_zero(self) -> None:
        # @trace FR-CLI-001
        """govern escalate resolve --help exits 0."""
        result = runner.invoke(app, ["govern", "escalate", "resolve", "--help"])
        assert result.exit_code == 0

    def test_govern_escalate_add_then_resolve_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern escalate add then resolve exits 0 (add to queue, then resolve)."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        add_result = runner.invoke(
            app,
            [
                "govern",
                "escalate",
                "add",
                "e2e_escalate_run_xyz",
                "E2E test reason",
                "--sla",
                "60",
            ],
        )
        assert add_result.exit_code == 0
        resolve_result = runner.invoke(app, ["govern", "escalate", "resolve", "e2e_escalate_run_xyz"])
        assert resolve_result.exit_code == 0

    def test_govern_escalate_list_past_sla_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern escalate list --past-sla exits 0 with empty queue."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "escalate", "list", "--past-sla", "--limit", "5"])
        assert result.exit_code == 0


@pytest.mark.e2e
class TestPlanAnalyzeAllOverlays:
    """E2E tests for plan analyze with all overlays combined (--pert --resources --continuity)."""

    def _dag_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        (project / ".git").mkdir()
        factory = project / ".factory"
        factory.mkdir()
        (factory / "dag-session.md").write_text(
            "# DAG\n\n## Tasks\n\n| id | agent | prompt | depends_on | status |\n"
            "|----|-------|--------|------------|--------|\n"
            "| T1 | gemini | hello | — | pending |\n"
        )
        return project

    def test_plan_analyze_all_overlays_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --pert --resources --continuity with DAG exits 0."""
        project = self._dag_project(tmp_path)
        result = runner.invoke(
            app,
            [
                "plan",
                "analyze",
                "--pert",
                "--resources",
                "--continuity",
                "--cd",
                str(project),
            ],
        )
        assert result.exit_code == 0

    def test_plan_analyze_all_overlays_format_json_exits_zero(self, tmp_path: Path) -> None:
        # @trace FR-CLI-001
        """plan analyze --pert --resources --continuity --format json exits 0."""
        project = self._dag_project(tmp_path)
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
                "--cd",
                str(project),
            ],
        )
        assert result.exit_code == 0
        data = _loads(result.stdout)
        assert isinstance(data, dict)


@pytest.mark.e2e
class TestGovernConformanceFormatJson:
    """E2E tests for govern conformance --format json."""

    def test_govern_conformance_format_json_exits_zero(
        # @trace FR-CLI-001
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """govern conformance --format json with empty session dir exits 0."""
        session_dir = tmp_path / "sessions"
        session_dir.mkdir(parents=True)
        monkeypatch.setenv("THGENT_SESSION_DIR", str(session_dir))
        result = runner.invoke(app, ["govern", "conformance", "--format", "json", "--drift-window", "10"])
        assert result.exit_code == 0
        # Output may have ANSI; assert JSON-like structure
        assert "{" in result.stdout or "[" in result.stdout
