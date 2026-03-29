"""Tests for thegent.integrations.header_normalizer — WL header normalization.

@trace WL-184
"""

from __future__ import annotations

import pytest

from thegent.integrations.header_normalizer import (
    NormalizationResult,
    WLHeaderNormalizer,
)


class TestNormalizationResult:
    """Test NormalizationResult dataclass. @trace WL-184"""

    @pytest.mark.requirement("WL-184")
    def test_create_result(self) -> None:
        """Can create a NormalizationResult with all fields."""
        result = NormalizationResult(
            wl_id="WL-123",
            original="wl-123: foo bar",
            normalized="WL-123: Foo Bar",
            changed=True,
        )

        assert result.wl_id == "WL-123"
        assert result.original == "wl-123: foo bar"
        assert result.normalized == "WL-123: Foo Bar"
        assert result.changed is True

    @pytest.mark.requirement("WL-184")
    def test_create_result_no_change(self) -> None:
        """Can create a NormalizationResult with changed=False."""
        result = NormalizationResult(
            wl_id="WL-456",
            original="WL-456: Foo",
            normalized="WL-456: Foo",
            changed=False,
        )

        assert result.changed is False


class TestWLHeaderNormalizer:
    """Test WLHeaderNormalizer operations. @trace WL-184"""

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_uppercase_wl_id(self) -> None:
        """normalize_title uppercases WL ID."""
        result = WLHeaderNormalizer.normalize_title("wl-123: test")

        assert result.startswith("WL-123")

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_title_case(self) -> None:
        """normalize_title capitalizes title after WL ID."""
        result = WLHeaderNormalizer.normalize_title("wl-123: foo bar baz")

        assert result == "WL-123: Foo Bar Baz"

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_strips_whitespace(self) -> None:
        """normalize_title strips leading/trailing whitespace."""
        result = WLHeaderNormalizer.normalize_title("  wl-456: test  ")

        assert result == "WL-456: Test"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_strips_punctuation(self) -> None:
        """normalize_title strips trailing punctuation."""
        result = WLHeaderNormalizer.normalize_title("wl-789: test title...")

        assert result == "WL-789: Test Title"
        assert not result.endswith(".")

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_no_wl_id(self) -> None:
        """normalize_title handles titles without WL ID."""
        result = WLHeaderNormalizer.normalize_title("just a title")

        assert result == "Just A Title"

    @pytest.mark.requirement("WL-184")
    def test_normalize_title_already_normalized(self) -> None:
        """normalize_title handles already-normalized titles."""
        result = WLHeaderNormalizer.normalize_title("WL-123: Foo Bar")

        assert result == "WL-123: Foo Bar"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_backlog(self) -> None:
        """normalize_status converts 'backlog' to 'BACKLOG'."""
        result = WLHeaderNormalizer.normalize_status("backlog")

        assert result == "BACKLOG"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_in_progress(self) -> None:
        """normalize_status converts 'in_progress' to 'IN_PROGRESS'."""
        result = WLHeaderNormalizer.normalize_status("in_progress")

        assert result == "IN_PROGRESS"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_completed(self) -> None:
        """normalize_status converts 'completed' to 'COMPLETED'."""
        result = WLHeaderNormalizer.normalize_status("completed")

        assert result == "COMPLETED"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_blocked(self) -> None:
        """normalize_status converts 'blocked' to 'BLOCKED'."""
        result = WLHeaderNormalizer.normalize_status("blocked")

        assert result == "BLOCKED"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_unknown_uppercased(self) -> None:
        """normalize_status uppercases unknown statuses."""
        result = WLHeaderNormalizer.normalize_status("pending")

        assert result == "PENDING"

    @pytest.mark.requirement("WL-184")
    def test_normalize_status_case_insensitive(self) -> None:
        """normalize_status is case-insensitive for known statuses."""
        result = WLHeaderNormalizer.normalize_status("In_Progress")

        assert result == "IN_PROGRESS"

    @pytest.mark.requirement("WL-184")
    def test_normalize_priority_p0(self) -> None:
        """normalize_priority converts 'p0' to 'P0'."""
        result = WLHeaderNormalizer.normalize_priority("p0")

        assert result == "P0"

    @pytest.mark.requirement("WL-184")
    def test_normalize_priority_p9(self) -> None:
        """normalize_priority converts 'p9' to 'P9'."""
        result = WLHeaderNormalizer.normalize_priority("p9")

        assert result == "P9"

    @pytest.mark.requirement("WL-184")
    def test_normalize_priority_already_uppercase(self) -> None:
        """normalize_priority handles already-uppercase P values."""
        result = WLHeaderNormalizer.normalize_priority("P1")

        assert result == "P1"

    @pytest.mark.requirement("WL-184")
    def test_normalize_priority_non_p_pattern(self) -> None:
        """normalize_priority uppercases non-P patterns."""
        result = WLHeaderNormalizer.normalize_priority("high")

        assert result == "HIGH"

    @pytest.mark.requirement("WL-184")
    def test_normalize_priority_strips_whitespace(self) -> None:
        """normalize_priority strips whitespace."""
        result = WLHeaderNormalizer.normalize_priority("  p2  ")

        assert result == "P2"

    @pytest.mark.requirement("WL-184")
    def test_normalize_record_all_fields(self) -> None:
        """normalize_record normalizes all fields."""
        record = {
            "wl_id": "wl-123",
            "title": "wl-123: test title",
            "status": "backlog",
            "priority": "p1",
        }

        result = WLHeaderNormalizer.normalize_record(record)

        assert result.wl_id == "wl-123"
        assert result.changed is True
        assert "WL-123" in result.normalized
        assert "BACKLOG" in result.normalized
        assert "P1" in result.normalized

    @pytest.mark.requirement("WL-184")
    def test_normalize_record_no_change_needed(self) -> None:
        """normalize_record detects when no changes needed."""
        record = {
            "wl_id": "WL-456",
            "title": "WL-456: Already Normalized",
            "status": "COMPLETED",
            "priority": "P0",
        }

        result = WLHeaderNormalizer.normalize_record(record)

        assert result.changed is False

    @pytest.mark.requirement("WL-184")
    def test_normalize_record_missing_field_raises(self) -> None:
        """normalize_record raises KeyError for missing required field."""
        record = {
            "wl_id": "WL-123",
            "title": "test",
            # missing status and priority
        }

        with pytest.raises(KeyError):
            WLHeaderNormalizer.normalize_record(record)

    @pytest.mark.requirement("WL-184")
    def test_normalize_record_partial_changes(self) -> None:
        """normalize_record handles partial field changes."""
        record = {
            "wl_id": "WL-789",
            "title": "WL-789: Already Good Title",
            "status": "backlog",  # needs change
            "priority": "P3",  # doesn't need change
        }

        result = WLHeaderNormalizer.normalize_record(record)

        assert result.changed is True
        assert "BACKLOG" in result.normalized
        assert "P3" in result.normalized

    @pytest.mark.requirement("WL-184")
    def test_normalize_record_original_unchanged(self) -> None:
        """normalize_record preserves original record input."""
        record = {
            "wl_id": "WL-111",
            "title": "wl-111: test",
            "status": "in_progress",
            "priority": "p2",
        }
        original_copy = record.copy()

        WLHeaderNormalizer.normalize_record(record)

        # Input record should not be modified
        assert record == original_copy
