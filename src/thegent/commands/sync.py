"""STUB MODULE - thegent.commands.sync

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OperationResult:
    """Result of a sync operation."""

    success: bool
    message: str
    details: dict[str, Any] | None = None


class SyncCommand:
    """Sync command implementation."""

    def __init__(self) -> None:
        self.name = "sync"

    def execute(self) -> OperationResult:
        """Execute the sync command."""
        return OperationResult(success=True, message="Sync completed")


class SyncOperationStatus:
    """Sync operation status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


__all__ = ["OperationResult", "SyncCommand", "SyncOperationStatus", "SyncResult"]


@dataclass
class SyncResult:
    """Result of a sync operation."""

    operation: str
    status: str
    message: str = ""
    data: dict[str, Any] | None = None

    def is_success(self) -> bool:
        """Check if operation was successful."""
        return self.status == "success"
