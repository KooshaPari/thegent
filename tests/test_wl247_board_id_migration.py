from __future__ import annotations

import pytest

from thegent.integrations.board_id_migration import (
    LegacyBoardIdMigrationTool,
    MigrationEntry,
)


@pytest.mark.requirement("WL-247")
class TestMigrationEntry:
    """Test MigrationEntry dataclass."""

    def test_create_migration_entry_default(self) -> None:
        """Test creating a migration entry with default migrated=False."""
        entry = MigrationEntry(old_id="old_123", new_id="new_456")
        assert entry.old_id == "old_123"
        assert entry.new_id == "new_456"
        assert entry.migrated is False

    def test_create_migration_entry_with_migrated(self) -> None:
        """Test creating a migration entry with migrated=True."""
        entry = MigrationEntry(old_id="old_789", new_id="new_012", migrated=True)
        assert entry.old_id == "old_789"
        assert entry.new_id == "new_012"
        assert entry.migrated is True


@pytest.mark.requirement("WL-247")
class TestLegacyBoardIdMigrationTool:
    """Test LegacyBoardIdMigrationTool."""

    def test_register_new_entry(self) -> None:
        """Test registering a new migration."""
        tool = LegacyBoardIdMigrationTool()
        entry = tool.register("old_board_1", "new_board_1")

        assert entry.old_id == "old_board_1"
        assert entry.new_id == "new_board_1"
        assert entry.migrated is False

    def test_register_multiple_entries(self) -> None:
        """Test registering multiple migrations."""
        tool = LegacyBoardIdMigrationTool()
        entry1 = tool.register("old_1", "new_1")
        entry2 = tool.register("old_2", "new_2")

        assert entry1.old_id == "old_1"
        assert entry2.old_id == "old_2"
        assert len(tool.pending()) == 2

    def test_register_duplicate_old_id_overwrites(self) -> None:
        """Test that registering with duplicate old_id overwrites."""
        tool = LegacyBoardIdMigrationTool()
        entry1 = tool.register("old_1", "new_1")
        entry2 = tool.register("old_1", "new_2")

        assert entry2.new_id == "new_2"
        assert tool.lookup_new("old_1") == "new_2"

    def test_migrate_marks_as_complete(self) -> None:
        """Test marking a migration as complete."""
        tool = LegacyBoardIdMigrationTool()
        tool.register("old_1", "new_1")
        entry = tool.migrate("old_1")

        assert entry.migrated is True
        assert len(tool.pending()) == 0
        assert len(tool.completed()) == 1

    def test_migrate_not_found_raises_keyerror(self) -> None:
        """Test migrate raises KeyError if old_id not registered."""
        tool = LegacyBoardIdMigrationTool()

        with pytest.raises(KeyError):
            tool.migrate("nonexistent")

    def test_lookup_new_returns_correct_id(self) -> None:
        """Test looking up new ID by old ID."""
        tool = LegacyBoardIdMigrationTool()
        tool.register("legacy_abc", "modern_xyz")

        result = tool.lookup_new("legacy_abc")
        assert result == "modern_xyz"

    def test_lookup_new_not_found_raises_keyerror(self) -> None:
        """Test lookup_new raises KeyError if old_id not registered."""
        tool = LegacyBoardIdMigrationTool()

        with pytest.raises(KeyError):
            tool.lookup_new("unknown")

    def test_pending_returns_unmigrated_entries(self) -> None:
        """Test pending() returns only unmigrated entries."""
        tool = LegacyBoardIdMigrationTool()
        tool.register("old_1", "new_1")
        tool.register("old_2", "new_2")
        tool.register("old_3", "new_3")

        tool.migrate("old_1")
        tool.migrate("old_3")

        pending = tool.pending()
        assert len(pending) == 1
        assert pending[0].old_id == "old_2"
        assert pending[0].migrated is False

    def test_completed_returns_migrated_entries(self) -> None:
        """Test completed() returns only migrated entries."""
        tool = LegacyBoardIdMigrationTool()
        tool.register("old_1", "new_1")
        tool.register("old_2", "new_2")
        tool.register("old_3", "new_3")

        tool.migrate("old_1")
        tool.migrate("old_3")

        completed = tool.completed()
        assert len(completed) == 2
        assert {e.old_id for e in completed} == {"old_1", "old_3"}

    def test_empty_tool_pending_and_completed(self) -> None:
        """Test pending() and completed() on empty tool."""
        tool = LegacyBoardIdMigrationTool()

        assert tool.pending() == []
        assert tool.completed() == []

    def test_workflow_register_lookup_migrate(self) -> None:
        """Test full workflow: register, lookup, migrate."""
        tool = LegacyBoardIdMigrationTool()

        # Register
        entry = tool.register("board_legacy_123", "board_wl_001")
        assert entry.migrated is False

        # Lookup
        new_id = tool.lookup_new("board_legacy_123")
        assert new_id == "board_wl_001"

        # Migrate
        migrated = tool.migrate("board_legacy_123")
        assert migrated.migrated is True

        # Verify in completed
        assert migrated in tool.completed()
        assert migrated not in tool.pending()
