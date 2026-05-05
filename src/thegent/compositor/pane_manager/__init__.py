"""Stub module."""


class PaneManager:
    """Manager for compositor panes."""

    def __init__(self) -> None:
        self.panes: list[str] = []

    def add_pane(self, pane_id: str) -> None:
        """Add a pane."""
        self.panes.append(pane_id)

    def remove_pane(self, pane_id: str) -> None:
        """Remove a pane."""
        if pane_id in self.panes:
            self.panes.remove(pane_id)


__all__ = ["PaneManager"]
