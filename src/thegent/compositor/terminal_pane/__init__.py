"""STUB MODULE - thegent.compositor.terminal_pane

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from typing import Any


class TerminalPane:
    """Terminal pane widget for compositor."""

    def __init__(self, width: int = 80, height: int = 24) -> None:
        self.width = width
        self.height = height
        self.content: list[str] = []
        self.cursor_x = 0
        self.cursor_y = 0

    def write(self, text: str) -> None:
        """Write text to the pane.

        Args:
            text: The text to write.
        """
        self.content.append(text)
        self.cursor_y += 1

    def clear(self) -> None:
        """Clear the pane content."""
        self.content.clear()
        self.cursor_x = 0
        self.cursor_y = 0

    def render(self) -> str:
        """Render the pane content.

        Returns:
            The rendered pane as a string.
        """
        return "\n".join(self.content)


__all__ = ["TerminalPane"]
