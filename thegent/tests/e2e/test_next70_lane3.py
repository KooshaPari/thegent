"""E2E help coverage tests for plan and sync command lanes."""

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_plan_incorporate_help() -> None:
    result = runner.invoke(app, ["plan", "incorporate", "--help"])
    assert result.exit_code == 0
    assert "incorporate" in result.stdout


@pytest.mark.e2e
def test_plan_claim_help() -> None:
    result = runner.invoke(app, ["plan", "claim", "--help"])
    assert result.exit_code == 0
    assert "claim" in result.stdout


@pytest.mark.e2e
def test_plan_complete_help() -> None:
    result = runner.invoke(app, ["plan", "complete", "--help"])
    assert result.exit_code == 0
    assert "complete" in result.stdout


@pytest.mark.e2e
def test_plan_verify_workstream_help() -> None:
    result = runner.invoke(app, ["plan", "verify-workstream", "--help"])
    assert result.exit_code == 0
    assert "verify-workstream" in result.stdout


@pytest.mark.e2e
def test_plan_progress_help() -> None:
    result = runner.invoke(app, ["plan", "progress", "--help"])
    assert result.exit_code == 0
    assert "progress" in result.stdout


@pytest.mark.e2e
def test_plan_sessions_help() -> None:
    result = runner.invoke(app, ["plan", "sessions", "--help"])
    assert result.exit_code == 0
    assert "sessions" in result.stdout


@pytest.mark.e2e
def test_plan_harness_status_help() -> None:
    result = runner.invoke(app, ["plan", "harness-status", "--help"])
    assert result.exit_code == 0
    assert "harness-status" in result.stdout


@pytest.mark.e2e
def test_sync_help() -> None:
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "sync" in result.stdout


@pytest.mark.e2e
def test_sync_all_help() -> None:
    result = runner.invoke(app, ["sync", "all", "--help"])
    assert result.exit_code == 0
    assert "all" in result.stdout


@pytest.mark.e2e
def test_sync_work_stream_help() -> None:
    result = runner.invoke(app, ["sync", "work-stream", "--help"])
    assert result.exit_code == 0
    assert "work-stream" in result.stdout
