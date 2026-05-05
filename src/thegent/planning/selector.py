"""Stub module."""
from __future__ import annotations
from dataclasses import dataclass


class Selector:
    """Selector for planning."""

    def __init__(self) -> None:
        self._options: list = []

    def select(self) -> str | None:
        if self._options:
            return self._options[0]
        return None


class ObjectiveSelector:
    """Selector for objectives."""

    def __init__(self) -> None:
        self._objectives: list = []

    def add_objective(self, objective: dict) -> None:
        """Add an objective."""
        self._objectives.append(objective)

    def select_next(self) -> dict | None:
        """Select the next objective."""
        if self._objectives:
            return self._objectives.pop(0)
        return None

    def get_all(self) -> list:
        """Get all objectives."""
        return self._objectives


__all__ = ["Selector", "ObjectiveSelector", "ObjectiveWeights", "get_objective_profile"]


@dataclass
class ObjectiveWeights:
    """Weights for different objective criteria."""
    priority: float = 1.0
    urgency: float = 1.0
    complexity: float = 1.0
    dependencies: float = 0.5
    resources: float = 0.3

    def score(self, objective: dict) -> float:
        """Calculate weighted score for an objective."""
        score = 0.0
        score += self.priority * objective.get("priority", 0)
        score += self.urgency * objective.get("urgency", 0)
        score += self.complexity * objective.get("complexity", 0)
        return score


def get_objective_profile(profile_name: str) -> ObjectiveWeights:
    """Get a predefined objective weight profile.

    Args:
        profile_name: Name of the profile ("balanced", "speed", "quality").

    Returns:
        ObjectiveWeights instance.
    """
    profiles = {
        "balanced": ObjectiveWeights(priority=1.0, urgency=1.0, complexity=1.0),
        "speed": ObjectiveWeights(priority=0.5, urgency=2.0, complexity=0.5),
        "quality": ObjectiveWeights(priority=1.0, urgency=0.5, complexity=2.0),
    }
    return profiles.get(profile_name, ObjectiveWeights())
