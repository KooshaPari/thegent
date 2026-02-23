"""Routing package compatibility surface."""

from .models import TaskMetadata
from .provider_types import ExecutionPath, get_execution_path

__all__ = ["ExecutionPath", "TaskMetadata", "get_execution_path"]
