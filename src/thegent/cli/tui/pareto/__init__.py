"""Stub module."""


class ParetoTuiSession:
    """TUI session for Pareto chart visualization."""

    def __init__(self) -> None:
        self.active: bool = False

    def start(self) -> None:
        """Start the TUI session."""
        self.active = True

    def stop(self) -> None:
        """Stop the TUI session."""
        self.active = False


__all__ = ["ParetoTuiSession"]
