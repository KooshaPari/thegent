"""Pure domain entities for thegent.

These are immutable or nearly-immutable data classes representing core domain concepts.
No I/O, no side effects, no external dependencies.
"""

from thegent.domain.entities.task import Task, TaskMetadata, TaskOutput, TaskStep
from thegent.domain.entities.run import RunMeta, RunState, CheckpointMeta, ContinuityPacket, MAIFArtifact

__all__ = [
    # Task entities
    "Task",
    "TaskMetadata",
    "TaskOutput",
    "TaskStep",
    # Run/execution entities
    "RunMeta",
    "RunState",
    "CheckpointMeta",
    "ContinuityPacket",
    "MAIFArtifact",
]
