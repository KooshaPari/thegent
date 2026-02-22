"""Tests for thegent.integrations.dry_run_diff — Human-Readable Dry-Run Diffs.

@trace WL-186
"""

from __future__ import annotations

import pytest

from thegent.integrations.dry_run_diff import (
    DryRunDiff,
    DryRunRenderer,
    FieldDiff,
)


class TestFieldDiffCreation:
    """Test FieldDiff dataclass creation."""

    @pytest.mark.requirement("WL-186")
    def test_create_field_diff(self) -> None:
        """Can create a FieldDiff."""
        diff = FieldDiff(
            field="status",
            local_value="TODO",
            remote_value="IN_PROGRESS",
            direction="local→remote",
        )

        assert diff.field == "status"
        assert diff.local_value == "TODO"
        assert diff.remote_value == "IN_PROGRESS"
        assert diff.direction == "local→remote"


class TestDryRunDiffCreation:
    """Test DryRunDiff dataclass creation."""

    @pytest.mark.requirement("WL-186")
    def test_create_empty_diff(self) -> None:
        """Can create a DryRunDiff with no field diffs."""
        diff = DryRunDiff(
            wl_id="WL-001",
            connector="github",
            diffs=[],
        )

        assert diff.wl_id == "WL-001"
        assert diff.connector == "github"
        assert diff.diffs == []

    @pytest.mark.requirement("WL-186")
    def test_create_diff_with_fields(self) -> None:
        """Can create a DryRunDiff with field diffs."""
        field_diffs = [
            FieldDiff("status", "TODO", "IN_PROGRESS", "local→remote"),
            FieldDiff("priority", "P1", "P2", "local→remote"),
        ]

        diff = DryRunDiff(
            wl_id="WL-002",
            connector="linear",
            diffs=field_diffs,
        )

        assert len(diff.diffs) == 2


class TestDryRunRendererComputeDiff:
    """Test DryRunRenderer.compute_diff operations."""

    @pytest.mark.requirement("WL-186")
    def test_compute_diff_no_changes(self) -> None:
        """compute_diff returns empty diffs when values match."""
        local = {"status": "TODO", "title": "Test"}
        remote = {"status": "TODO", "title": "Test"}
        fields = ["status", "title"]

        diff = DryRunRenderer.compute_diff("WL-001", "github", local, remote, fields)

        assert diff.wl_id == "WL-001"
        assert diff.connector == "github"
        assert diff.diffs == []

    @pytest.mark.requirement("WL-186")
    def test_compute_diff_single_change(self) -> None:
        """compute_diff detects single field change."""
        local = {"status": "IN_PROGRESS", "title": "Test"}
        remote = {"status": "TODO", "title": "Test"}
        fields = ["status", "title"]

        diff = DryRunRenderer.compute_diff("WL-001", "github", local, remote, fields)

        assert len(diff.diffs) == 1
        assert diff.diffs[0].field == "status"
        assert diff.diffs[0].local_value == "IN_PROGRESS"
        assert diff.diffs[0].remote_value == "TODO"

    @pytest.mark.requirement("WL-186")
    def test_compute_diff_multiple_changes(self) -> None:
        """compute_diff detects multiple field changes."""
        local = {
            "status": "IN_PROGRESS",
            "priority": "P2",
            "title": "Test",
        }
        remote = {
            "status": "TODO",
            "priority": "P1",
            "title": "Test",
        }
        fields = ["status", "priority", "title"]

        diff = DryRunRenderer.compute_diff("WL-001", "github", local, remote, fields)

        assert len(diff.diffs) == 2
        field_names = {fd.field for fd in diff.diffs}
        assert field_names == {"status", "priority"}

    @pytest.mark.requirement("WL-186")
    def test_compute_diff_missing_fields(self) -> None:
        """compute_diff handles missing fields (treats as empty string)."""
        local = {"status": "TODO"}
        remote = {"status": "TODO", "priority": "P1"}
        fields = ["status", "priority"]

        diff = DryRunRenderer.compute_diff("WL-001", "github", local, remote, fields)

        assert len(diff.diffs) == 1
        assert diff.diffs[0].field == "priority"
        assert diff.diffs[0].local_value == ""
        assert diff.diffs[0].remote_value == "P1"

    @pytest.mark.requirement("WL-186")
    def test_compute_diff_converts_to_string(self) -> None:
        """compute_diff converts values to strings."""
        local = {"count": 42, "status": "TODO"}
        remote = {"count": 100, "status": "TODO"}
        fields = ["count", "status"]

        diff = DryRunRenderer.compute_diff("WL-001", "github", local, remote, fields)

        assert len(diff.diffs) == 1
        assert diff.diffs[0].local_value == "42"
        assert diff.diffs[0].remote_value == "100"


class TestDryRunRendererRenderText:
    """Test DryRunRenderer.render_text operations."""

    @pytest.mark.requirement("WL-186")
    def test_render_text_no_changes(self) -> None:
        """render_text shows (no changes) for empty diffs."""
        diff = DryRunDiff(wl_id="WL-001", connector="github", diffs=[])

        text = DryRunRenderer.render_text(diff)

        assert text == "WL-001 [github]: (no changes)"

    @pytest.mark.requirement("WL-186")
    def test_render_text_single_change(self) -> None:
        """render_text formats single field change."""
        field_diffs = [
            FieldDiff("status", "TODO", "IN_PROGRESS", "local→remote"),
        ]
        diff = DryRunDiff(wl_id="WL-001", connector="github", diffs=field_diffs)

        text = DryRunRenderer.render_text(diff)

        assert "WL-001 [github]:" in text
        assert 'status: "TODO" → "IN_PROGRESS"' in text

    @pytest.mark.requirement("WL-186")
    def test_render_text_multiple_changes(self) -> None:
        """render_text formats multiple field changes."""
        field_diffs = [
            FieldDiff("status", "TODO", "IN_PROGRESS", "local→remote"),
            FieldDiff("priority", "P1", "P2", "local→remote"),
        ]
        diff = DryRunDiff(wl_id="WL-001", connector="github", diffs=field_diffs)

        text = DryRunRenderer.render_text(diff)

        assert "WL-001 [github]:" in text
        assert 'status: "TODO" → "IN_PROGRESS"' in text
        assert 'priority: "P1" → "P2"' in text

    @pytest.mark.requirement("WL-186")
    def test_render_text_format_exact(self) -> None:
        """render_text produces exact expected format."""
        field_diffs = [
            FieldDiff("status", "TODO", "DONE", "local→remote"),
        ]
        diff = DryRunDiff(wl_id="WL-123", connector="linear", diffs=field_diffs)

        text = DryRunRenderer.render_text(diff)

        lines = text.split("\n")
        assert lines[0] == "WL-123 [linear]:"
        assert lines[1] == '  status: "TODO" → "DONE"'


class TestDryRunRendererRenderBatch:
    """Test DryRunRenderer.render_batch operations."""

    @pytest.mark.requirement("WL-186")
    def test_render_batch_empty(self) -> None:
        """render_batch returns (no changes) for empty list."""
        diffs: list[DryRunDiff] = []

        text = DryRunRenderer.render_batch(diffs)

        assert text == "(no changes)"

    @pytest.mark.requirement("WL-186")
    def test_render_batch_single_item_no_changes(self) -> None:
        """render_batch renders single item with no changes."""
        diffs = [DryRunDiff(wl_id="WL-001", connector="github", diffs=[])]

        text = DryRunRenderer.render_batch(diffs)

        assert text == "WL-001 [github]: (no changes)"

    @pytest.mark.requirement("WL-186")
    def test_render_batch_multiple_items(self) -> None:
        """render_batch separates multiple items with blank lines."""
        diffs = [
            DryRunDiff(
                wl_id="WL-001",
                connector="github",
                diffs=[FieldDiff("status", "TODO", "IN_PROGRESS", "local→remote")],
            ),
            DryRunDiff(
                wl_id="WL-002",
                connector="linear",
                diffs=[FieldDiff("priority", "P1", "P2", "local→remote")],
            ),
        ]

        text = DryRunRenderer.render_batch(diffs)

        lines = text.split("\n\n")
        assert len(lines) == 2
        assert "WL-001 [github]:" in lines[0]
        assert "WL-002 [linear]:" in lines[1]

    @pytest.mark.requirement("WL-186")
    def test_render_batch_mixed_changes(self) -> None:
        """render_batch handles items with and without changes."""
        diffs = [
            DryRunDiff(
                wl_id="WL-001",
                connector="github",
                diffs=[FieldDiff("status", "TODO", "IN_PROGRESS", "local→remote")],
            ),
            DryRunDiff(wl_id="WL-002", connector="linear", diffs=[]),
            DryRunDiff(
                wl_id="WL-003",
                connector="github",
                diffs=[FieldDiff("priority", "P1", "P2", "local→remote")],
            ),
        ]

        text = DryRunRenderer.render_batch(diffs)

        assert "WL-001 [github]:" in text
        assert "WL-002 [linear]: (no changes)" in text
        assert "WL-003 [github]:" in text

    @pytest.mark.requirement("WL-186")
    def test_render_batch_three_items_separated(self) -> None:
        """render_batch uses exactly blank line separation."""
        diffs = [
            DryRunDiff(wl_id="WL-001", connector="github", diffs=[]),
            DryRunDiff(wl_id="WL-002", connector="linear", diffs=[]),
            DryRunDiff(wl_id="WL-003", connector="github", diffs=[]),
        ]

        text = DryRunRenderer.render_batch(diffs)

        # Should have exactly 2 blank lines (between 3 items)
        parts = text.split("\n\n")
        assert len(parts) == 3


class TestDryRunRendererIntegration:
    """Integration tests for DryRunRenderer."""

    @pytest.mark.requirement("WL-186")
    def test_full_workflow_compute_and_render(self) -> None:
        """Full workflow: compute diffs and render them."""
        local = {
            "status": "IN_PROGRESS",
            "priority": "P2",
            "title": "Updated Title",
        }
        remote = {
            "status": "TODO",
            "priority": "P1",
            "title": "Updated Title",
        }
        fields = ["status", "priority", "title"]

        diff = DryRunRenderer.compute_diff("WL-042", "github", local, remote, fields)
        text = DryRunRenderer.render_text(diff)

        assert "WL-042 [github]:" in text
        assert 'status: "IN_PROGRESS" → "TODO"' in text
        assert 'priority: "P2" → "P1"' in text
        assert "title" not in text  # unchanged field

    @pytest.mark.requirement("WL-186")
    def test_full_workflow_batch_diffs(self) -> None:
        """Full workflow: compute multiple diffs and render batch."""
        diffs = [
            DryRunRenderer.compute_diff(
                "WL-001",
                "github",
                {"status": "IN_PROGRESS"},
                {"status": "TODO"},
                ["status"],
            ),
            DryRunRenderer.compute_diff(
                "WL-002",
                "linear",
                {"priority": "P1"},
                {"priority": "P1"},
                ["priority"],
            ),
        ]

        batch_text = DryRunRenderer.render_batch(diffs)

        assert "WL-001 [github]:" in batch_text
        assert "WL-002 [linear]: (no changes)" in batch_text
