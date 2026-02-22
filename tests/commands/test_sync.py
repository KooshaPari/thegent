"""Tests for thegent.commands.sync — status, push, pull, reset subcommands.

Covers the four new subcommands added in the impl-sync-command work-stream
item.  All filesystem access is isolated to tmp_path; no live repo state is
touched.

Traces to: FR-SYNC-021 through FR-SYNC-040
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from thegent.commands.sync import (
    OperationResult,
    SyncCommand,
    SyncOperationStatus,
    SyncResult,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


def _make_cmd(tmp_path: Path, **kwargs: object) -> SyncCommand:
    """Return a SyncCommand rooted at a throwaway temp directory."""
    return SyncCommand(project_root=tmp_path, **kwargs)


def _agent_dir(tmp_path: Path, names: list[str]) -> Path:
    d = tmp_path / "agents"
    d.mkdir(exist_ok=True)
    for name in names:
        (d / f"{name}.md").write_text(f"# {name}\n", encoding="utf-8")
    return d


def _hooks_dir(tmp_path: Path, scripts: list[str]) -> Path:
    d = tmp_path / "hooks"
    d.mkdir(exist_ok=True)
    for name in scripts:
        (d / f"{name}.sh").write_text(f"#!/bin/sh\n# {name}\n", encoding="utf-8")
    return d


def _hook_config(hooks_dir: Path, registered: list[str]) -> Path:
    lines = ["hooks:"]
    for name in registered:
        lines.append(f"  {name}:")
        lines.append(f"    description: {name}")
    path = hooks_dir / "hook-config.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# SyncResult — new fields
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncResultNewFields:
    """Verify files_synced and errors properties added to SyncResult."""

    def test_files_synced_sums_changes(self) -> None:
        # @trace FR-SYNC-021
        r = SyncResult(
            operations=[
                OperationResult("a", SyncOperationStatus.SUCCESS, changes=["x", "y"]),
                OperationResult("b", SyncOperationStatus.SUCCESS, changes=["z"]),
            ]
        )
        assert r.files_synced == 3

    def test_files_synced_empty_operations(self) -> None:
        # @trace FR-SYNC-021
        r = SyncResult()
        assert r.files_synced == 0

    def test_errors_flattened_from_failed_ops(self) -> None:
        # @trace FR-SYNC-022
        r = SyncResult(
            operations=[
                OperationResult("a", SyncOperationStatus.FAILED, errors=["err-a"]),
                OperationResult("b", SyncOperationStatus.FAILED, errors=["err-b1", "err-b2"]),
            ]
        )
        assert r.errors == ["err-a", "err-b1", "err-b2"]

    def test_errors_empty_when_all_success(self) -> None:
        # @trace FR-SYNC-022
        r = SyncResult(
            operations=[
                OperationResult("a", SyncOperationStatus.SUCCESS),
                OperationResult("b", SyncOperationStatus.SUCCESS),
            ]
        )
        assert r.errors == []

    def test_to_dict_includes_files_synced_and_errors(self) -> None:
        # @trace FR-SYNC-023
        r = SyncResult(
            operations=[
                OperationResult("a", SyncOperationStatus.SUCCESS, changes=["f1"]),
            ]
        )
        d = r.to_dict()
        assert "files_synced" in d
        assert "errors" in d
        assert d["files_synced"] == 1
        assert d["errors"] == []


# ---------------------------------------------------------------------------
# status()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncStatus:
    def test_returns_operation_result(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-024
        cmd = _make_cmd(tmp_path)
        op = cmd.status()
        assert isinstance(op, OperationResult)

    def test_status_ok_when_no_drift(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-024
        hd = _hooks_dir(tmp_path, ["quality-gate"])
        _hook_config(hd, ["quality-gate"])
        cmd = SyncCommand(
            project_root=tmp_path,
            hooks_dir=hd,
            hook_config_path=hd / "hook-config.yaml",
        )
        op = cmd.status()
        assert op.ok is True
        assert op.details["has_drift"] is False

    def test_status_reports_unregistered_hooks_as_drift(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-025
        hd = _hooks_dir(tmp_path, ["new-hook", "registered"])
        _hook_config(hd, ["registered"])
        cmd = SyncCommand(
            project_root=tmp_path,
            hooks_dir=hd,
            hook_config_path=hd / "hook-config.yaml",
        )
        op = cmd.status()
        assert op.ok is True  # status itself succeeds
        assert op.details["has_drift"] is True
        assert "new-hook" in op.details["unregistered_hooks"]

    def test_status_reports_orphaned_config_as_drift(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-025
        hd = _hooks_dir(tmp_path, ["real-hook"])
        _hook_config(hd, ["real-hook", "ghost"])
        cmd = SyncCommand(
            project_root=tmp_path,
            hooks_dir=hd,
            hook_config_path=hd / "hook-config.yaml",
        )
        op = cmd.status()
        assert op.details["has_drift"] is True
        assert "ghost" in op.details["orphaned_hooks"]

    def test_status_includes_local_agents_list(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-026
        _agent_dir(tmp_path, ["claude", "gemini"])
        cmd = _make_cmd(tmp_path)
        op = cmd.status()
        assert sorted(op.details["local_agents"]) == ["claude", "gemini"]

    def test_status_no_hooks_dir_still_ok(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-026
        cmd = _make_cmd(tmp_path)
        op = cmd.status()
        assert op.ok is True
        assert op.details["has_drift"] is False

    def test_status_exception_returns_failed(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-027
        cmd = _make_cmd(tmp_path)
        with patch.object(cmd, "_discover_agent_files", side_effect=RuntimeError("disk error")):
            op = cmd.status()
        assert op.status == SyncOperationStatus.FAILED
        assert "disk error" in op.errors[0]

    def test_status_changes_list_when_drift(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-027
        hd = _hooks_dir(tmp_path, ["unregistered-hook"])
        _hook_config(hd, [])
        cmd = SyncCommand(
            project_root=tmp_path,
            hooks_dir=hd,
            hook_config_path=hd / "hook-config.yaml",
        )
        op = cmd.status()
        assert any("unregistered" in c for c in op.changes)


# ---------------------------------------------------------------------------
# push()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncPush:
    def test_returns_operation_result(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-028
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        assert isinstance(op, OperationResult)

    def test_push_succeeds_with_default_target(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-028
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        assert op.ok is True
        assert op.operation == "push"

    def test_push_with_explicit_target(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-029
        cmd = _make_cmd(tmp_path)
        op = cmd.push(target="https://sync.example.com")
        assert op.ok is True
        assert op.details["target"] == "https://sync.example.com"

    def test_push_respects_env_var(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-029
        cmd = _make_cmd(tmp_path)
        with patch.dict(os.environ, {"THGENT_SYNC_REMOTE": "remote-server"}):
            op = cmd.push()
        assert op.details["target"] == "remote-server"

    def test_push_env_var_overridden_by_explicit_target(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-029
        cmd = _make_cmd(tmp_path)
        with patch.dict(os.environ, {"THGENT_SYNC_REMOTE": "remote-server"}):
            op = cmd.push(target="explicit-target")
        assert op.details["target"] == "explicit-target"

    def test_push_lists_agent_files_in_changes(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-030
        _agent_dir(tmp_path, ["alpha", "beta"])
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        change_paths = [c.replace("push: ", "") for c in op.changes]
        assert any("agents/alpha.md" in p for p in change_paths)
        assert any("agents/beta.md" in p for p in change_paths)

    def test_push_lists_hook_files_in_changes(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-030
        _hooks_dir(tmp_path, ["quality-gate"])
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        assert any("hooks/quality-gate.sh" in c for c in op.changes)

    def test_push_stub_flag_set(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-031
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        assert op.details.get("stub") is True

    def test_push_message_contains_file_count(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-031
        _agent_dir(tmp_path, ["agent-a"])
        cmd = _make_cmd(tmp_path)
        op = cmd.push()
        assert "1" in op.message  # at least 1 file (the agent)


# ---------------------------------------------------------------------------
# pull()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncPull:
    def test_returns_operation_result(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-032
        cmd = _make_cmd(tmp_path)
        op = cmd.pull()
        assert isinstance(op, OperationResult)

    def test_pull_succeeds_with_default_source(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-032
        cmd = _make_cmd(tmp_path)
        op = cmd.pull()
        assert op.ok is True
        assert op.operation == "pull"

    def test_pull_with_explicit_source(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-033
        cmd = _make_cmd(tmp_path)
        op = cmd.pull(source="https://sync.example.com")
        assert op.ok is True
        assert op.details["source"] == "https://sync.example.com"

    def test_pull_respects_env_var(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-033
        cmd = _make_cmd(tmp_path)
        with patch.dict(os.environ, {"THGENT_SYNC_REMOTE": "remote-server"}):
            op = cmd.pull()
        assert op.details["source"] == "remote-server"

    def test_pull_env_var_overridden_by_explicit_source(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-033
        cmd = _make_cmd(tmp_path)
        with patch.dict(os.environ, {"THGENT_SYNC_REMOTE": "should-be-ignored"}):
            op = cmd.pull(source="explicit-source")
        assert op.details["source"] == "explicit-source"

    def test_pull_stub_flag_set(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-034
        cmd = _make_cmd(tmp_path)
        op = cmd.pull()
        assert op.details.get("stub") is True

    def test_pull_files_pulled_is_empty_stub(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-034
        cmd = _make_cmd(tmp_path)
        op = cmd.pull()
        assert op.details["files_pulled"] == []


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncReset:
    def test_returns_operation_result(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-035
        cmd = _make_cmd(tmp_path)
        op = cmd.reset()
        assert isinstance(op, OperationResult)

    def test_reset_succeeds_empty_dir(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-035
        cmd = _make_cmd(tmp_path)
        op = cmd.reset()
        assert op.ok is True
        assert op.operation == "reset"

    def test_reset_stub_flag_set(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-036
        cmd = _make_cmd(tmp_path)
        op = cmd.reset()
        assert op.details.get("stub") is True

    def test_reset_no_files_when_work_stream_missing(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-036
        cmd = _make_cmd(tmp_path)
        op = cmd.reset()
        # work_stream doesn't exist so nothing to reset
        work_stream_str = str((tmp_path / "docs" / "reference" / "WORK_STREAM.md").relative_to(tmp_path))
        assert work_stream_str not in op.details["files_would_reset"]

    def test_reset_reports_work_stream_when_present(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-037
        ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
        ws.parent.mkdir(parents=True)
        ws.write_text("# WORK_STREAM\n", encoding="utf-8")
        cmd = SyncCommand(project_root=tmp_path, work_stream_path=ws)
        op = cmd.reset()
        assert op.ok is True
        # The work stream path should appear in the reset candidate list
        assert any("WORK_STREAM" in f for f in op.details["files_would_reset"])

    def test_reset_reports_hook_config_when_present(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-037
        hd = _hooks_dir(tmp_path, ["quality-gate"])
        cfg = _hook_config(hd, ["quality-gate"])
        cmd = SyncCommand(
            project_root=tmp_path,
            hooks_dir=hd,
            hook_config_path=cfg,
        )
        op = cmd.reset()
        assert op.ok is True
        assert any("hook-config" in f for f in op.details["files_would_reset"])

    def test_reset_changes_list_reflects_files_would_reset(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-038
        ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
        ws.parent.mkdir(parents=True)
        ws.write_text("# WS\n", encoding="utf-8")
        cmd = SyncCommand(project_root=tmp_path, work_stream_path=ws)
        op = cmd.reset()
        assert len(op.changes) == len(op.details["files_would_reset"])
        assert all(c.startswith("reset:") for c in op.changes)

    def test_reset_does_not_modify_files(self, tmp_path: Path) -> None:
        # @trace FR-SYNC-038
        ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
        ws.parent.mkdir(parents=True)
        original_content = "# WORK_STREAM\noriginal content\n"
        ws.write_text(original_content, encoding="utf-8")
        cmd = SyncCommand(project_root=tmp_path, work_stream_path=ws)
        cmd.reset()
        # File must be unchanged — reset is currently a stub
        assert ws.read_text(encoding="utf-8") == original_content


# ---------------------------------------------------------------------------
# CLI integration — sync_app subcommands registered in main
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSyncCLIRegistration:
    """Verify the new CLI subcommands are registered and invokable.

    We invoke ``sync_app`` directly (not the top-level ``app``) to avoid
    pre-existing issues in unrelated sub-apps (e.g. the audit app) that
    cause typer's annotation evaluation to fail at the root level.
    """

    def test_status_command_exists(self) -> None:
        # @trace FR-SYNC-039
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_push_command_exists(self) -> None:
        # @trace FR-SYNC-039
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["--help"])
        assert result.exit_code == 0
        assert "push" in result.output

    def test_pull_command_exists(self) -> None:
        # @trace FR-SYNC-040
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["--help"])
        assert result.exit_code == 0
        assert "pull" in result.output

    def test_reset_command_exists(self) -> None:
        # @trace FR-SYNC-040
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["--help"])
        assert result.exit_code == 0
        assert "reset" in result.output

    def test_status_subcommand_help(self) -> None:
        # @trace FR-SYNC-039
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["status", "--help"])
        assert result.exit_code == 0

    def test_push_subcommand_help(self) -> None:
        # @trace FR-SYNC-039
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["push", "--help"])
        assert result.exit_code == 0
        assert "--target" in result.output

    def test_pull_subcommand_help(self) -> None:
        # @trace FR-SYNC-040
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["pull", "--help"])
        assert result.exit_code == 0
        assert "--source" in result.output

    def test_reset_subcommand_help(self) -> None:
        # @trace FR-SYNC-040
        from typer.testing import CliRunner

        from thegent.main import sync_app

        runner = CliRunner()
        result = runner.invoke(sync_app, ["reset", "--help"])
        assert result.exit_code == 0
        assert "--yes" in result.output
