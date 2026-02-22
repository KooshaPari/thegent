"""Tests for WL-160: Full Automatic Workstream Reflection (GitHub Projects + Linear).

Tests cover:
- Configuration validation
- Standalone-safe behavior (no crash when disabled or credentials missing)
- Cycle runner initialization and control
- Workstream item parsing
- Platform-specific sync operations (stubs with proper structure)
- Autosync command-line interface
"""

import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from thegent.docgen.code_annotation import CodeAnnotationGenerator
from thegent.execution import EscalationQueue
from thegent.integrations.reflection_event_log import ReflectionDecision, ReflectionEventLog
from thegent.integrations.workstream_autosync import (
    SyncDirection,
    SyncOperation,
    MaintenanceWindow,
    RemoteMissingItemPolicy,
    WorkstreamAutosyncConfig,
    WorkstreamAutosyncConfigError,
    WorkstreamAutosyncRunner,
    WorkstreamItem,
    WorkstreamParser,
    load_autosync_config_from_env,
)
from thegent.integrations.idempotency_cache import IdempotencyCache


@pytest.fixture
def valid_github_config():
    """Valid GitHub Projects configuration."""
    return WorkstreamAutosyncConfig(
        enabled=True,
        github_enabled=True,
        github_owner="kooshapari",
        github_project_number=1,
        github_direction=SyncDirection.BIDIRECTIONAL,
        standalone_mode=True,
    )


@pytest.fixture
def valid_linear_config():
    """Valid Linear configuration."""
    return WorkstreamAutosyncConfig(
        enabled=True,
        linear_enabled=True,
        linear_api_key="test-key-123",
        linear_team_key="test-team",
        linear_direction=SyncDirection.BIDIRECTIONAL,
        standalone_mode=True,
    )


@pytest.fixture
def disabled_config():
    """Disabled autosync configuration."""
    return WorkstreamAutosyncConfig(
        enabled=False,
        github_enabled=True,
        github_owner="kooshapari",
        github_project_number=1,
        standalone_mode=True,
    )


@pytest.fixture
def sample_work_stream_file(tmp_path):
    """Create a sample WORK_STREAM.md for testing."""
    work_stream = tmp_path / "WORK_STREAM.md"
    content = """# Work Stream

### [WL-160] Full Automatic Workstream Reflection
**Status:** IN PROGRESS
**Priority:** P1
**Area:** sync, automation
**Blocked by:** external credentials

Make board/tooling concerns transparent.

### [WL-161] Board-ID-First Reconciliation
**Status:** BACKLOG
**Priority:** P1
**Area:** sync

Define deterministic conflict precedence.
"""
    work_stream.write_text(content)
    return work_stream


class TestWorkstreamAutosyncConfig:
    """Test WorkstreamAutosyncConfig validation."""

    def test_valid_github_config(self, valid_github_config):
        """Valid GitHub config passes validation."""
        assert valid_github_config.is_valid() is True
        assert valid_github_config.should_sync_github() is True
        assert valid_github_config.should_sync_linear() is False

    def test_valid_linear_config(self, valid_linear_config):
        """Valid Linear config passes validation."""
        assert valid_linear_config.is_valid() is True
        assert valid_linear_config.should_sync_linear() is True
        assert valid_linear_config.should_sync_github() is False

    def test_disabled_config(self, disabled_config):
        """Disabled config fails validation."""
        assert disabled_config.is_valid() is False

    def test_github_permissions(self, valid_github_config):
        """Test GitHub read/write permissions based on direction."""
        # Bidirectional
        assert valid_github_config.github_can_read() is True
        assert valid_github_config.github_can_write() is True

        # Read-only
        ro_config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="test",
            github_project_number=1,
            github_direction=SyncDirection.READ_ONLY,
        )
        assert ro_config.github_can_read() is True
        assert ro_config.github_can_write() is False

        # Write-only
        wo_config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="test",
            github_project_number=1,
            github_direction=SyncDirection.WRITE_ONLY,
        )
        assert wo_config.github_can_read() is False
        assert wo_config.github_can_write() is True

    def test_linear_permissions(self, valid_linear_config):
        """Test Linear read/write permissions based on direction."""
        # Bidirectional
        assert valid_linear_config.linear_can_read() is True
        assert valid_linear_config.linear_can_write() is True

        # Read-only
        ro_config = WorkstreamAutosyncConfig(
            enabled=True,
            linear_enabled=True,
            linear_api_key="key",
            linear_team_key="team",
            linear_direction=SyncDirection.READ_ONLY,
        )
        assert ro_config.linear_can_read() is True
        assert ro_config.linear_can_write() is False


class TestWorkstreamParser:
    """Test workstream markdown parsing."""

    def test_parse_valid_items(self, sample_work_stream_file):
        """Parse valid work stream items."""
        items = WorkstreamParser.parse_items(sample_work_stream_file)

        assert len(items) == 2
        assert items[0].item_id == "WL-160"
        assert items[0].title == "Full Automatic Workstream Reflection"
        assert items[0].status == "IN PROGRESS"
        assert items[0].priority == "P1"
        assert items[0].area == "sync, automation"

        assert items[1].item_id == "WL-161"
        assert items[1].status == "BACKLOG"

    def test_parse_missing_file(self, tmp_path):
        """Handle missing WORK_STREAM.md gracefully."""
        missing_file = tmp_path / "missing.md"
        items = WorkstreamParser.parse_items(missing_file)
        assert items == []

    def test_parse_extract_blocked_by(self, tmp_path):
        """Extract blocked_by field from metadata."""
        work_stream = tmp_path / "WORK_STREAM.md"
        content = """
### [WL-100] Test Item
**Status:** BACKLOG
**Blocked by:** WL-099
"""
        work_stream.write_text(content)
        items = WorkstreamParser.parse_items(work_stream)

        assert len(items) == 1
        assert items[0].blocked_by == "WL-099"

    def test_parse_tags_and_sla(self, tmp_path):
        """Parse tags and SLA metadata."""
        work_stream = tmp_path / "WORK_STREAM.md"
        work_stream.write_text(
            """### [WL-100] Test Tags
**Status:** BACKLOG
**Tags:** urgent, critical, UI
**SLA:** 6h
"""
        )

        items = WorkstreamParser.parse_items(work_stream)
        assert len(items) == 1
        assert items[0].tags == ["urgent", "critical", "ui"]
        assert items[0].sla_hours == 6.0

    def test_open_blocker_digest(self):
        """Build digest for blocked open items."""
        items = [
            WorkstreamItem(
                item_id="WL-1",
                title="A",
                status="IN PROGRESS",
                priority="P1",
                area="core",
                blocked_by="WL-2",
            ),
            WorkstreamItem(
                item_id="WL-2",
                title="B",
                status="COMPLETED",
                priority="P1",
                area="core",
                blocked_by="WL-3",
            ),
            WorkstreamItem(
                item_id="WL-3",
                title="C",
                status="BACKLOG",
                priority="P1",
                area="core",
                blocked_by="none",
            ),
        ]

        digest = WorkstreamParser.open_blocker_digest(items)

        assert digest == ["WL-1:A -> WL-2"]

    def test_duplicate_titles(self):
        """Detect duplicate item titles."""
        items = [
            WorkstreamItem(item_id="WL-1", title="same", status="BACKLOG", priority="P1", area="core"),
            WorkstreamItem(item_id="WL-2", title="same", status="BACKLOG", priority="P1", area="core"),
            WorkstreamItem(item_id="WL-3", title="unique", status="BACKLOG", priority="P1", area="core"),
        ]

        duplicates = WorkstreamParser.duplicate_titles(items)
        assert len(duplicates) == 1
        assert duplicates[0][0] == "same"

    def test_validate_tags_and_partitioning(self):
        """Validate tags and partition ranges."""
        items = [
            WorkstreamItem(item_id="WL-1", title="a", status="BACKLOG", priority="P1", area="core", tags=["api"]),
            WorkstreamItem(item_id="WL-2", title="b", status="BACKLOG", priority="P1", area="core", tags=["ui"]),
            WorkstreamItem(item_id="WL-3", title="c", status="BACKLOG", priority="P1", area="core", tags=["infra"]),
        ]
        is_valid, invalid = WorkstreamParser.validate_tags(items, allowed_tags=["api", "ui"], strict=False)
        assert is_valid is True
        assert invalid == ["infra"]

        is_valid, invalid = WorkstreamParser.validate_tags(items, allowed_tags=["api", "ui"], strict=True)
        assert is_valid is False
        assert invalid == ["infra"]

        partitions = WorkstreamParser.split_items(items, partition_size=2)
        assert len(partitions) == 2
        assert len(partitions[0]) == 2
        assert len(partitions[1]) == 1

    def test_sync_sla_annotations(self, tmp_path):
        """Ensure SLA values are reflected in markdown blocks."""
        content = """### [WL-1] Test
**Status:** BACKLOG
"""
        updated = WorkstreamParser.sync_sla_annotations(
            content,
            items=[
                WorkstreamItem(
                    item_id="WL-1", title="Test", status="BACKLOG", priority="P1", area="core", sla_hours=12.5
                )
            ],
        )
        assert "**SLA:** 12.5h" in updated

    def test_scope_filters_match_area_status_priority_and_range(self):
        """WL-168 scope filters should include only matching items."""
        config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="owner",
            github_project_number=1,
            scope_areas=["sync, automation"],
            scope_statuses=["BACKLOG"],
            scope_priorities=["P1"],
            scope_wl_ranges=["WL-160..WL-170"],
        )
        matching = WorkstreamItem(
            item_id="WL-160",
            title="match",
            status="BACKLOG",
            priority="P1",
            area="sync, automation",
        )
        excluded = WorkstreamItem(
            item_id="WL-190",
            title="skip",
            status="BACKLOG",
            priority="P1",
            area="sync, automation",
        )

        assert config.matches_scope_filters(matching) is True
        assert config.matches_scope_filters(excluded) is False

    def test_sync_status_annotations(self):
        """Ensure status lines are reflected in markdown blocks."""
        content = """### [WL-1] Test
**Status:** BACKLOG
"""
        updated = WorkstreamParser.sync_status_annotations(
            content,
            statuses={"WL-1": "COMPLETED"},
        )
        assert "**Status:** COMPLETED" in updated


class TestWorkstreamItem:
    """Test WorkstreamItem model."""

    def test_item_to_dict(self):
        """Convert item to dictionary."""
        item = WorkstreamItem(
            item_id="WL-160",
            title="Test Item",
            status="IN PROGRESS",
            priority="P1",
            area="test",
            blocked_by="WL-159",
            source_line=10,
        )

        d = item.to_dict()
        assert d["item_id"] == "WL-160"
        assert d["status"] == "IN PROGRESS"
        assert d["blocked_by"] == "WL-159"


class TestSyncOperation:
    """Test SyncOperation model."""

    def test_operation_to_dict(self):
        """Convert operation to dictionary."""
        op = SyncOperation(
            operation_id="test-op-1",
            platform="github",
            direction="write",
            items_processed=10,
            items_successful=9,
            items_failed=1,
            errors=["Failed to sync item WL-100"],
        )

        d = op.to_dict()
        assert d["operation_id"] == "test-op-1"
        assert d["platform"] == "github"
        assert d["items_successful"] == 9
        assert d["errors"] == ["Failed to sync item WL-100"]


class TestWorkstreamAutosyncRunner:
    """Test WorkstreamAutosyncRunner."""

    @pytest.mark.asyncio
    async def test_runner_init(self, valid_github_config):
        """Test runner initialization."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        assert runner.config == valid_github_config
        assert runner.is_running is False
        assert runner.last_sync_time is None

    @pytest.mark.asyncio
    async def test_runner_start_with_valid_config(self, valid_github_config):
        """Test runner starts with valid config."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        await runner.start()

        # Check that task was created
        assert runner.is_running is True
        assert runner._task is not None

        # Clean up
        await runner.stop()

    @pytest.mark.asyncio
    async def test_runner_start_with_invalid_config(self, disabled_config):
        """Test runner doesn't start with invalid config."""
        runner = WorkstreamAutosyncRunner(disabled_config)
        await runner.start()

        # Should not start due to invalid config
        assert runner.is_running is False

    @pytest.mark.asyncio
    async def test_runner_stop(self, valid_github_config):
        """Test runner can be stopped."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        await runner.start()
        assert runner.is_running is True

        await runner.stop()
        assert runner.is_running is False

    @pytest.mark.asyncio
    async def test_perform_sync_cycle_with_items(self, valid_github_config, sample_work_stream_file):
        """Test sync cycle with work stream items."""
        valid_github_config.work_stream_path = sample_work_stream_file

        runner = WorkstreamAutosyncRunner(valid_github_config)
        with (
            patch(
                "thegent.integrations.workstream_autosync.gh_sync_to_github",
                return_value={"items_created": 0, "items_updated": 1, "errors": []},
            ),
            patch(
                "thegent.integrations.workstream_autosync.gh_sync_from_github",
                return_value={"items": [{"item_id": "WL-160", "status": "IN PROGRESS"}], "errors": []},
            ),
        ):
            await runner._perform_sync_cycle()

        # Should have recorded a sync time
        assert runner.last_sync_time is not None

    @pytest.mark.asyncio
    async def test_run_cycle_skips_maintenance(self, valid_github_config, sample_work_stream_file):
        """Run cycle should skip connectors in maintenance window."""
        now = datetime.now(timezone.utc)
        valid_github_config.work_stream_path = sample_work_stream_file
        runner = WorkstreamAutosyncRunner(valid_github_config)

        async def boom(_items):
            raise RuntimeError("should not run")

        runner._sync_to_github = boom  # type: ignore[method-assign]
        valid_github_config.maintenance_windows = [
            MaintenanceWindow(
                connector="github",
                start_utc=now - timedelta(minutes=1),
                end_utc=now + timedelta(minutes=1),
            )
        ]
        await runner._perform_sync_cycle()
        assert runner.last_sync_time is not None
        assert runner._checkpoint is None

    @pytest.mark.asyncio
    async def test_run_cycle_stops_on_emergency_env_flag(self, valid_github_config, sample_work_stream_file):
        """Emergency stop env should block autosync cycle."""
        valid_github_config.work_stream_path = sample_work_stream_file
        valid_github_config.emergency_stop_env_var = "THGENT_AUTOSYNC_EMERGENCY_STOP"
        runner = WorkstreamAutosyncRunner(valid_github_config)
        with patch.dict("os.environ", {"THGENT_AUTOSYNC_EMERGENCY_STOP": "1"}):
            await runner._perform_sync_cycle()
        assert runner.last_error is not None
        assert "Emergency stop active" in runner.last_error

    @pytest.mark.asyncio
    async def test_write_entrypoint_blocks_when_emergency_stop_file_exists(self, valid_github_config, tmp_path):
        """Write entrypoints fail fast when emergency stop sentinel file is present."""
        sentinel = tmp_path / "autosync.stop"
        sentinel.write_text("stop", encoding="utf-8")
        valid_github_config.emergency_stop_file_path = sentinel
        runner = WorkstreamAutosyncRunner(valid_github_config)
        items = [WorkstreamItem(item_id="WL-1", title="One", status="BACKLOG", priority="P1", area="sync")]
        with pytest.raises(WorkstreamAutosyncConfigError, match="Emergency stop active"):
            await runner._sync_to_github(items)

    @pytest.mark.asyncio
    async def test_operation_ids_are_replay_safe_for_same_batch(self, valid_github_config):
        """Write op ID should be deterministic for same connector+direction+batch."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        items = [WorkstreamItem(item_id="WL-1", title="One", status="BACKLOG", priority="P1", area="sync")]
        with patch(
            "thegent.integrations.workstream_autosync.gh_sync_to_github",
            return_value={"items_created": 0, "items_updated": 1, "errors": []},
        ):
            await runner._sync_to_github(items)
            first_id = runner.last_operation.operation_id if runner.last_operation else None
            await runner._sync_to_github(items)
            second_id = runner.last_operation.operation_id if runner.last_operation else None
        assert first_id is not None
        assert second_id is not None
        assert first_id == second_id
        assert first_id.startswith("gh-write-")

    @pytest.mark.asyncio
    async def test_replay_safe_mutations_skip_second_write(self, valid_github_config, tmp_path):
        """Second write for same batch should be skipped by idempotency cache."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        runner._idempotency_cache = IdempotencyCache(tmp_path / "idempotency.json")
        items = [
            WorkstreamItem(item_id="WL-1", title="One", status="BACKLOG", priority="P1", area="sync"),
            WorkstreamItem(item_id="WL-2", title="Two", status="BACKLOG", priority="P1", area="sync"),
        ]
        with patch(
            "thegent.integrations.workstream_autosync.gh_sync_to_github",
            return_value={"items_created": 0, "items_updated": 2, "errors": []},
        ):
            await runner._sync_to_github(items)
            assert runner.last_operation is not None
            assert runner.last_operation.items_successful == 2

            await runner._sync_to_github(items)
            assert runner.last_operation is not None
            assert runner.last_operation.items_successful == 0

    def test_connector_chaos_timeout_fixture(self):
        """Deterministic timeout fixture should request retries and escalation."""
        payload = WorkstreamAutosyncRunner.simulate_connector_chaos("github", "timeout", items_count=4)
        assert payload["scenario"] == "timeout"
        assert payload["retry_count"] == 3
        assert payload["escalate"] is True
        assert payload["outcome"] == "outage"

    def test_connector_chaos_partial_ack_fixture(self):
        """Partial ack fixture should report deterministic partial completion."""
        payload = WorkstreamAutosyncRunner.simulate_connector_chaos("linear", "partial_ack", items_count=5)
        assert payload["items_attempted"] == 5
        assert payload["items_acked"] == 4
        assert payload["escalate"] is True

    def test_connector_chaos_unknown_fixture_raises(self):
        """Unsupported chaos scenarios must fail loudly."""
        with pytest.raises(ValueError, match="Unsupported chaos scenario"):
            WorkstreamAutosyncRunner.simulate_connector_chaos("github", "unknown", items_count=1)

    @pytest.mark.asyncio
    async def test_checkpoint_resume_on_failure(self, tmp_path):
        """Resume sync from checkpoint after a partition failure."""
        work_stream = tmp_path / "WORK_STREAM.md"
        work_stream.write_text(
            """### [WL-1] One
**Status:** BACKLOG

### [WL-2] Two
**Status:** BACKLOG

### [WL-3] Three
**Status:** BACKLOG
"""
        )

        config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="owner",
            github_project_number=1,
            max_partition_size=1,
            checkpoint_file_path=tmp_path / "checkpoint.json",
            standalone_mode=True,
        )
        config.should_sync_github()
        runner = WorkstreamAutosyncRunner(config)
        runner.config.work_stream_path = work_stream

        calls = []

        async def flaky_sync(items: list[WorkstreamItem]) -> None:
            calls.append([item.item_id for item in items])
            if len(calls) == 1:
                raise RuntimeError("flaky")

        await runner._sync_in_partitions(
            connector="github",
            direction="write",
            items=WorkstreamParser.parse_items(work_stream),
            sync_fn=flaky_sync,
        )
        assert calls == [["WL-1"]]
        assert runner._checkpoint is None

        async def sync_identity(items: list[WorkstreamItem]) -> None:
            calls.append([item.item_id for item in items])

        await runner._sync_in_partitions(
            connector="github",
            direction="write",
            items=WorkstreamParser.parse_items(work_stream),
            sync_fn=sync_identity,
        )
        assert calls == [["WL-1"], ["WL-1"], ["WL-2"], ["WL-3"]]

    @pytest.mark.asyncio
    async def test_sync_to_github(self, valid_github_config):
        """Test GitHub sync operation."""
        runner = WorkstreamAutosyncRunner(valid_github_config)

        items = [
            WorkstreamItem(
                item_id="WL-160",
                title="Test",
                status="IN PROGRESS",
                priority="P1",
                area="test",
            )
        ]

        with patch(
            "thegent.integrations.workstream_autosync.gh_sync_to_github",
            return_value={"items_created": 0, "items_updated": 1, "errors": []},
        ):
            await runner._sync_to_github(items)

        # Should record operation
        assert runner.last_operation is not None
        assert runner.last_operation.platform == "github"
        assert runner.last_operation.direction == "write"

    @pytest.mark.asyncio
    async def test_sync_from_github(self, valid_github_config, tmp_path):
        """Test reading from GitHub Projects."""
        work_stream = tmp_path / "WORK_STREAM.md"
        work_stream.write_text("# Test\n")
        valid_github_config.work_stream_path = work_stream

        runner = WorkstreamAutosyncRunner(valid_github_config)
        items = []

        with patch(
            "thegent.integrations.workstream_autosync.gh_sync_from_github",
            return_value={"items": [{"item_id": "WL-160", "status": "COMPLETED"}], "errors": []},
        ):
            await runner._sync_from_github(items, work_stream)

        # Should record operation
        assert runner.last_operation is not None
        assert runner.last_operation.platform == "github"
        assert runner.last_operation.direction == "read"

    @pytest.mark.asyncio
    async def test_sync_from_github_closes_issue_on_completion_transition(self, valid_github_config, tmp_path):
        """Remote completion transition should trigger GitHub issue auto-close flow."""
        work_stream = tmp_path / "WORK_STREAM.md"
        work_stream.write_text(
            """### [WL-160] Test
**Status:** IN PROGRESS
"""
        )
        valid_github_config.work_stream_path = work_stream
        valid_github_config.github_auto_close_issues = True
        valid_github_config.github_auto_close_comment = "Closed via autosync."

        runner = WorkstreamAutosyncRunner(valid_github_config)
        items = WorkstreamParser.parse_items(work_stream)

        with (
            patch(
                "thegent.integrations.workstream_autosync.extract_github_issue_refs",
                return_value=["owner/repo#123"],
            ),
            patch(
                "thegent.integrations.workstream_autosync.gh_sync_from_github",
                return_value={
                    "items": [
                        {
                            "item_id": "WL-160",
                            "status": "COMPLETED",
                            "body": "Completes owner/repo#123",
                        }
                    ],
                    "errors": [],
                },
            ),
            patch(
                "thegent.integrations.workstream_autosync.close_or_comment_github_issue_refs",
                return_value={
                    "items_processed": 1,
                    "items_updated": 1,
                    "items_commented": 1,
                    "issues": [
                        {
                            "issue_ref": "owner/repo#123",
                            "commented": True,
                            "closed": True,
                            "status": "ok",
                        }
                    ],
                    "errors": [],
                },
            ) as close_mock,
        ):
            await runner._sync_from_github(items, work_stream)

        updated = work_stream.read_text(encoding="utf-8")
        assert "**Status:** COMPLETED" in updated
        close_mock.assert_called_once_with(["owner/repo#123"], close_comment="Closed via autosync.")

    @pytest.mark.asyncio
    async def test_finalize_incident_snapshot_enqueues_slo_escalation(self, valid_github_config, tmp_path):
        """Snapshot with stale age and budget breach should enqueue escalation entry."""
        status_path = tmp_path / "autosync_status.json"
        status_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path = status_path.parent / "autosync_snapshot_old.json"
        snapshot_path.write_text("{}", encoding="utf-8")
        old_time = datetime.now().timestamp() - 3_600
        os.utime(snapshot_path, (old_time, old_time))

        config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="owner",
            github_project_number=1,
            standalone_mode=True,
            status_file_path=status_path,
            error_budget_max_consecutive_failures=1,
            error_budget_max_failure_rate=0.1,
            error_budget_escalation_after=1,
            autosync_stale_snapshot_seconds=1,
        )
        runner = WorkstreamAutosyncRunner(config)
        runner._current_run_correlation_id = "run-123"
        runner._error_budget.record_failure()

        runner._finalize_incident_snapshot(items_count=3, metadata_state={"status": "fresh", "age_seconds": 0})

        snapshot = runner._latest_incident_snapshot
        assert any("autosync snapshot stale" in reason for reason in snapshot["slo_alerts"])
        assert any("error budget" in reason for reason in snapshot["slo_alerts"])

        queue = EscalationQueue(status_path.parent)
        pending = queue.list_pending()
        assert any("autosync snapshot stale" in str(item.get("reason", "")) for item in pending)

    @pytest.mark.asyncio
    async def test_sync_to_linear(self, valid_linear_config):
        """Test Linear sync operation."""
        runner = WorkstreamAutosyncRunner(valid_linear_config)

        items = [
            WorkstreamItem(
                item_id="WL-160",
                title="Test",
                status="IN PROGRESS",
                priority="P1",
                area="test",
            )
        ]

        with patch(
            "thegent.integrations.workstream_autosync.linear_sync_to",
            return_value={"items_created": 0, "items_updated": 1, "errors": []},
        ):
            await runner._sync_to_linear(items)

        # Should record operation
        assert runner.last_operation is not None
        assert runner.last_operation.platform == "linear"
        assert runner.last_operation.direction == "write"

    @pytest.mark.asyncio
    async def test_sync_from_linear(self, valid_linear_config, tmp_path):
        """Test reading from Linear."""
        work_stream = tmp_path / "WORK_STREAM.md"
        work_stream.write_text("# Test\n")
        valid_linear_config.work_stream_path = work_stream

        runner = WorkstreamAutosyncRunner(valid_linear_config)
        items = []

        with patch(
            "thegent.integrations.workstream_autosync.linear_sync_from",
            return_value={"items": [{"item_id": "WL-160", "status": "COMPLETED"}], "errors": []},
        ):
            await runner._sync_from_linear(items, work_stream)

        # Should record operation
        assert runner.last_operation is not None
        assert runner.last_operation.platform == "linear"
        assert runner.last_operation.direction == "read"

    def test_get_status(self, valid_github_config):
        """Test getting runner status."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        status = runner.get_status()

        assert status["enabled"] is True
        assert status["is_running"] is False
        assert status["github_enabled"] is True
        assert status["linear_enabled"] is False
        assert status["last_operation"] is None

    def test_get_status_with_operation(self, valid_github_config):
        """Test status includes last operation."""
        runner = WorkstreamAutosyncRunner(valid_github_config)
        runner.last_operation = SyncOperation(
            operation_id="test-op",
            platform="github",
            direction="write",
            items_processed=5,
            items_successful=5,
        )

        status = runner.get_status()
        assert status["last_operation"] is not None
        assert status["last_operation"]["operation_id"] == "test-op"

    def test_remote_missing_item_policy_archive(self, valid_github_config):
        """WL-167 archive policy should mark missing remote items as ARCHIVED."""
        valid_github_config.remote_missing_item_policy = RemoteMissingItemPolicy.ARCHIVE
        runner = WorkstreamAutosyncRunner(valid_github_config)
        local = [
            WorkstreamItem(item_id="WL-160", title="A", status="BACKLOG", priority="P1", area="sync"),
            WorkstreamItem(item_id="WL-161", title="B", status="BACKLOG", priority="P1", area="sync"),
        ]
        updates = runner._build_remote_reflection_status_updates(
            local_items=local,
            remote_status_updates={"WL-160": "IN PROGRESS"},
        )
        assert updates["WL-160"] == "IN PROGRESS"
        assert updates["WL-161"] == "ARCHIVED"


class TestLoadAutosyncConfigFromEnv:
    """Test loading config from environment."""

    def test_load_with_github_enabled(self):
        """Load config with GitHub enabled."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_GITHUB_ENABLED": "true",
                "THGENT_GITHUB_OWNER": "test-owner",
                "THGENT_GITHUB_PROJECT_NUMBER": "42",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.enabled is True
            assert config.github_enabled is True
            assert config.github_owner == "test-owner"
            assert config.github_project_number == 42

    def test_load_with_linear_enabled(self):
        """Load config with Linear enabled."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_LINEAR_ENABLED": "true",
                "THGENT_LINEAR_API_KEY": "test-key",
                "THGENT_LINEAR_TEAM_KEY": "test-team",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.enabled is True
            assert config.linear_enabled is True
            assert config.linear_api_key == "test-key"

    def test_load_with_custom_interval(self):
        """Load config with custom cycle interval."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_WORKSTREAM_AUTOSYNC_INTERVAL": "600",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.cycle_interval_seconds == 600

    def test_load_defaults(self):
        """Load config with all defaults."""
        with patch.dict("os.environ", {}, clear=True):
            config = load_autosync_config_from_env()
            assert config.enabled is False
            assert config.cycle_interval_seconds == 300

    def test_load_with_sync_directions(self):
        """Load config with custom sync directions."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_GITHUB_ENABLED": "true",
                "THGENT_GITHUB_OWNER": "test",
                "THGENT_GITHUB_PROJECT_NUMBER": "1",
                "THGENT_GITHUB_DIRECTION": "read_only",
                "THGENT_LINEAR_ENABLED": "true",
                "THGENT_LINEAR_API_KEY": "key",
                "THGENT_LINEAR_TEAM_KEY": "team",
                "THGENT_LINEAR_DIRECTION": "write_only",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.github_direction == SyncDirection.READ_ONLY
            assert config.linear_direction == SyncDirection.WRITE_ONLY

    def test_load_emergency_stop_settings(self):
        """Load emergency-stop settings from env."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_GITHUB_ENABLED": "true",
                "THGENT_GITHUB_OWNER": "test-owner",
                "THGENT_GITHUB_PROJECT_NUMBER": "1",
                "THGENT_AUTOSYNC_EMERGENCY_STOP_ENABLED": "true",
                "THGENT_AUTOSYNC_EMERGENCY_STOP_FILE_PATH": "/tmp/thegent-stop",
                "THGENT_AUTOSYNC_EMERGENCY_STOP_ENV_VAR": "CUSTOM_STOP",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.emergency_stop_enabled is True
            assert str(config.emergency_stop_file_path) == "/tmp/thegent-stop"
            assert config.emergency_stop_env_var == "CUSTOM_STOP"

    def test_load_scope_filters_and_remote_missing_policy(self):
        """WL-168/WL-167 env config should populate scope filters and missing-item policy."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_GITHUB_ENABLED": "true",
                "THGENT_GITHUB_OWNER": "test-owner",
                "THGENT_GITHUB_PROJECT_NUMBER": "1",
                "THGENT_WORKSTREAM_SYNC_SCOPE_AREAS": "sync,automation",
                "THGENT_WORKSTREAM_SYNC_SCOPE_STATUSES": "backlog,in progress",
                "THGENT_WORKSTREAM_SYNC_SCOPE_PRIORITIES": "p0,p1",
                "THGENT_WORKSTREAM_SYNC_SCOPE_WL_RANGES": "WL-160..WL-168",
                "THGENT_WORKSTREAM_REMOTE_MISSING_ITEM_POLICY": "archive",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.scope_areas == ["sync", "automation"]
            assert config.scope_statuses == ["BACKLOG", "IN PROGRESS"]
            assert config.scope_priorities == ["P0", "P1"]
            assert config.scope_wl_ranges == ["WL-160..WL-168"]
            assert config.remote_missing_item_policy == RemoteMissingItemPolicy.ARCHIVE

    def test_load_slo_and_stale_snapshot_env(self):
        """Load error budget thresholds and stale snapshot threshold from environment."""
        with patch.dict(
            "os.environ",
            {
                "THGENT_WORKSTREAM_AUTOSYNC_ENABLED": "true",
                "THGENT_GITHUB_ENABLED": "true",
                "THGENT_GITHUB_OWNER": "test-owner",
                "THGENT_GITHUB_PROJECT_NUMBER": "1",
                "THGENT_AUTOSYNC_ERROR_BUDGET_MAX_CONSECUTIVE_FAILURES": "2",
                "THGENT_AUTOSYNC_ERROR_BUDGET_MAX_FAILURE_RATE": "0.2",
                "THGENT_AUTOSYNC_ERROR_BUDGET_ESCALATION_AFTER": "4",
                "THGENT_AUTOSYNC_STALE_SNAPSHOT_SECONDS": "1200",
            },
        ):
            config = load_autosync_config_from_env()
            assert config.error_budget_max_consecutive_failures == 2
            assert config.error_budget_max_failure_rate == 0.2
            assert config.error_budget_escalation_after == 4
            assert config.autosync_stale_snapshot_seconds == 1200


class TestStandaloneMode:
    """Test standalone-safe behavior."""

    @pytest.mark.asyncio
    async def test_graceful_skip_when_disabled(self):
        """Gracefully skip when autosync disabled."""
        config = WorkstreamAutosyncConfig(
            enabled=False,
            standalone_mode=True,
        )

        runner = WorkstreamAutosyncRunner(config)
        await runner.start()

        # Should not crash, just not start
        assert runner.is_running is False


class TestAnnotationAndReflectionStandard:
    """Tests for WL-238 remote->local annotation schema standard."""

    def test_annotation_schema_requires_canonical_keys(self) -> None:
        gen = CodeAnnotationGenerator(annotation_format="json")
        payload = gen.format_reflection_annotation(
            {
                "schema": "reflection-annotation-v1",
                "wl_id": "WL-238",
                "connector": "github",
                "direction": "remote_to_local",
                "decision": "apply",
                "mutation_id": "github-mutation-WL-238-abc",
                "timestamp": "2026-02-22T00:00:00Z",
                "extra": "ok",
            }
        )
        assert list(payload.keys())[:7] == list(CodeAnnotationGenerator.REQUIRED_REFLECTION_KEYS)
        assert payload["extra"] == "ok"

    def test_reflection_event_log_writes_annotation_block(self, tmp_path) -> None:
        log_path = tmp_path / "reflection.jsonl"
        log = ReflectionEventLog(log_path)
        decision = ReflectionDecision(
            wl_id="WL-238",
            decision_type="apply",
            before_value="BACKLOG",
            after_value="IN PROGRESS",
            connector="github",
            timestamp="2026-02-22T00:00:00Z",
            cycle_id="cycle-1",
        )
        log.log(decision)
        raw = log_path.read_text(encoding="utf-8").strip()
        assert '"annotation"' in raw
        assert '"schema": "reflection-annotation-v1"' in raw

    @pytest.mark.asyncio
    async def test_graceful_skip_when_credentials_missing(self):
        """Gracefully skip when credentials missing."""
        config = WorkstreamAutosyncConfig(
            enabled=True,
            github_enabled=True,
            github_owner="",  # Missing required field
            standalone_mode=True,
        )

        runner = WorkstreamAutosyncRunner(config)
        await runner.start()

        # Should not crash, just not start
        assert runner.is_running is False
