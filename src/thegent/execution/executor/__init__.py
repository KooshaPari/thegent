"""Execution engine for task orchestration.

Core executor providing dependency-injected orchestration
with no direct CLI imports. Implements pure execution logic
with abstract dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol
from pathlib import Path


class LoggerInterface(Protocol):
    """Abstract logger interface for execution events."""

    def info(self, message: str, **kwargs: Any) -> None:
        """Log informational message."""
        ...

    def error(self, message: str, exc: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log error message."""
        ...

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...


class EventBusInterface(Protocol):
    """Abstract event bus for execution events."""

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit an execution event."""
        ...

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to event type."""
        ...


@dataclass
class ExecutionResult:
    """Result of task execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Executor:
    """Dependency-injected task executor.

    This executor accepts all dependencies via constructor,
    ensuring zero imports from CLI layer. It can be used
    via CLI, MCP, or other adapters through dependency injection.

    No circular imports: execution -> core only.
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        event_bus: Optional[EventBusInterface] = None,
        agent_factory: Optional[Callable] = None,
        model_factory: Optional[Callable] = None,
    ):
        """Initialize executor with injected dependencies.

        Args:
            logger: Optional logger interface (uses no-op if None)
            event_bus: Optional event bus (uses no-op if None)
            agent_factory: Optional factory for creating agents
            model_factory: Optional factory for creating models
        """
        self.logger = logger or self._noop_logger()
        self.event_bus = event_bus or self._noop_event_bus()
        self.agent_factory = agent_factory
        self.model_factory = model_factory

    def run(
        self,
        task_id: str,
        task_spec: dict[str, Any],
        workspace_path: Optional[Path] = None,
    ) -> ExecutionResult:
        """Execute a task.

        Pure orchestration logic with injected dependencies.
        No direct CLI references.

        Args:
            task_id: Unique task identifier
            task_spec: Task specification (contracts from core)
            workspace_path: Optional workspace path

        Returns:
            ExecutionResult with success status and output
        """
        try:
            self.logger.info(f"Starting execution for task {task_id}")
            self.event_bus.emit("execution:started", {"task_id": task_id})

            # Execute task using injected agents/models
            result = self._execute_task(task_id, task_spec, workspace_path)

            self.event_bus.emit("execution:completed", {
                "task_id": task_id,
                "success": result.success,
            })
            self.logger.info(f"Task {task_id} completed: {result.success}")

            return result

        except Exception as e:
            self.logger.error(f"Execution failed for task {task_id}", exc=e)
            self.event_bus.emit("execution:failed", {
                "task_id": task_id,
                "error": str(e),
            })
            return ExecutionResult(
                success=False,
                error=str(e),
            )

    def _execute_task(
        self,
        task_id: str,
        task_spec: dict[str, Any],
        workspace_path: Optional[Path],
    ) -> ExecutionResult:
        """Internal task execution logic."""
        # Placeholder for actual execution logic
        # This will be enhanced in Phase 3-4 decomposition
        return ExecutionResult(
            success=True,
            output={"task_id": task_id, "status": "executed"},
        )

    @staticmethod
    def _noop_logger() -> LoggerInterface:
        """Create a no-op logger for testing."""
        class NoOpLogger:
            def info(self, message: str, **kwargs: Any) -> None: pass
            def error(self, message: str, exc: Optional[Exception] = None, **kwargs: Any) -> None: pass
            def debug(self, message: str, **kwargs: Any) -> None: pass
        return NoOpLogger()

    @staticmethod
    def _noop_event_bus() -> EventBusInterface:
        """Create a no-op event bus for testing."""
        class NoOpEventBus:
            def emit(self, event_type: str, data: dict[str, Any]) -> None: pass
            def subscribe(self, event_type: str, handler: Callable) -> None: pass
        return NoOpEventBus()


__all__ = [
    "Executor",
    "ExecutionResult",
    "LoggerInterface",
    "EventBusInterface",
]
