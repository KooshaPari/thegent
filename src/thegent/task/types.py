"""Pydantic models for task types.

DEPRECATED: This module re-exports from the domain layer.
New code should import from thegent.domain.entities.task instead.
"""

import warnings

# Re-export from domain layer
from thegent.domain.entities.task import (
    Complexity,
    Deliverable,
    Priority,
    SubagentType,
    Task,
    TaskMetadata,
    TaskOutput,
    TaskOutputStatus,
    TaskStep,
    TaskVisibility,
)

__all__ = [
    "SubagentType",
    "Priority",
    "TaskVisibility",
    "Complexity",
    "TaskStep",
    "TaskMetadata",
    "Task",
    "TaskOutputStatus",
    "Deliverable",
    "TaskOutput",
]

# Issue deprecation warning on import
warnings.warn(
    "Importing from thegent.task.types is deprecated. "
    "Please import from thegent.domain.entities.task instead.",
    DeprecationWarning,
    stacklevel=2,
)
