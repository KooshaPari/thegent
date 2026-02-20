"""WP-21001: Fork Explosion Guard.
Prevents agent recursion depth and fan-out (parallel sub-tasks) from exceeding safe limits.
"""

import logging
from dataclasses import dataclass

_log = logging.getLogger(__name__)


@dataclass
class ForkContext:
    """Tracks fork state for a specific run and its children."""

    run_id: str
    parent_id: str | None = None
    recursion_depth: int = 0
    child_count: int = 0
    max_depth: int = 5
    max_fanout: int = 10


class ForkExplosionGuard:
    """Monitors and limits the creation of sub-tasks to prevent cascading execution."""

    def __init__(self) -> None:
        # In a real system, this would be persisted to a shared state (e.g. SQLite/Redis)
        self.fork_registry: dict[str, ForkContext] = {}

    def register_run(self, run_id: str, parent_id: str | None = None):
        """Register a new run, inheriting depth from parent."""
        depth = 0
        if parent_id and parent_id in self.fork_registry:
            parent = self.fork_registry[parent_id]
            depth = parent.recursion_depth + 1
            parent.child_count += 1

            # 1. Check Parent Fan-out
            if parent.child_count > parent.max_fanout:
                _log.error("Fork explosion detected: Run %s exceeded max fan-out (%d)", parent_id, parent.max_fanout)
                raise RuntimeError(f"Fork explosion: Parent {parent_id} fan-out limit reached")

        # 2. Check Recursion Depth
        if depth > 5:  # Default max depth
            _log.error("Fork explosion detected: Run %s exceeded max recursion depth (%d)", run_id, depth)
            raise RuntimeError("Fork explosion: Recursion depth limit reached (%d)" % depth)

        ctx = ForkContext(run_id=run_id, parent_id=parent_id, recursion_depth=depth)
        self.fork_registry[run_id] = ctx
        _log.info("Registered run %s (Depth: %d, Parent: %s)", run_id, depth, parent_id)

    def get_stats(self, run_id: str) -> ForkContext | None:
        """Return stats for a specific run."""
        return self.fork_registry.get(run_id)
