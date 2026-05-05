"""Stub module."""
from dataclasses import dataclass


@dataclass
class DependencyRouter:
    """Router for dependencies."""

    def route(self, task_id: str) -> list[str]:
        """Route task dependencies."""
        return []


__all__ = ["DependencyRouter"]
