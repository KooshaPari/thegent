"""Task routing and categorization for thegent.

Implements Pareto frontier routing based on Terminal Bench 2.0 benchmarks.
Routes tasks to optimal models based on complexity, cost constraints, and quality requirements.

Key components:
- TaskRouter: Main routing engine with constraint validation
- TaskClassifier: Categorizes tasks (FAST/NORMAL/COMPLEX/HIGH_COMPLEX)
- ConstraintValidator: Validates hard constraints (quality, cost, speed)
- TaskCategory: Enum for task complexity levels
- TaskMetadata: Routing decision metadata
"""

from thegent.routing.models import RoutingConstraint, TaskCategory, TaskMetadata
from thegent.routing.task_router import ConstraintValidator, TaskClassifier, TaskRouter

__all__ = [
    "ConstraintValidator",
    "RoutingConstraint",
    "TaskCategory",
    "TaskClassifier",
    "TaskMetadata",
    "TaskRouter",
]
