"""Stub module."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class SpeculativeStrategy:
    """Speculative execution strategy."""
    
    def __init__(self) -> None:
        self.attempts = 0
    
    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        return {"executed": True}


@dataclass
class SpeculativeConfig:
    """Speculative configuration."""
    enabled: bool = False
    max_attempts: int = 3


__all__ = ["SpeculativeConfig", "SpeculativeStrategy", "compute_adaptive_timeout", "select_speculative_providers", "should_terminate_early"]


def should_terminate_early(task: dict, result: dict) -> bool:
    """Determine if speculative execution should terminate early.

    Args:
        task: The task being executed.
        result: The current result.

    Returns:
        True if should terminate early, False otherwise.
    """
    if result.get("status") == "error":
        return True
    if result.get("confidence", 1.0) >= 0.95:
        return True
    return False


def compute_adaptive_timeout(base_timeout: float, complexity: float = 1.0, load_factor: float = 1.0) -> float:
    """Compute adaptive timeout based on complexity and load."""
    return base_timeout * complexity * load_factor


def select_speculative_providers(task: dict, available_providers: list[str]) -> list[str]:
    """Select speculative providers for a task."""
    return available_providers[:2] if available_providers else []
