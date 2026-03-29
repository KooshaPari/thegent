"""Tests for HTML diff artifact generation.

# @trace WL-244
"""

from __future__ import annotations

import pytest

from thegent.integrations.html_diff_artifact import (
    DiffLine,
    HtmlDiffArtifact,
)


@pytest.mark.requirement("WL-244")
class TestDiffLine:
    """Test DiffLine dataclass."""

    def test_diff_line_creation(self) -> None:
        """Test creating a DiffLine."""
        line = DiffLine(line_no=1, kind="added", content="new line")
        assert line.line_no == 1
        assert line.kind == "added"
        assert line.content == "new line"

    def test_diff_line_fields(self) -> None:
        """Test DiffLine has expected fields."""
        line = DiffLine(line_no=5, kind="removed", content="old line")
        assert hasattr(line, "line_no")
        assert hasattr(line, "kind")
        assert hasattr(line, "content")


@pytest.mark.requirement("WL-244")
class TestHtmlDiffArtifact:
    """Test HtmlDiffArtifact."""

    def test_compute_identical(self) -> None:
        """Test compute with identical content."""
        before = ["line1", "line2", "line3"]
        after = ["line1", "line2", "line3"]
        lines = HtmlDiffArtifact.compute(before, after)
        assert len(lines) == 3
        assert all(line.kind == "unchanged" for line in lines)

    def test_compute_with_additions(self) -> None:
        """Test compute with added lines."""
        before = ["line1", "line2"]
        after = ["line1", "line2", "line3"]
        lines = HtmlDiffArtifact.compute(before, after)
        kinds = [line.kind for line in lines]
        assert "added" in kinds
        assert kinds.count("unchanged") >= 2

    def test_compute_with_removals(self) -> None:
        """Test compute with removed lines."""
        before = ["line1", "line2", "line3"]
        after = ["line1", "line2"]
        lines = HtmlDiffArtifact.compute(before, after)
        kinds = [line.kind for line in lines]
        assert "removed" in kinds
        assert kinds.count("unchanged") >= 2

    def test_compute_empty_before(self) -> None:
        """Test compute with empty before list."""
        before = []
        after = ["line1", "line2"]
        lines = HtmlDiffArtifact.compute(before, after)
        assert all(line.kind in ("added", "unchanged") for line in lines)

    def test_compute_empty_after(self) -> None:
        """Test compute with empty after list."""
        before = ["line1", "line2"]
        after = []
        lines = HtmlDiffArtifact.compute(before, after)
        assert all(line.kind in ("removed", "unchanged") for line in lines)

    def test_compute_both_empty(self) -> None:
        """Test compute with both lists empty."""
        before = []
        after = []
        lines = HtmlDiffArtifact.compute(before, after)
        assert lines == []

    def test_render_html_empty(self) -> None:
        """Test render_html with empty lines."""
        html = HtmlDiffArtifact.render_html([])
        assert '<div style="font-family: monospace; white-space: pre-wrap;">' in html
        assert "</div>" in html

    def test_render_html_single_line(self) -> None:
        """Test render_html with a single line."""
        lines = [DiffLine(line_no=1, kind="added", content="new line")]
        html = HtmlDiffArtifact.render_html(lines)
        assert "new line" in html
        assert "#90EE90" in html  # Green for added
        assert "<br/>" in html

    def test_render_html_color_coding(self) -> None:
        """Test render_html applies correct colors."""
        lines = [
            DiffLine(line_no=1, kind="added", content="added"),
            DiffLine(line_no=2, kind="removed", content="removed"),
            DiffLine(line_no=3, kind="unchanged", content="unchanged"),
        ]
        html = HtmlDiffArtifact.render_html(lines)
        assert "#90EE90" in html  # Green for added
        assert "#FFB6C6" in html  # Pink for removed
        assert "#FFFFFF" in html  # White for unchanged

    def test_render_html_escaping(self) -> None:
        """Test render_html escapes HTML entities."""
        lines = [DiffLine(line_no=1, kind="unchanged", content="<tag> & test")]
        html = HtmlDiffArtifact.render_html(lines)
        assert "&lt;tag&gt;" in html
        assert "&amp;" in html
        assert "&quot;" not in html  # Not needed for content
        assert "<tag>" not in html  # Original should not be present

    def test_summary_empty(self) -> None:
        """Test summary with empty lines."""
        summary = HtmlDiffArtifact.summary([])
        assert summary == {"added": 0, "removed": 0, "unchanged": 0}

    def test_summary_counts(self) -> None:
        """Test summary counts lines by kind."""
        lines = [
            DiffLine(line_no=1, kind="added", content="new1"),
            DiffLine(line_no=2, kind="added", content="new2"),
            DiffLine(line_no=3, kind="removed", content="old1"),
            DiffLine(line_no=4, kind="unchanged", content="same1"),
        ]
        summary = HtmlDiffArtifact.summary(lines)
        assert summary["added"] == 2
        assert summary["removed"] == 1
        assert summary["unchanged"] == 1

    def test_summary_only_one_kind(self) -> None:
        """Test summary with only one kind of line."""
        lines = [
            DiffLine(line_no=1, kind="added", content="new1"),
            DiffLine(line_no=2, kind="added", content="new2"),
            DiffLine(line_no=3, kind="added", content="new3"),
        ]
        summary = HtmlDiffArtifact.summary(lines)
        assert summary["added"] == 3
        assert summary["removed"] == 0
        assert summary["unchanged"] == 0
