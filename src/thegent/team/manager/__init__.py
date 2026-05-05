"""Stub module."""

from typing import Any


class TeamManager:
    """Team manager stub."""

    def __init__(self) -> None:
        self.teams: dict[str, Any] = {}

    def create_team(self, name: str) -> None:
        """Create a team."""
        self.teams[name] = {}


__all__ = ["TeamManager"]
