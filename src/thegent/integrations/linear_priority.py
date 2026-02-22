"""Linear Priority round-trip conversion for workstream sync.

# @trace WL-165
"""

from __future__ import annotations

from enum import IntEnum


class LinearPriority(IntEnum):
    """Linear.app priority levels."""

    NO_PRIORITY = 0
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class LocalPriority(IntEnum):
    """thegent local priority levels."""

    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3


def linear_to_local(linear_prio: LinearPriority | int) -> LocalPriority:
    """Convert Linear priority to local priority.

    Args:
        linear_prio: LinearPriority enum value or integer.

    Returns:
        LocalPriority enum value.

    Raises:
        ValueError: If linear_prio is not a valid LinearPriority value.
    """
    prio_int = int(linear_prio)

    # Map Linear priorities to local priorities
    mapping = {
        LinearPriority.URGENT: LocalPriority.P0,
        LinearPriority.HIGH: LocalPriority.P1,
        LinearPriority.MEDIUM: LocalPriority.P2,
        LinearPriority.LOW: LocalPriority.P3,
        LinearPriority.NO_PRIORITY: LocalPriority.P3,
    }

    # Convert int to LinearPriority enum for dict lookup
    try:
        linear_enum = LinearPriority(prio_int)
    except ValueError:
        raise ValueError(f"Invalid LinearPriority value: {prio_int}") from None

    return mapping[linear_enum]


def local_to_linear(local_prio: LocalPriority | str) -> LinearPriority:
    """Convert local priority to Linear priority.

    Args:
        local_prio: LocalPriority enum value or string.

    Returns:
        LinearPriority enum value.

    Raises:
        ValueError: If local_prio is not a valid LocalPriority value.
    """
    if isinstance(local_prio, str):
        try:
            local_prio = LocalPriority[local_prio]
        except KeyError:
            raise ValueError(f"Invalid LocalPriority string: {local_prio}") from None

    # Map local priorities to Linear priorities
    mapping = {
        LocalPriority.P0: LinearPriority.URGENT,
        LocalPriority.P1: LinearPriority.HIGH,
        LocalPriority.P2: LinearPriority.MEDIUM,
        LocalPriority.P3: LinearPriority.LOW,
    }

    return mapping[local_prio]
