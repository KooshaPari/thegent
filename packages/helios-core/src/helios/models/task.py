"""Task-related models"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskMetadata:
    """Metadata about a task"""
    id: str
    dataset: str
    instance_id: str
    difficulty: str = "medium"  # easy, medium, hard
    tags: list[str] = field(default_factory=list)
    estimated_time_sec: int | None = None


@dataclass
class TaskResources:
    """Resource requirements for a task"""
    cpus: int = 1
    memory_mb: int = 2048
    timeout_sec: int = 600
    gpu: bool = False


@dataclass
class TaskInput:
    """Input for a task"""
    instruction: str
    files: dict[str, str] = field(default_factory=dict)  # path -> content
    environment: dict[str, Any] = field(default_factory=dict)  # env vars
    resources: TaskResources = field(default_factory=TaskResources)


@dataclass
class TaskOutput:
    """Output from a task execution"""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    files: dict[str, str] = field(default_factory=dict)
    trajectory: list[dict[str, Any]] = field(default_factory=list)
