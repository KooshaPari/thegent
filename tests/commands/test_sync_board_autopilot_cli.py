from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from typer.testing import CliRunner

from thegent.cli.apps.sync import app
from thegent.commands.sync import OperationResult, SyncOperationStatus


class _SyncCommandStub:
    def __init__(self, *, project_root):
        _ = project_root
        self._op = OperationResult(operation="board", status=SyncOperationStatus.SUCCESS, message="ok")

    def sync_board(
        self,
        *,
        board_id: str | None,
        source: str,
        dry_run: bool,
        shadow_mode: bool,
        wl_start: int | None,
        wl_end: int | None,
        write_batch_size: int,
    ) -> OperationResult:
        assert board_id == "42"
        assert source == "github"
        assert dry_run is False
        assert shadow_mode is False
        assert wl_start is None
        assert wl_end is None
        assert write_batch_size == 50
        return OperationResult(
            operation="board",
            status=SyncOperationStatus.SUCCESS,
            message="Board sync complete: 1 item(s) updated on github.",
            changes=["synced: WL-009"],
            details={"board_id": "42", "source": "github", "items_synced": 1},
        )


class _SyncCommandDryRunStub:
    def __init__(self, *, project_root):
        _ = project_root
        self._op = OperationResult(operation="board", status=SyncOperationStatus.DRY_RUN, message="dry")

    def sync_board(
        self,
        *,
        board_id: str | None,
        source: str,
        dry_run: bool,
        shadow_mode: bool,
        wl_start: int | None,
        wl_end: int | None,
        write_batch_size: int,
    ) -> OperationResult:
        assert board_id == "42"
        assert source == "linear"
        assert dry_run is True
        assert shadow_mode is False
        assert wl_start is None
        assert wl_end is None
        assert write_batch_size == 50
        return OperationResult(
            operation="board",
            status=SyncOperationStatus.DRY_RUN,
            message="Board sync dry-run: would sync 2 item(s) to linear.",
            changes=["[dry-run] WL-010: BACKLOG"],
        )


class _SyncCommandFailedStub:
    def __init__(self, *, project_root):
        _ = project_root
        self._op = OperationResult(operation="board", status=SyncOperationStatus.FAILED, message="failed")

    def sync_board(
        self,
        *,
        board_id: str | None,
        source: str,
        dry_run: bool,
        shadow_mode: bool,
        wl_start: int | None,
        wl_end: int | None,
        write_batch_size: int,
    ) -> OperationResult:
        _ = (board_id, source, dry_run, shadow_mode, wl_start, wl_end, write_batch_size)
        return OperationResult(
            operation="board",
            status=SyncOperationStatus.FAILED,
            message="Board sync failed: boom",
            errors=["boom"],
        )


class _SyncCommandRangeStub:
    def __init__(self, *, project_root):
        _ = project_root
        self._op = OperationResult(operation="board", status=SyncOperationStatus.DRY_RUN, message="dry")

    def sync_board(
        self,
        *,
        board_id: str | None,
        source: str,
        dry_run: bool,
        shadow_mode: bool,
        wl_start: int | None,
        wl_end: int | None,
        write_batch_size: int,
    ) -> OperationResult:
        assert board_id == "42"
        assert source == "github"
        assert dry_run is True
        assert shadow_mode is False
        assert wl_start == 184
        assert wl_end == 188
        assert write_batch_size == 3
        return OperationResult(
            operation="board",
            status=SyncOperationStatus.DRY_RUN,
            message="Board sync dry-run: would sync 2 item(s) to github.",
            changes=["[dry-run] WL-184: ...", "[dry-run] WL-188: ..."],
        )


class _SyncCommandDeadLetterReplayStub:
    def __init__(self, *, project_root):
        _ = project_root

    def replay_dead_letters(
        self,
        *,
        source: str | None,
        board_id: str | None,
        limit: int,
        dry_run: bool,
    ) -> OperationResult:
        assert source == "github"
        assert board_id == "42"
        assert limit == 2
        assert dry_run is False
        return OperationResult(
            operation="dead-letter-replay",
            status=SyncOperationStatus.SUCCESS,
            message="Dead-letter replay complete: replayed=1, failed=0.",
            details={"replayed": 1, "failed": 0, "selected": 1},
            changes=["replayed: WL-213"],
        )


@pytest.mark.unit
def test_sync_board_success_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thegent.commands.sync.SyncCommand", _SyncCommandStub)

    result = CliRunner().invoke(app, ["board", "--board", "42", "--source", "github"])

    assert result.exit_code == 0
    assert "Board sync complete" in result.stdout
    assert "synced: WL-009" in result.stdout


@pytest.mark.unit
def test_sync_board_dry_run_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thegent.commands.sync.SyncCommand", _SyncCommandDryRunStub)

    result = CliRunner().invoke(app, ["board", "--board", "42", "--source", "linear", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry-run" in result.stdout
    assert "WL-010" in result.stdout


@pytest.mark.unit
def test_sync_board_failed_path_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thegent.commands.sync.SyncCommand", _SyncCommandFailedStub)

    result = CliRunner().invoke(app, ["board", "--board", "42", "--source", "github"])

    assert result.exit_code == 1
    assert "board sync failed" in result.stdout.lower()
    assert "boom" in result.stdout


@pytest.mark.unit
def test_sync_board_passes_wl_range_and_batch_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thegent.commands.sync.SyncCommand", _SyncCommandRangeStub)

    result = CliRunner().invoke(
        app,
        [
            "board",
            "--board",
            "42",
            "--source",
            "github",
            "--dry-run",
            "--wl-start",
            "184",
            "--wl-end",
            "188",
            "--write-batch-size",
            "3",
        ],
    )

    assert result.exit_code == 0
    assert "Dry-run" in result.stdout


@pytest.mark.unit
def test_sync_dead_letter_replay_success_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thegent.commands.sync.SyncCommand", _SyncCommandDeadLetterReplayStub)

    result = CliRunner().invoke(
        app,
        ["dead-letter-replay", "--source", "github", "--board", "42", "--limit", "2"],
    )

    assert result.exit_code == 0
    assert "replayed=1" in result.stdout
    assert "WL-213" in result.stdout


class _ValidConfig:
    cycle_interval_seconds = 300
    dry_run = False
    bootstrap_required_fields: list[str] = []
    bootstrap_mapping_cache_path = None
    bootstrap_connector = "github"

    def is_valid(self) -> bool:
        return True

    def should_sync_github(self) -> bool:
        return True

    def should_sync_linear(self) -> bool:
        return False


class _InvalidConfig:
    cycle_interval_seconds = 300
    dry_run = False
    bootstrap_required_fields: list[str] = []
    bootstrap_mapping_cache_path = None
    bootstrap_connector = "github"

    def is_valid(self) -> bool:
        return False

    def should_sync_github(self) -> bool:
        return False

    def should_sync_linear(self) -> bool:
        return False


class _RunnerStub:
    def __init__(self, config: Any):
        self.config = config
        self.performed = False

    async def _perform_sync_cycle(self) -> None:
        self.performed = True

    def get_status(self) -> dict[str, Any]:
        return {
            "health": "ok",
            "last_operation": {
                "operation_id": "op-123",
                "platform": "github",
                "items_processed": 4,
                "items_successful": 4,
                "errors": [],
            },
        }


class _ConfigSurfaceCapture:
    cycle_interval_seconds = 300
    dry_run = False
    bootstrap_required_fields: list[str] = []
    bootstrap_mapping_cache_path = None
    bootstrap_connector = "github"
    simulation_mode = False
    snapshot_retention_count = 20
    artifact_encryption_enabled = False
    artifact_encryption_key = ""
    scope_areas: list[str] | None = None
    scope_statuses: list[str] | None = None
    scope_priorities: list[str] | None = None
    scope_wl_ranges: list[str] | None = None

    def is_valid(self) -> bool:
        return True

    def should_sync_github(self) -> bool:
        return True

    def should_sync_linear(self) -> bool:
        return False


def _extract_json_payload(stdout: str) -> dict[str, Any]:
    start = stdout.find("{")
    if start < 0:
        raise ValueError(f"No JSON object found in output: {stdout!r}")
    return json.loads(stdout[start:])


@pytest.mark.unit
def test_sync_autopilot_once_json_path(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _RunnerStub(config=_ValidConfig())

    monkeypatch.setattr(
        "thegent.integrations.workstream_autosync.load_autosync_config_from_env",
        lambda: _ValidConfig(),
    )
    monkeypatch.setattr(
        "thegent.integrations.workstream_autosync.WorkstreamAutosyncRunner",
        lambda config: runner,
    )

    result = CliRunner().invoke(app, ["autopilot", "--once", "--format", "json"])

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert payload["health"] == "ok"
    assert payload["last_operation"]["operation_id"] == "op-123"
    assert runner.performed is True


@pytest.mark.unit
def test_sync_autopilot_once_surface_flags_map_to_config(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def load_config() -> _ConfigSurfaceCapture:
        return _ConfigSurfaceCapture()

    class _RunnerSurfaceStub(_RunnerStub):
        def __init__(self, config: Any):
            super().__init__(config=config)
            captured["config"] = config

    monkeypatch.setattr(
        "thegent.integrations.workstream_autosync.load_autosync_config_from_env",
        load_config,
    )
    monkeypatch.setattr(
        "thegent.integrations.workstream_autosync.WorkstreamAutosyncRunner",
        lambda config: _RunnerSurfaceStub(config),
    )

    result = CliRunner().invoke(
        app,
        [
            "autopilot",
            "--once",
            "--offline",
            "--snapshot-retention-count",
            "7",
            "--artifact-encryption",
            "--artifact-encryption-key",
            "unit-key",
        ],
    )

    assert result.exit_code == 0
    config = captured["config"]
    assert config.simulation_mode is True
    assert config.snapshot_retention_count == 7
    assert config.artifact_encryption_enabled is True
    assert config.artifact_encryption_key == "unit-key"


@pytest.mark.unit
def test_sync_autopilot_invalid_config_exits_zero_with_guidance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "thegent.integrations.workstream_autosync.load_autosync_config_from_env",
        lambda: _InvalidConfig(),
    )

    result = CliRunner().invoke(app, ["autopilot", "--once"])

    assert result.exit_code == 0
    assert "Autopilot not enabled" in result.stdout


@pytest.mark.unit
def test_sync_autopilot_rejects_invalid_interval() -> None:
    result = CliRunner().invoke(app, ["autopilot", "--once", "--interval", "5"])

    assert result.exit_code == 2
    assert "interval must be between 10 and 3600" in result.stderr


@pytest.mark.unit
def test_sync_autopilot_status_uses_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        status_path = "custom_status.json"
        with open(status_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "last_cycle_at": "2026-02-22T11:22:33",
                    "total_cycles": 7,
                    "last_error": None,
                    "health": "degraded",
                },
                handle,
            )

        monkeypatch.setenv("THGENT_AUTOSYNC_STATUS_PATH", status_path)
        result = runner.invoke(app, ["autopilot-status", "--format", "json"])

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert payload["total_cycles"] == 7
    assert payload["health"] == "degraded"


@pytest.mark.unit
def test_sync_autopilot_status_json_exposes_correlation_and_no_op(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        status_path = "custom_status.json"
        with open(status_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "last_cycle_at": "2026-02-23T09:00:00",
                    "total_cycles": 13,
                    "health": "ok",
                    "correlation_id": "run-255",
                    "no_op_summary": {
                        "no_op": True,
                        "reason": "simulation_mode",
                        "skipped_connectors": 1,
                    },
                },
                handle,
            )

        monkeypatch.setenv("THGENT_AUTOSYNC_STATUS_PATH", status_path)
        result = runner.invoke(app, ["autopilot-status", "--format", "json"])

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert payload["correlation_id"] == "run-255"
    assert payload["no_op_summary"] == {
        "no_op": True,
        "reason": "simulation_mode",
        "skipped_connectors": 1,
    }


@pytest.mark.unit
def test_sync_autopilot_status_malformed_file_falls_back_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        status_path = "bad_status.json"
        with open(status_path, "w", encoding="utf-8") as handle:
            handle.write("{malformed")

        monkeypatch.setenv("THGENT_AUTOSYNC_STATUS_PATH", status_path)
        result = runner.invoke(app, ["autopilot-status", "--format", "json"])

    assert result.exit_code == 0
    try:
        payload = _extract_json_payload(result.stdout)
        assert payload["total_cycles"] == 0
        assert payload["health"] == "degraded"
        assert isinstance(payload["last_error"], str)
        assert "Failed to parse" in payload["last_error"]
    except json.JSONDecodeError:
        assert '"total_cycles": 0' in result.stdout
        assert '"health": "degraded"' in result.stdout
        assert "Failed to parse" in result.stdout


@pytest.mark.unit
def test_sync_audit_reads_sync_policy_contract() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        policy_path = Path(".thegent/sync-policy.yaml")
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(
            """
schema_version: sync-policy/v1
conflict_precedence: board_id_first
strict_mode: true
connectors:
  github:
    enabled: true
    mode: enforce
    direction: bidirectional
    quota_daily: 100
tenancy:
  mode: single_project
  default_tenant: tenant-default
  projects: []
""".strip(),
            encoding="utf-8",
        )

        result = runner.invoke(app, ["audit", "--format", "json"])

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert payload["schema_version"] == "sync-policy/v1"
    assert payload["enabled_connectors"] == ["github"]
    assert payload["policy_modes"] == {"github": "enforce"}
