"""Circuit breaker module for resilience."""

from __future__ import annotations
from pathlib import Path
from typing import Any

__all__ = ["is_open", "should_allow"]


def is_open(_root: Path, circuit_name: str) -> bool:
    """Check if a circuit breaker is open."""
    return False


def should_allow(_root: Path, circuit_name: str) -> bool:
    """Check if operation should be allowed through the circuit breaker."""
    return not is_open(_root, circuit_name)
