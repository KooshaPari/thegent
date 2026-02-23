"""Tests for WL-189: WL Ignore List.

Verifies that workload IDs are correctly added, removed, and filtered.

# @trace WL-189
"""

from __future__ import annotations

import pytest

from thegent.integrations.wl_ignore_list import WLIgnoreList


@pytest.mark.requirement("WL-189")
class TestWLIgnoreList:
    """WL-189: WL ignore list."""

    def test_init_empty(self):
        """Newly created ignore list is empty."""
        ignore_list = WLIgnoreList()
        assert ignore_list.all_ignored() == []

    def test_add_single_id(self):
        """add() adds a single ID."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        assert "wl001" in ignore_list.all_ignored()

    def test_add_multiple_ids(self):
        """add() accumulates multiple IDs."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        ignore_list.add("wl002")
        ignore_list.add("wl003")
        ignored = ignore_list.all_ignored()
        assert len(ignored) == 3
        assert "wl001" in ignored
        assert "wl002" in ignored
        assert "wl003" in ignored

    def test_add_duplicate_id(self):
        """add() ignores duplicate IDs (set behavior)."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        ignore_list.add("wl001")
        assert len(ignore_list.all_ignored()) == 1

    def test_remove_existing_id(self):
        """remove() removes an ID from the list."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        ignore_list.add("wl002")
        ignore_list.remove("wl001")
        assert "wl001" not in ignore_list.all_ignored()
        assert "wl002" in ignore_list.all_ignored()

    def test_remove_non_existing_id(self):
        """remove() on non-existent ID does nothing."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        ignore_list.remove("wl999")  # Should not raise
        assert len(ignore_list.all_ignored()) == 1
        assert "wl001" in ignore_list.all_ignored()

    def test_remove_from_empty(self):
        """remove() from empty list does nothing."""
        ignore_list = WLIgnoreList()
        ignore_list.remove("wl001")  # Should not raise
        assert ignore_list.all_ignored() == []

    def test_is_ignored_true(self):
        """is_ignored() returns True for ignored IDs."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        assert ignore_list.is_ignored("wl001") is True

    def test_is_ignored_false(self):
        """is_ignored() returns False for non-ignored IDs."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        assert ignore_list.is_ignored("wl002") is False

    def test_is_ignored_empty_list(self):
        """is_ignored() returns False on empty list."""
        ignore_list = WLIgnoreList()
        assert ignore_list.is_ignored("wl001") is False

    def test_all_ignored_returns_sorted(self):
        """all_ignored() returns sorted list."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl003")
        ignore_list.add("wl001")
        ignore_list.add("wl002")
        assert ignore_list.all_ignored() == ["wl001", "wl002", "wl003"]

    def test_filter_empty_list(self):
        """filter() with empty list returns empty."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        result = ignore_list.filter([])
        assert result == []

    def test_filter_no_ignored(self):
        """filter() returns all IDs when none are ignored."""
        ignore_list = WLIgnoreList()
        result = ignore_list.filter(["wl001", "wl002", "wl003"])
        assert result == ["wl001", "wl002", "wl003"]

    def test_filter_all_ignored(self):
        """filter() returns empty when all IDs are ignored."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        ignore_list.add("wl002")
        ignore_list.add("wl003")
        result = ignore_list.filter(["wl001", "wl002", "wl003"])
        assert result == []

    def test_filter_partial_ignored(self):
        """filter() removes only ignored IDs."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl002")
        result = ignore_list.filter(["wl001", "wl002", "wl003"])
        assert result == ["wl001", "wl003"]

    def test_filter_preserves_order(self):
        """filter() preserves order of input list."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl002")
        result = ignore_list.filter(["wl005", "wl002", "wl001"])
        assert result == ["wl005", "wl001"]

    def test_add_then_remove_then_add(self):
        """Add, remove, and re-add operations work correctly."""
        ignore_list = WLIgnoreList()
        ignore_list.add("wl001")
        assert ignore_list.is_ignored("wl001")
        ignore_list.remove("wl001")
        assert not ignore_list.is_ignored("wl001")
        ignore_list.add("wl001")
        assert ignore_list.is_ignored("wl001")
