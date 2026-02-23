"""Doctor models and types."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CheckStatus(Enum):
    """Status of a doctor check."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a single doctor check."""
    check_id: str
    status: CheckStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    fix_available: bool = False


@dataclass
class ProcessInfo:
    """Information about a process."""
    pid: int
    name: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    status: str = ""
    command: str = ""


@dataclass
class FixResult:
    """Result of applying a fix."""
    check_id: str
    success: bool
    message: str
    changes: dict[str, Any] = field(default_factory=dict)
