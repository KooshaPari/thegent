"""Local-vs-Remote integrity scanner for sync validation.

# @trace WL-174
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SeverityLevel(str, Enum):
    """Severity levels for integrity mismatches."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IntegrityMismatch:
    """Represents a mismatch between local and remote item state.

    Attributes:
        wl_id: Work stream item identifier.
        field: Field name (e.g., 'status', 'priority').
        local_value: Value in local state.
        remote_value: Value in remote state.
        connector: Connector name (e.g., 'github', 'linear').
        severity: Severity level of the mismatch.
    """

    wl_id: str
    field: str
    local_value: Any
    remote_value: Any
    connector: str
    severity: SeverityLevel | str


class IntegrityScanner:
    """Scanner for detecting local-vs-remote integrity mismatches."""

    def __init__(self) -> None:
        """Initialize the integrity scanner."""
        pass

    def scan(
        self,
        local_items: list[dict[str, Any]],
        remote_items: list[dict[str, Any]],
        connector: str,
    ) -> list[IntegrityMismatch]:
        """Scan for integrity mismatches between local and remote items.

        Compares 'status' and 'priority' fields. Returns a list of detected
        mismatches.

        Args:
            local_items: List of local item dictionaries. Each must have 'id' field.
            remote_items: List of remote item dictionaries. Each must have 'id' field.
            connector: Name of the connector (e.g., 'github', 'linear').

        Returns:
            List of IntegrityMismatch objects.
        """
        mismatches: list[IntegrityMismatch] = []

        # Build remote lookup by id
        remote_by_id: dict[str, dict[str, Any]] = {
            item.get("id"): item for item in remote_items if item.get("id")
        }

        # Compare fields for each local item
        for local_item in local_items:
            local_id = local_item.get("id")
            if not local_id or local_id not in remote_by_id:
                continue

            remote_item = remote_by_id[local_id]

            # Check status field
            local_status = local_item.get("status")
            remote_status = remote_item.get("status")
            if local_status != remote_status and local_status is not None and remote_status is not None:
                mismatches.append(
                    IntegrityMismatch(
                        wl_id=local_id,
                        field="status",
                        local_value=local_status,
                        remote_value=remote_status,
                        connector=connector,
                        severity=SeverityLevel.MEDIUM,
                    )
                )

            # Check priority field
            local_priority = local_item.get("priority")
            remote_priority = remote_item.get("priority")
            if (
                local_priority != remote_priority
                and local_priority is not None
                and remote_priority is not None
            ):
                mismatches.append(
                    IntegrityMismatch(
                        wl_id=local_id,
                        field="priority",
                        local_value=local_priority,
                        remote_value=remote_priority,
                        connector=connector,
                        severity=SeverityLevel.LOW,
                    )
                )

        return mismatches
