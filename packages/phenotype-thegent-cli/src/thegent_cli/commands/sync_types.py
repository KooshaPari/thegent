"""Data types for sync operations.

Provides OperationResult, SyncResult, and SyncOperationStatus
for tracking sync operation outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class SyncOperationStatus(str, Enum):
    """Status of a single sync operation."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


@dataclass
class OperationResult:
    """Result of a single sync operation."""

    operation: str
    status: SyncOperationStatus
    message: str = ""
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def ok(self) -> bool:
        """Check if operation succeeded or was dry run."""
        return self.status in (SyncOperationStatus.SUCCESS, SyncOperationStatus.DRY_RUN)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation": self.operation,
            "status": self.status.value,
            "message": self.message,
            "duration": self.duration,
            "details": self.details,
            "errors": self.errors,
            "changes": self.changes,
            "timestamp": self.timestamp,
        }


@dataclass
class SyncResult:
    """Aggregate result of a sync run (one or more operations).

    Attributes:
        operations: Per-operation results.
        files_synced: Total number of files synced across all operations.
        errors: Flat list of all error strings from failed operations.
        started_at: ISO timestamp when the sync began.
        finished_at: ISO timestamp when the sync ended.
        total_duration: Wall-clock duration in seconds.
    """

    operations: list[OperationResult] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = ""
    total_duration: float = 0.0

    @property
    def success(self) -> bool:
        """Check if all operations succeeded."""
        return all(op.ok for op in self.operations)

    @property
    def files_synced(self) -> int:
        """Total number of changes/files synced across all operations."""
        return sum(len(op.changes) for op in self.operations)

    @property
    def errors(self) -> list[str]:
        """Flat list of all error strings from failed operations."""
        errs: list[str] = []
        for op in self.operations:
            errs.extend(op.errors)
        return errs

    @property
    def failed_operations(self) -> list[OperationResult]:
        """List of failed operations."""
        return [op for op in self.operations if not op.ok]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "files_synced": self.files_synced,
            "errors": self.errors,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "total_duration": self.total_duration,
            "operations": [op.to_dict() for op in self.operations],
        }


__all__ = [
    "SyncOperationStatus",
    "OperationResult",
    "SyncResult",
]
