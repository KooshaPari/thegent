"""Stub module."""

from dataclasses import dataclass


class DagCycleError(Exception):
    """Error raised when a cycle is detected in a DAG."""


class DependencyRouter:
    """Router for dependencies in a DAG."""

    def __init__(self) -> None:
        self.routes: dict = {}

    def route(self, node_id: str) -> list[str]:
        """Route dependencies for a node."""
        return self.routes.get(node_id, [])


@dataclass
class DagTask:
    """Task node in a DAG."""

    id: str = ""
    dependencies: list = None
    priority: int = 0

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


class DagPrioritizer:
    """Prioritizer for DAG nodes."""

    def __init__(self) -> None:
        self.priorities: dict[str, int] = {}

    def prioritize(self, nodes: list[str]) -> list[str]:
        """Prioritize nodes for execution."""
        return sorted(nodes, key=lambda n: self.priorities.get(n, 0))


__all__ = ["DagCycleError", "DependencyRouter", "DagPrioritizer", "DagTask"]
