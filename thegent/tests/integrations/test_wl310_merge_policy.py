"""Tests for thegent.integrations.merge_policy — Merge policy for parallel edits.

@trace WL-310
"""

from __future__ import annotations

import pytest

from thegent.integrations.merge_policy import (
    LocalEditMerger,
    MergeConflict,
    MergePolicy,
    MergeStrategy,
)


class TestMergeStrategy:
    """Test MergeStrategy enum. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_enum_values(self) -> None:
        """MergeStrategy has expected values."""
        assert MergeStrategy.LAST_WRITE_WINS.value == "last_write_wins"
        assert MergeStrategy.REMOTE_WINS.value == "remote_wins"
        assert MergeStrategy.LOCAL_WINS.value == "local_wins"
        assert MergeStrategy.FAIL_ON_CONFLICT.value == "fail_on_conflict"

    @pytest.mark.requirement("WL-310")
    def test_enum_comparison(self) -> None:
        """MergeStrategy members can be compared."""
        assert MergeStrategy.LAST_WRITE_WINS == MergeStrategy.LAST_WRITE_WINS
        assert MergeStrategy.LAST_WRITE_WINS != MergeStrategy.REMOTE_WINS


class TestMergePolicy:
    """Test MergePolicy dataclass. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_default_strategy(self) -> None:
        """MergePolicy defaults to LAST_WRITE_WINS."""
        policy = MergePolicy()
        assert policy.strategy == MergeStrategy.LAST_WRITE_WINS

    @pytest.mark.requirement("WL-310")
    def test_custom_strategy(self) -> None:
        """MergePolicy can be created with a custom strategy."""
        policy = MergePolicy(strategy=MergeStrategy.FAIL_ON_CONFLICT)
        assert policy.strategy == MergeStrategy.FAIL_ON_CONFLICT


class TestMergeConflictException:
    """Test MergeConflict exception. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_raise_merge_conflict(self) -> None:
        """Can raise and catch MergeConflict."""
        with pytest.raises(MergeConflict) as exc_info:
            raise MergeConflict("Test conflict message")

        assert "Test conflict message" in str(exc_info.value)


class TestLocalEditMergerInit:
    """Test LocalEditMerger initialization. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_init_with_policy(self) -> None:
        """Can create merger with a policy."""
        policy = MergePolicy(strategy=MergeStrategy.LOCAL_WINS)
        merger = LocalEditMerger(policy)
        assert merger.policy == policy

    @pytest.mark.requirement("WL-310")
    def test_init_with_default_policy(self) -> None:
        """Can create merger with default policy."""
        policy = MergePolicy()
        merger = LocalEditMerger(policy)
        assert merger.policy.strategy == MergeStrategy.LAST_WRITE_WINS


class TestLocalEditMergerMerge:
    """Test LocalEditMerger.merge() method. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_merge_last_write_wins(self) -> None:
        """LAST_WRITE_WINS uses local value."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "completed"}
        remote = {"status": "in_progress"}

        result = merger.merge(local, remote, "status")
        assert result == "completed"

    @pytest.mark.requirement("WL-310")
    def test_merge_remote_wins(self) -> None:
        """REMOTE_WINS uses remote value."""
        policy = MergePolicy(strategy=MergeStrategy.REMOTE_WINS)
        merger = LocalEditMerger(policy)

        local = {"priority": "low"}
        remote = {"priority": "high"}

        result = merger.merge(local, remote, "priority")
        assert result == "high"

    @pytest.mark.requirement("WL-310")
    def test_merge_local_wins(self) -> None:
        """LOCAL_WINS uses local value."""
        policy = MergePolicy(strategy=MergeStrategy.LOCAL_WINS)
        merger = LocalEditMerger(policy)

        local = {"title": "Local Title"}
        remote = {"title": "Remote Title"}

        result = merger.merge(local, remote, "title")
        assert result == "Local Title"

    @pytest.mark.requirement("WL-310")
    def test_merge_fail_on_conflict_no_conflict(self) -> None:
        """FAIL_ON_CONFLICT returns value when no conflict."""
        policy = MergePolicy(strategy=MergeStrategy.FAIL_ON_CONFLICT)
        merger = LocalEditMerger(policy)

        local = {"status": "done"}
        remote = {"status": "done"}

        result = merger.merge(local, remote, "status")
        assert result == "done"

    @pytest.mark.requirement("WL-310")
    def test_merge_fail_on_conflict_with_conflict(self) -> None:
        """FAIL_ON_CONFLICT raises MergeConflict on conflict."""
        policy = MergePolicy(strategy=MergeStrategy.FAIL_ON_CONFLICT)
        merger = LocalEditMerger(policy)

        local = {"status": "completed"}
        remote = {"status": "in_progress"}

        with pytest.raises(MergeConflict) as exc_info:
            merger.merge(local, remote, "status")

        assert "status" in str(exc_info.value)
        assert "completed" in str(exc_info.value)
        assert "in_progress" in str(exc_info.value)

    @pytest.mark.requirement("WL-310")
    def test_merge_missing_field_in_local(self) -> None:
        """Raises KeyError if field missing in local."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done"}
        remote = {"status": "done", "priority": "high"}

        with pytest.raises(KeyError):
            merger.merge(local, remote, "priority")

    @pytest.mark.requirement("WL-310")
    def test_merge_missing_field_in_remote(self) -> None:
        """Raises KeyError if field missing in remote."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done", "priority": "high"}
        remote = {"status": "done"}

        with pytest.raises(KeyError):
            merger.merge(local, remote, "priority")


class TestLocalEditMergerMergeRecord:
    """Test LocalEditMerger.merge_record() method. @trace WL-310"""

    @pytest.mark.requirement("WL-310")
    def test_merge_record_single_field(self) -> None:
        """Can merge a single field."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "completed", "priority": "high"}
        remote = {"status": "in_progress", "priority": "high"}

        result = merger.merge_record(local, remote, ["status"])
        assert result == {"status": "completed"}

    @pytest.mark.requirement("WL-310")
    def test_merge_record_multiple_fields(self) -> None:
        """Can merge multiple fields."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done", "priority": "low", "title": "Task A"}
        remote = {"status": "pending", "priority": "high", "title": "Task A"}

        result = merger.merge_record(local, remote, ["status", "priority", "title"])
        assert result == {"status": "done", "priority": "low", "title": "Task A"}

    @pytest.mark.requirement("WL-310")
    def test_merge_record_with_remote_wins(self) -> None:
        """Respects REMOTE_WINS strategy across multiple fields."""
        policy = MergePolicy(strategy=MergeStrategy.REMOTE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done", "priority": "low"}
        remote = {"status": "pending", "priority": "high"}

        result = merger.merge_record(local, remote, ["status", "priority"])
        assert result == {"status": "pending", "priority": "high"}

    @pytest.mark.requirement("WL-310")
    def test_merge_record_empty_fields(self) -> None:
        """Merging empty field list returns empty dict."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done"}
        remote = {"status": "pending"}

        result = merger.merge_record(local, remote, [])
        assert result == {}

    @pytest.mark.requirement("WL-310")
    def test_merge_record_fail_on_conflict_first_field(self) -> None:
        """FAIL_ON_CONFLICT fails on first conflicting field."""
        policy = MergePolicy(strategy=MergeStrategy.FAIL_ON_CONFLICT)
        merger = LocalEditMerger(policy)

        local = {"status": "done", "priority": "low"}
        remote = {"status": "pending", "priority": "high"}

        with pytest.raises(MergeConflict) as exc_info:
            merger.merge_record(local, remote, ["status", "priority"])

        assert "status" in str(exc_info.value)

    @pytest.mark.requirement("WL-310")
    def test_merge_record_fail_on_conflict_second_field(self) -> None:
        """FAIL_ON_CONFLICT fails on second field if first matches."""
        policy = MergePolicy(strategy=MergeStrategy.FAIL_ON_CONFLICT)
        merger = LocalEditMerger(policy)

        local = {"status": "done", "priority": "low"}
        remote = {"status": "done", "priority": "high"}

        with pytest.raises(MergeConflict) as exc_info:
            merger.merge_record(local, remote, ["status", "priority"])

        assert "priority" in str(exc_info.value)

    @pytest.mark.requirement("WL-310")
    def test_merge_record_missing_field(self) -> None:
        """Raises KeyError if any field is missing."""
        policy = MergePolicy(strategy=MergeStrategy.LAST_WRITE_WINS)
        merger = LocalEditMerger(policy)

        local = {"status": "done"}
        remote = {"status": "done", "priority": "high"}

        with pytest.raises(KeyError):
            merger.merge_record(local, remote, ["status", "priority"])
