"""Priority mappings between Linear and local workstream values."""

from __future__ import annotations

from enum import IntEnum

__all__ = ["LinearPriority", "LocalPriority", "linear_to_local", "local_to_linear"]


class LinearPriority(IntEnum):
    """Linear issue priorities."""

    NO_PRIORITY = 0
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class LocalPriority(IntEnum):
    """Local normalized priority values."""

    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3


_LINEAR_TO_LOCAL = {
    LinearPriority.NO_PRIORITY: LocalPriority.P3,
    LinearPriority.URGENT: LocalPriority.P0,
    LinearPriority.HIGH: LocalPriority.P1,
    LinearPriority.MEDIUM: LocalPriority.P2,
    LinearPriority.LOW: LocalPriority.P3,
}

_LOCAL_TO_LINEAR = {
    LocalPriority.P0: LinearPriority.URGENT,
    LocalPriority.P1: LinearPriority.HIGH,
    LocalPriority.P2: LinearPriority.MEDIUM,
    LocalPriority.P3: LinearPriority.LOW,
}


def linear_to_local(priority: LinearPriority | int) -> LocalPriority:
    """Map a Linear priority enum or integer to the local priority scale."""
    try:
        return _LINEAR_TO_LOCAL[LinearPriority(priority)]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unsupported Linear priority: {priority!r}") from exc



def local_to_linear(priority: LocalPriority | str | int) -> LinearPriority:
    """Map a local priority enum, name, or integer to the Linear scale."""
    try:
        resolved = LocalPriority[priority] if isinstance(priority, str) else LocalPriority(priority)
        return _LOCAL_TO_LINEAR[resolved]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"unsupported local priority: {priority!r}") from exc
