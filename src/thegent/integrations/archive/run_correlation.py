"""Run correlation IDs for tracing and observability.

Provides shared run-level correlation IDs for all connector calls and events,
enabling end-to-end tracing across distributed operations.

# @trace WL-255
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CorrelationContext:
    """Context for a run with correlation tracking.

    Attributes:
        run_id: Unique identifier for the run.
        parent_id: Parent run ID if this is a child run, None otherwise.
        trace_ids: List of trace IDs associated with this run.
    """

    run_id: str
    parent_id: str | None = None
    trace_ids: list[str] = field(default_factory=list)


class RunCorrelationTracker:
    """Tracks correlation contexts for runs and their children.

    Enables tracing of run hierarchies and all trace events within each run.
    """

    def __init__(self) -> None:
        """Initialize the tracker with empty state."""
        self._contexts: dict[str, CorrelationContext] = {}

    def start_run(self, run_id: str, parent_id: str | None = None) -> CorrelationContext:
        """Start a new run with optional parent.

        Args:
            run_id: Unique identifier for this run.
            parent_id: Parent run ID if this is a child run.

        Returns:
            CorrelationContext for the new run.
        """
        context = CorrelationContext(run_id=run_id, parent_id=parent_id)
        self._contexts[run_id] = context
        logger.debug(f"Started run {run_id} with parent_id={parent_id}")
        return context

    def add_trace(self, run_id: str, trace_id: str) -> None:
        """Add a trace ID to a run's context.

        Args:
            run_id: The run to add the trace to.
            trace_id: The trace ID to add.

        Raises:
            KeyError: If run_id does not exist.
        """
        if run_id not in self._contexts:
            raise KeyError(f"Run {run_id} not found")
        self._contexts[run_id].trace_ids.append(trace_id)
        logger.debug(f"Added trace {trace_id} to run {run_id}")

    def get(self, run_id: str) -> CorrelationContext:
        """Get the correlation context for a run.

        Args:
            run_id: The run ID to retrieve.

        Returns:
            CorrelationContext for the run.

        Raises:
            KeyError: If run_id does not exist.
        """
        if run_id not in self._contexts:
            raise KeyError(f"Run {run_id} not found")
        return self._contexts[run_id]

    def children(self, parent_id: str) -> list[CorrelationContext]:
        """Get all child runs of a parent.

        Args:
            parent_id: The parent run ID.

        Returns:
            List of CorrelationContext objects for child runs.
        """
        return [ctx for ctx in self._contexts.values() if ctx.parent_id == parent_id]
