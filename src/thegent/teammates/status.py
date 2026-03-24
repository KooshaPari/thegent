"""
Task Status

Status tracking for delegated tasks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskResult:
    """Result of a delegated task."""
    id: str
    status: TaskStatus
    teammate_id: str
    task: str
    output: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Optional[dict] = None

    def duration(self) -> Optional[float]:
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def is_complete(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMEOUT
        )
