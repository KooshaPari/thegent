"""
Teammate Subagent System

Delegates tasks to specialized AI agent teammates with async execution,
status tracking, and priority-based scheduling.
"""

from .registry import TeammateRegistry
from .delegate import Delegate
from .status import TaskStatus

__all__ = ["TeammateRegistry", "Delegate", "TaskStatus"]
