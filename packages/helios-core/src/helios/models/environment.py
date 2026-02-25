"""Environment-related models"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EnvironmentType(Enum):
    """Types of execution environments"""
    DOCKER = "docker"
    DAYTONA = "daytona"
    LOCAL = "local"
    MODAL = "modal"


@dataclass
class EnvironmentConfig:
    """Configuration for an environment"""
    type: EnvironmentType = EnvironmentType.DOCKER
    image: str | None = None
    cpus: int = 1
    memory_mb: int = 2048
    timeout_sec: int = 600
    gpu: bool = False
    allow_internet: bool = True


@dataclass
class ExecResult:
    """Result from executing a command in an environment"""
    stdout: str
    stderr: str
    return_code: int
