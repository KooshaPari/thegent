"""Execution framework for thegent.

Provides core abstractions for run tracking, metadata management,
distributed execution coordination, and dependency-injected orchestration.

Phase 2 Structure (with NO CLI imports):
- executor/: Core task executor with dependency injection
- planner/: Task decomposition logic
- router/: Request routing to agents/models
- ports/: Abstract interfaces
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Protocol
from pathlib import Path


class ExecutionStatus(Enum):
    """Status of an execution run."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class RunMeta:
    """Metadata for a single execution run.
    
    Tracks run identification, timing, status, and agent assignment.
    """
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    task_id: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "status": self.status.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class RunRegistry(Protocol):
    """Protocol for run registration and tracking.
    
    Implementations provide persistence and query capabilities
    for execution runs across the system.
    """
    
    def register(self, meta: RunMeta) -> None:
        """Register a new run in the registry."""
        ...
    
    def update(self, run_id: str, **kwargs) -> None:
        """Update run metadata."""
        ...
    
    def get(self, run_id: str) -> Optional[RunMeta]:
        """Retrieve run metadata by ID."""
        ...
    
    def list_by_agent(self, agent_id: str) -> list[RunMeta]:
        """List all runs for a specific agent."""
        ...
    
    def list_by_status(self, status: ExecutionStatus) -> list[RunMeta]:
        """List all runs with a specific status."""
        ...


@dataclass
class ExecutionContext:
    """Context for executing a task.
    
    Provides runtime information, configuration, and state
    for task execution.
    """
    run_id: str
    agent_id: str
    task_id: str
    workspace_path: Path
    config: dict[str, Any] = field(default_factory=dict)
    env_vars: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict)
    parent_context: Optional["ExecutionContext"] = None
    
    def child_context(self, task_id: str) -> "ExecutionContext":
        """Create a child execution context for sub-tasks."""
        return ExecutionContext(
            run_id=self.run_id,
            agent_id=self.agent_id,
            task_id=task_id,
            workspace_path=self.workspace_path,
            config=self.config.copy(),
            env_vars=self.env_vars.copy(),
            parent_context=self,
        )


@dataclass
class ExecutionResult:
    """Result of task execution.
    
    Captures success/failure status, outputs, and metadata.
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    
    @classmethod
    def success_result(cls, output: Any, **metadata) -> "ExecutionResult":
        """Create a successful result."""
        return cls(success=True, output=output, metadata=metadata)
    
    @classmethod
    def failure_result(cls, error: str, **metadata) -> "ExecutionResult":
        """Create a failure result."""
        return cls(success=False, error=error, metadata=metadata)


class ExecutionEngine(Protocol):
    """Protocol for task execution engines.
    
    Implementations provide the actual execution logic for
    running tasks within an execution context.
    """
    
    def execute(self, context: ExecutionContext, task: Any) -> ExecutionResult:
        """Execute a task within the given context."""
        ...
    
    def can_execute(self, task: Any) -> bool:
        """Check if this engine can execute the given task."""
        ...


@dataclass
class ExecutionSession:
    """Session managing multiple related executions.
    
    Groups related runs together for batch processing,
    dependency management, and coordinated execution.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    runs: list[RunMeta] = field(default_factory=list)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_run(self, run: RunMeta, depends_on: Optional[list[str]] = None) -> None:
        """Add a run to the session with optional dependencies."""
        self.runs.append(run)
        if depends_on:
            self.dependencies[run.run_id] = depends_on
    
    def get_ready_runs(self) -> list[RunMeta]:
        """Get runs that have all dependencies satisfied."""
        completed = {r.run_id for r in self.runs if r.status == ExecutionStatus.COMPLETED}
        ready = []
        for run in self.runs:
            if run.status != ExecutionStatus.PENDING:
                continue
            deps = self.dependencies.get(run.run_id, [])
            if all(d in completed for d in deps):
                ready.append(run)
        return ready


class DLQManager:
    """Dead Letter Queue manager for failed executions.
    
    Provides retry logic, failure tracking, and dead letter
    queue management for resilient execution.
    """
    
    def __init__(self, max_retries: int = 3, dlq_path: Optional[Path] = None):
        self.max_retries = max_retries
        self.dlq_path = dlq_path or Path(".thegent/dlq")
        self.dlq_path.mkdir(parents=True, exist_ok=True)
        self._failed: dict[str, list[RunMeta]] = {}
    
    def record_failure(self, run: RunMeta, error: str) -> bool:
        """Record a failure and return True if should retry.
        
        Returns False if max retries exceeded (sent to DLQ).
        """
        if run.run_id not in self._failed:
            self._failed[run.run_id] = []
        self._failed[run.run_id].append(run)
        
        if len(self._failed[run.run_id]) >= self.max_retries:
            self._send_to_dlq(run, error)
            return False
        return True
    
    def _send_to_dlq(self, run: RunMeta, error: str) -> None:
        """Send a failed run to the dead letter queue."""
        import json
        dlq_file = self.dlq_path / f"{run.run_id}.json"
        dlq_file.write_text(json.dumps({
            "run": run.to_dict(),
            "error": error,
            "attempts": len(self._failed.get(run.run_id, [])),
            "timestamp": datetime.utcnow().isoformat(),
        }))
    
    def get_dlq_items(self) -> list[dict[str, Any]]:
        """Get all items in the dead letter queue."""
        import json
        items = []
        for dlq_file in self.dlq_path.glob("*.json"):
            items.append(json.loads(dlq_file.read_text()))
        return items


class PolicyEngine:
    """Policy evaluation engine for execution governance.
    
    Evaluates policies against execution context and metadata
to enforce governance rules.
    """
    
    def __init__(self):
        self._policies: list[callable] = []
    
    def register_policy(self, policy: callable) -> None:
        """Register a policy function."""
        self._policies.append(policy)
    
    def evaluate(self, context: ExecutionContext, action: str) -> tuple[bool, Optional[str]]:
        """Evaluate all policies against an action.
        
        Returns (allowed, reason) tuple.
        """
        for policy in self._policies:
            allowed, reason = policy(context, action)
            if not allowed:
                return False, reason
        return True, None


class ConcurrencyController:
    """Controls concurrent execution limits.
    
    Manages resource limits and concurrency across agents
    and execution contexts.
    """
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._active: set[str] = set()
        self._semaphore: Optional[Any] = None
    
    async def acquire(self, run_id: str) -> bool:
        """Acquire a concurrency slot."""
        if len(self._active) >= self.max_concurrent:
            return False
        self._active.add(run_id)
        return True
    
    def release(self, run_id: str) -> None:
        """Release a concurrency slot."""
        self._active.discard(run_id)
    
    def get_active_count(self) -> int:
        """Get number of active executions."""
        return len(self._active)


class TrustBoundaryValidator:
    """Validates trust boundaries for execution security.
    
    Ensures executions stay within defined trust boundaries
    and security policies.
    """
    
    def __init__(self, boundaries: Optional[list[str]] = None):
        self.boundaries = boundaries or []
    
    def validate(self, context: ExecutionContext, target: str) -> tuple[bool, Optional[str]]:
        """Validate that a target is within trust boundaries.
        
        Returns (valid, reason) tuple.
        """
        # TODO: Implement actual boundary checking
        return True, None


class EscalationQueue:
    """Queue for escalating execution issues.
    
    Manages escalation of failed or stuck executions
    to higher-level handlers.
    """
    
    def __init__(self):
        self._escalations: list[dict[str, Any]] = []
    
    def escalate(self, run: RunMeta, reason: str, level: int = 1) -> None:
        """Escalate a run with given reason and level."""
        self._escalations.append({
            "run": run.to_dict(),
            "reason": reason,
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_pending(self, min_level: int = 1) -> list[dict[str, Any]]:
        """Get pending escalations at or above a level."""
        return [e for e in self._escalations if e["level"] >= min_level]


class HandoffManager:
    """Manages handoffs between agents during execution.
    
    Coordinates transfer of execution state and context
    between different agents.
    """
    
    def __init__(self):
        self._handoffs: dict[str, dict[str, Any]] = {}
    
    def initiate_handoff(
        self,
        from_agent: str,
        to_agent: str,
        context: ExecutionContext,
        state: dict[str, Any],
    ) -> str:
        """Initiate a handoff between agents."""
        handoff_id = str(uuid.uuid4())
        self._handoffs[handoff_id] = {
            "from": from_agent,
            "to": to_agent,
            "context": context,
            "state": state,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        return handoff_id
    
    def complete_handoff(self, handoff_id: str) -> Optional[dict[str, Any]]:
        """Complete a pending handoff."""
        handoff = self._handoffs.get(handoff_id)
        if handoff and handoff["status"] == "pending":
            handoff["status"] = "completed"
            handoff["completed_at"] = datetime.utcnow().isoformat()
            return handoff
        return None


class Auditor:
    """Audit logging for execution tracking.
    
    Provides comprehensive audit logging for compliance
    and debugging purposes.
    """
    
    def __init__(self, audit_log_path: Optional[Path] = None):
        self.audit_log_path = audit_log_path or Path(".thegent/audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, event: str, context: ExecutionContext, details: dict[str, Any]) -> None:
        """Log an audit event."""
        import json
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "run_id": context.run_id,
            "agent_id": context.agent_id,
            "task_id": context.task_id,
            "details": details,
        }
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")


class AgentSource(Enum):
    """Source of an agent for execution."""
    LOCAL = "local"
    REMOTE = "remote"
    REGISTRY = "registry"
    BUILTIN = "builtin"


class InteractivityMode(Enum):
    """Level of interactivity for execution."""
    NONE = "none"
    CONFIRM = "confirm"
    FULL = "full"


# Simple implementations for common use cases
class InMemoryRunRegistry:
    """In-memory implementation of RunRegistry for testing/single-node use."""
    
    def __init__(self):
        self._runs: dict[str, RunMeta] = {}
    
    def register(self, meta: RunMeta) -> None:
        self._runs[meta.run_id] = meta
    
    def update(self, run_id: str, **kwargs) -> None:
        if run_id in self._runs:
            for key, value in kwargs.items():
                setattr(self._runs[run_id], key, value)
    
    def get(self, run_id: str) -> Optional[RunMeta]:
        return self._runs.get(run_id)
    
    def list_by_agent(self, agent_id: str) -> list[RunMeta]:
        return [r for r in self._runs.values() if r.agent_id == agent_id]
    
    def list_by_status(self, status: ExecutionStatus) -> list[RunMeta]:
        return [r for r in self._runs.values() if r.status == status]


# Type aliases for backward compatibility
LoadClassifier = Any  # TODO: Implement proper classifier
ProviderScorer = Any  # TODO: Implement proper scorer


# Phase 2: New dependency-injected execution layer (NO CLI imports)
# Import and re-export new components
from .executor import Executor, ExecutionResult, LoggerInterface, EventBusInterface  # noqa: E402, F401
from .planner import Planner, TaskSpec  # noqa: E402, F401
from .router import Router  # noqa: E402, F401

# Phase 3: ExecutionPort adapter for agents (breaks CLI<->Agents cycle)
from .execution_port_adapter import ExecutionPortAdapter, get_execution_port, set_execution_port  # noqa: E402, F401

__all__ = [
    "Executor",
    "ExecutionResult",
    "LoggerInterface",
    "EventBusInterface",
    "Planner",
    "TaskSpec",
    "Router",
    "ExecutionPortAdapter",
    "get_execution_port",
    "set_execution_port",
    "ExecutionStatus",
    "RunMeta",
    "RunRegistry",
    "AgentSource",
    "InteractivityMode",
    "InMemoryRunRegistry",
]
