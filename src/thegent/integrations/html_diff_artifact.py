"""HTML diff artifact generation for state comparison reporting.

Generate side-by-side HTML diff artifacts for local/remote state comparisons.

# @trace WL-244
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiffLine:
    """Represents a single line in a diff."""

    line_no: int
    kind: str
    content: str


class HtmlDiffArtifact:
    """Generates HTML diff artifacts for visual comparison."""

    @staticmethod
    def compute(before: list[str], after: list[str]) -> list[DiffLine]:
        """Compute line-by-line diff between two lists of lines.

        Uses a simple algorithm to identify added, removed, and unchanged lines.

        Args:
            before: List of lines before the change.
            after: List of lines after the change.

        Returns:
            List of DiffLine objects with kind ("added", "removed", "unchanged").
        """
        lines: list[DiffLine] = []
        before_set = set(before)
        after_set = set(after)

        # Lines that were removed
        removed_lines = before_set - after_set
        for i, line in enumerate(before):
            if line in removed_lines:
                lines.append(DiffLine(line_no=i + 1, kind="removed", content=line))
            elif line in after_set:
                lines.append(DiffLine(line_no=i + 1, kind="unchanged", content=line))

        # Lines that were added
        added_lines = after_set - before_set
        for i, line in enumerate(after):
            if line in added_lines:
                lines.append(DiffLine(line_no=i + 1, kind="added", content=line))

        logger.debug(
            f"Computed diff: {len(before)} before, {len(after)} after, "
            f"{len(lines)} total diff lines"
        )
        return lines

    @staticmethod
    def render_html(lines: list[DiffLine]) -> str:
        """Render diff lines as HTML with color-coded spans.

        Args:
            lines: List of DiffLine objects to render.

        Returns:
            HTML string with styled diff lines.
        """
        color_map = {"added": "#90EE90", "removed": "#FFB6C6", "unchanged": "#FFFFFF"}

        html_lines = ['<div style="font-family: monospace; white-space: pre-wrap;">']
        for line in lines:
            color = color_map.get(line.kind, "#FFFFFF")
            escaped_content = (
                line.content.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            html_line = f'<span style="background-color: {color};">{escaped_content}</span><br/>'
            html_lines.append(html_line)

        html_lines.append("</div>")
        html = "\n".join(html_lines)
        logger.debug(f"Rendered {len(lines)} lines as HTML")
        return html

    @staticmethod
    def summary(lines: list[DiffLine]) -> dict[str, int]:
        """Generate a summary of diff line counts by kind.

        Args:
            lines: List of DiffLine objects to summarize.

        Returns:
            Dictionary with counts per kind: {"added": N, "removed": N, "unchanged": N}.
        """
        counts = {"added": 0, "removed": 0, "unchanged": 0}
        for line in lines:
            if line.kind in counts:
                counts[line.kind] += 1
        logger.debug(f"Diff summary: {counts}")
        return counts
