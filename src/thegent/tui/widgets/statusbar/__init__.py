"""STUB MODULE - thegent.tui.widgets.statusbar

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from typing import Any


def compute_context_usage_display(used: float, total: float) -> str:
    """Compute context usage display string.

    Args:
        used: Amount of context used.
        total: Total context available.

    Returns:
        Formatted display string showing usage percentage.
    """
    if total <= 0:
        return "N/A"
    percentage = (used / total) * 100
    return f"{percentage:.1f}% ({used:.0f}/{total:.0f})"


class StatusBar:
    """Status bar widget stub."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add_item(self, item: str) -> None:
        """Add an item to the status bar."""
        self.items.append(item)

    def render(self) -> str:
        """Render the status bar."""
        return " | ".join(self.items)


__all__ = ["StatusBar", "compute_context_usage_display"]
