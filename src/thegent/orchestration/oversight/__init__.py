"""Orchestration oversight module."""
from __future__ import annotations
from pathlib import Path
from typing import Any

__all__ = ["get_oversight_action", "should_trigger_oversight"]


def should_trigger_oversight(
    path: Path,
    agent: str,
    attempts: int,
    threshold: int = 3,
) -> bool:
    """Check if oversight should be triggered."""
    return attempts >= threshold


def get_oversight_action(
    agent: int | str,
    context: dict[str, Any] | None = None,
) -> str:
    """Get the oversight action for the given agent."""
    if isinstance(agent, int):
        if agent >= 5:
            return "escalate"
        elif agent >= 3:
            return "pause"
    return "continue"
