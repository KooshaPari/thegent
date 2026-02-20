"""Circuit breaker service per subsystem (WP-2003, FR-007).

Delegates to execution.CircuitBreakerRegistry. Provides trip, recover, half-open semantics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from thegent.execution import CircuitBreakerRegistry

if TYPE_CHECKING:
    from pathlib import Path


def trip(session_dir: Path, target: str, category: str = "agent") -> None:
    """Record a failure; may open the circuit."""
    CircuitBreakerRegistry(session_dir).record_failure(target=target, category=category)


def is_open(session_dir: Path, target: str, category: str = "agent") -> bool:
    """True if circuit is open (blocked). False if closed or half-open (trial allowed)."""
    return CircuitBreakerRegistry(session_dir).is_open(target=target, category=category)


def should_allow(session_dir: Path, target: str, category: str = "agent") -> bool:
    """True if requests to target should be allowed (circuit closed or half-open)."""
    return not is_open(session_dir, target, category)
