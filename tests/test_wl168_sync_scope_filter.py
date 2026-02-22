"""Tests for WL-168: Sync Scope Filters.

Verifies that SyncScopeFilter correctly filters items based on
include and exclude patterns using substring matching.

# @trace WL-168
"""

from __future__ import annotations

import pytest

from thegent.integrations.sync_scope_filter import SyncScopeFilter


class TestSyncScopeFilterMatches:
    """WL-168: SyncScopeFilter.matches() behavior."""

    @pytest.mark.requirement("WL-168")
    def test_matches_no_patterns_accepts_all(self):
        """matches() with no patterns accepts all items."""
        f = SyncScopeFilter()

        assert f.matches("anything") is True
        assert f.matches("system:123") is True
        assert f.matches("") is True

    @pytest.mark.requirement("WL-168")
    def test_matches_single_include_pattern(self):
        """matches() with include pattern matches substrings."""
        f = SyncScopeFilter(include_patterns=["prod"])

        assert f.matches("prod-item") is True
        assert f.matches("item-prod") is True
        assert f.matches("prod") is True
        assert f.matches("staging-item") is False

    @pytest.mark.requirement("WL-168")
    def test_matches_multiple_include_patterns(self):
        """matches() accepts items matching any include pattern."""
        f = SyncScopeFilter(include_patterns=["prod", "staging"])

        assert f.matches("prod-db") is True
        assert f.matches("staging-server") is True
        assert f.matches("dev-env") is False

    @pytest.mark.requirement("WL-168")
    def test_matches_exclude_pattern_rejects(self):
        """matches() rejects items matching exclude pattern."""
        f = SyncScopeFilter(exclude_patterns=["temp"])

        assert f.matches("temp-file") is False
        assert f.matches("temporary") is False
        assert f.matches("file") is True

    @pytest.mark.requirement("WL-168")
    def test_matches_include_and_exclude_combined(self):
        """matches() applies both include and exclude patterns."""
        f = SyncScopeFilter(include_patterns=["prod"], exclude_patterns=["backup"])

        assert f.matches("prod-db") is True
        assert f.matches("prod-backup") is False
        assert f.matches("backup") is False
        assert f.matches("staging") is False

    @pytest.mark.requirement("WL-168")
    def test_matches_multiple_exclude_patterns(self):
        """matches() rejects items matching any exclude pattern."""
        f = SyncScopeFilter(exclude_patterns=["temp", "test", "debug"])

        assert f.matches("item") is True
        assert f.matches("temp-item") is False
        assert f.matches("item-test") is False
        assert f.matches("debug-data") is False

    @pytest.mark.requirement("WL-168")
    def test_matches_case_sensitive_substring(self):
        """matches() uses case-sensitive substring matching."""
        f = SyncScopeFilter(include_patterns=["PROD"])

        assert f.matches("PROD-item") is True
        assert f.matches("prod-item") is False

    @pytest.mark.requirement("WL-168")
    def test_matches_empty_pattern_matches_all(self):
        """matches() with empty string pattern matches everything."""
        f = SyncScopeFilter(include_patterns=[""])

        assert f.matches("anything") is True
        assert f.matches("") is True

    @pytest.mark.requirement("WL-168")
    def test_matches_empty_exclude_pattern(self):
        """matches() with empty exclude pattern rejects everything."""
        f = SyncScopeFilter(exclude_patterns=[""])

        # Empty string is substring of everything
        assert f.matches("anything") is False
        assert f.matches("") is False


class TestSyncScopeFilterFilter:
    """WL-168: SyncScopeFilter.filter() batch operations."""

    @pytest.mark.requirement("WL-168")
    def test_filter_no_patterns(self):
        """filter() with no patterns returns all items."""
        f = SyncScopeFilter()

        result = f.filter(["a", "b", "c"])

        assert result == ["a", "b", "c"]

    @pytest.mark.requirement("WL-168")
    def test_filter_include_pattern(self):
        """filter() returns only items matching include pattern."""
        f = SyncScopeFilter(include_patterns=["prod"])

        result = f.filter(["prod-a", "staging-b", "prod-c", "dev-d"])

        assert result == ["prod-a", "prod-c"]

    @pytest.mark.requirement("WL-168")
    def test_filter_exclude_pattern(self):
        """filter() removes items matching exclude pattern."""
        f = SyncScopeFilter(exclude_patterns=["temp"])

        result = f.filter(["file", "temp-a", "data", "temp-b"])

        assert result == ["file", "data"]

    @pytest.mark.requirement("WL-168")
    def test_filter_combined_patterns(self):
        """filter() applies both include and exclude."""
        f = SyncScopeFilter(include_patterns=["user"], exclude_patterns=["backup"])

        result = f.filter(["user-123", "user-backup", "item", "user-active", "backup"])

        assert result == ["user-123", "user-active"]

    @pytest.mark.requirement("WL-168")
    def test_filter_empty_list(self):
        """filter() handles empty input list."""
        f = SyncScopeFilter(include_patterns=["prod"])

        result = f.filter([])

        assert result == []

    @pytest.mark.requirement("WL-168")
    def test_filter_multiple_include_patterns(self):
        """filter() accepts items matching any include pattern."""
        f = SyncScopeFilter(include_patterns=["prod", "staging"])

        result = f.filter(["prod-a", "staging-b", "dev-c", "prod-d"])

        assert result == ["prod-a", "staging-b", "prod-d"]

    @pytest.mark.requirement("WL-168")
    def test_filter_order_preserved(self):
        """filter() maintains original item order."""
        f = SyncScopeFilter(include_patterns=["a"])

        result = f.filter(["xa", "ba", "ca", "da"])

        assert result == ["xa", "ba", "ca", "da"]

    @pytest.mark.requirement("WL-168")
    def test_filter_all_excluded(self):
        """filter() returns empty list if all items excluded."""
        f = SyncScopeFilter(exclude_patterns=["x"])

        result = f.filter(["ax", "bx", "cx"])

        assert result == []

    @pytest.mark.requirement("WL-168")
    def test_filter_none_match_include(self):
        """filter() returns empty list if no items match include."""
        f = SyncScopeFilter(include_patterns=["nomatch"])

        result = f.filter(["a", "b", "c"])

        assert result == []


class TestSyncScopeFilterEdgeCases:
    """WL-168: Edge cases and special scenarios."""

    @pytest.mark.requirement("WL-168")
    def test_filter_overlapping_patterns(self):
        """filter() handles overlapping include/exclude patterns correctly."""
        f = SyncScopeFilter(include_patterns=["prod"], exclude_patterns=["prod-backup"])

        result = f.filter(["prod-app", "prod-backup", "prod-data"])

        assert result == ["prod-app", "prod-data"]

    @pytest.mark.requirement("WL-168")
    def test_filter_special_characters_in_items(self):
        """filter() handles special characters in item names."""
        f = SyncScopeFilter(include_patterns=["$"])

        result = f.filter(["normal", "$special", "another$one"])

        assert result == ["$special", "another$one"]

    @pytest.mark.requirement("WL-168")
    def test_filter_numeric_patterns(self):
        """filter() can use numeric patterns for item filtering."""
        f = SyncScopeFilter(include_patterns=["2024"])

        result = f.filter(["2023-item", "2024-01", "2024-02", "2025-item"])

        assert result == ["2024-01", "2024-02"]
