"""thegent-mesh: Coordination mesh for multi-agent orchestration."""

__version__ = "0.1.0"

from .cache import MeshCache
from .coordination import Coordination
from .smart_merge import SmartMerge
from .task_queue import TaskQueue

__all__ = [
    "Coordination",
    "TaskQueue",
    "MeshCache",
    "SmartMerge",
]
