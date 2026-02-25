"""Hierarchical L^N Agent Dispatcher with caps and automatic pruning.

Implements hierarchical agent dispatch supporting L^1 (direct children) and
L^2 (grandchildren) depth levels. Enforces system-wide and per-session agent
caps, and automatically prunes finished/stale agents.

Key Features:
- L^N dispatch: Support for 1-2 levels of sub-agent hierarchy (max depth=2)
- System cap: Maximum 100 agents across all sessions
- Session cap: Maximum 50 agents per chat session
- Automatic pruning: Finished and stale agents are cleaned up

# @trace WL-138 (Hierarchical Agent Dispatch)
# @trace WL-139 (Agent Lifecycle Management)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from thegent.agents.capability_index import CapabilityIndex
    from thegent.compute.offload import ComputePoolManager
    from thegent.governance.hitl import HITLApprovalWorkflow
    from thegent.orchestration.sub_agent_dispatcher import SubAgentDispatcher

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------

# Maximum depth of agent hierarchy (L^1 = direct children, L^2 = grandchildren)
MAX_HIERARCHY_DEPTH: int = 2

# System-wide maximum number of active agents
SYSTEM_AGENT_CAP: int = 100

# Maximum agents per session/chat
SESSION_AGENT_CAP: int = 50

# Seconds after which an agent is considered stale
STALE_THRESHOLD_SECONDS: float = 300.0  # 5 minutes

# Seconds after which a finished agent is pruned
FINISHED_PRUNE_DELAY_SECONDS: float = 60.0  # 1 minute


class AgentLifecycleState(str, Enum):
    """Lifecycle state of a hierarchical agent."""

    PENDING = "pending"  # Waiting to be spawned
    RUNNING = "running"  # Currently executing
    FINISHED = "finished"  # Completed successfully
    FAILED = "failed"  # Failed with error
    STALE = "stale"  # No heartbeat for STALE_THRESHOLD_SECONDS
    PRUNED = "pruned"  # Cleaned up


@dataclass
class HierarchicalAgent:
    """Represents an agent in the hierarchical dispatch tree.

    Attributes:
        agent_id: Unique identifier for this agent.
        session_id: Session/chat this agent belongs to.
        parent_id: Parent agent ID (None for root agents).
        depth: Hierarchy depth (0=root, 1=L^1 child, 2=L^2 grandchild).
        state: Current lifecycle state.
        created_at: Timestamp when agent was created.
        last_heartbeat: Timestamp of last heartbeat/activity.
        task_prompt: The prompt/task for this agent.
        result: Output from agent execution (when finished).
        error: Error message (when failed).
        children: List of child agent IDs.
    """

    agent_id: str
    session_id: str
    parent_id: str | None = None
    depth: int = 0
    state: AgentLifecycleState = AgentLifecycleState.PENDING
    created_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    task_prompt: str = ""
    result: str | None = None
    error: str | None = None
    children: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "state": self.state.value,
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat,
            "task_prompt": self.task_prompt,
            "result": self.result,
            "error": self.error,
            "children": self.children,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HierarchicalAgent":
        """Deserialize from dictionary."""
        data = data.copy()
        if "state" in data and isinstance(data["state"], str):
            data["state"] = AgentLifecycleState(data["state"])
        return cls(**data)

    def update_heartbeat(self) -> None:
        """Update last heartbeat to current time."""
        self.last_heartbeat = time.time()

    def is_stale(self, threshold: float = STALE_THRESHOLD_SECONDS) -> bool:
        """Check if agent is stale (no heartbeat for threshold seconds)."""
        if self.state in (AgentLifecycleState.FINISHED, AgentLifecycleState.FAILED, AgentLifecycleState.PRUNED):
            return False
        return (time.time() - self.last_heartbeat) > threshold

    def is_prunable(self, delay: float = FINISHED_PRUNE_DELAY_SECONDS) -> bool:
        """Check if agent can be pruned."""
        if self.state == AgentLifecycleState.PRUNED:
            return False
        if self.state in (AgentLifecycleState.FINISHED, AgentLifecycleState.FAILED):
            return (time.time() - self.last_heartbeat) > delay
        if self.is_stale():
            return True
        return False


@dataclass
class SessionAgentRegistry:
    """Registry of agents for a single session.

    Tracks all agents within a session and enforces session cap.
    """

    session_id: str
    session_cap: int = SESSION_AGENT_CAP  # Configurable per-session cap
    agents: dict[str, HierarchicalAgent] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def active_count(self) -> int:
        """Count active (non-pruned) agents."""
        return sum(
            1
            for a in self.agents.values()
            if a.state not in (AgentLifecycleState.PRUNED,)
        )

    def running_count(self) -> int:
        """Count currently running agents."""
        return sum(1 for a in self.agents.values() if a.state == AgentLifecycleState.RUNNING)

    def can_spawn(self) -> bool:
        """Check if we can spawn more agents in this session."""
        return self.active_count() < self.session_cap

    def get_by_depth(self, depth: int) -> list[HierarchicalAgent]:
        """Get all agents at a specific depth."""
        return [a for a in self.agents.values() if a.depth == depth]


@dataclass
class HierarchicalDispatchRequest:
    """Request for hierarchical agent dispatch.

    Attributes:
        prompt: The task prompt.
        session_id: Session/chat ID.
        parent_agent_id: Optional parent agent (None = root dispatch).
        max_children: Maximum children to spawn (for L^1 agents).
        spawn_depth: How deep to allow spawning (1=L^1 only, 2=L^2 allowed).
        agent_hint: Capability hint for agent selection.
        context: Additional context for the agent.
    """

    prompt: str
    session_id: str
    parent_agent_id: str | None = None
    max_children: int = 7
    spawn_depth: int = 1
    agent_hint: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HierarchicalDispatchResult:
    """Result from hierarchical dispatch."""

    agent_id: str
    session_id: str
    depth: int
    state: AgentLifecycleState
    output: str | None = None
    error: str | None = None
    children_spawned: list[str] = field(default_factory=list)


class AgentCapExceededError(RuntimeError):
    """Raised when agent cap would be exceeded."""


class MaxDepthExceededError(RuntimeError):
    """Raised when max hierarchy depth would be exceeded."""


class HierarchicalAgentRegistry:
    """Global registry for hierarchical agents across all sessions.

    Enforces system-wide agent cap and provides pruning capabilities.
    """

    def __init__(self, system_cap: int = SYSTEM_AGENT_CAP, session_cap: int = SESSION_AGENT_CAP):
        self._system_cap = system_cap
        self._session_cap = session_cap
        self._sessions: dict[str, SessionAgentRegistry] = {}
        self._agents: dict[str, HierarchicalAgent] = {}
        self._lock = asyncio.Lock()

    @property
    def system_cap(self) -> int:
        return self._system_cap

    @property
    def session_cap(self) -> int:
        return self._session_cap

    def total_active_count(self) -> int:
        """Count total active agents across all sessions."""
        return sum(
            1
            for a in self._agents.values()
            if a.state not in (AgentLifecycleState.PRUNED,)
        )

    def can_spawn_system_wide(self) -> bool:
        """Check if system can accept more agents."""
        return self.total_active_count() < self._system_cap

    def can_spawn_session(self, session_id: str) -> bool:
        """Check if a session can accept more agents."""
        session = self._sessions.get(session_id)
        if session is None:
            return True
        return session.can_spawn()

    def get_or_create_session(self, session_id: str) -> SessionAgentRegistry:
        """Get or create a session registry."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionAgentRegistry(
                session_id=session_id, 
                session_cap=self._session_cap
            )
        return self._sessions[session_id]

    def register_agent(self, agent: HierarchicalAgent) -> None:
        """Register a new agent.

        Raises:
            AgentCapExceededError: If caps would be exceeded.
        """
        if not self.can_spawn_system_wide():
            raise AgentCapExceededError(
                f"System agent cap ({self._system_cap}) exceeded. "
                f"Current: {self.total_active_count()}"
            )

        session = self.get_or_create_session(agent.session_id)
        if not session.can_spawn():
            raise AgentCapExceededError(
                f"Session agent cap ({self._session_cap}) exceeded for session {agent.session_id}. "
                f"Current: {session.active_count()}"
            )

        self._agents[agent.agent_id] = agent
        session.agents[agent.agent_id] = agent

        # Register with parent if applicable
        if agent.parent_id and agent.parent_id in self._agents:
            parent = self._agents[agent.parent_id]
            if agent.agent_id not in parent.children:
                parent.children.append(agent.agent_id)

        _log.info(
            "Registered agent %s (session=%s, depth=%d, parent=%s)",
            agent.agent_id,
            agent.session_id,
            agent.depth,
            agent.parent_id,
        )

    def update_agent_state(
        self,
        agent_id: str,
        state: AgentLifecycleState,
        result: str | None = None,
        error: str | None = None,
    ) -> None:
        """Update an agent's state."""
        if agent_id not in self._agents:
            _log.warning("Attempted to update unknown agent: %s", agent_id)
            return

        agent = self._agents[agent_id]
        agent.state = state
        agent.update_heartbeat()
        if result is not None:
            agent.result = result
        if error is not None:
            agent.error = error

        _log.debug("Updated agent %s state to %s", agent_id, state.value)

    def get_agent(self, agent_id: str) -> HierarchicalAgent | None:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def get_children(self, agent_id: str) -> list[HierarchicalAgent]:
        """Get all direct children of an agent."""
        agent = self._agents.get(agent_id)
        if agent is None:
            return []
        return [self._agents[cid] for cid in agent.children if cid in self._agents]

    def get_descendants(self, agent_id: str) -> list[HierarchicalAgent]:
        """Get all descendants (children + grandchildren) of an agent."""
        descendants: list[HierarchicalAgent] = []
        for child in self.get_children(agent_id):
            descendants.append(child)
            descendants.extend(self.get_descendants(child.agent_id))
        return descendants

    def prune_agent(self, agent_id: str) -> bool:
        """Mark an agent as pruned and remove from active count.

        Returns:
            True if agent was pruned, False if not prunable.
        """
        agent = self._agents.get(agent_id)
        if agent is None or not agent.is_prunable():
            return False

        old_state = agent.state
        agent.state = AgentLifecycleState.PRUNED
        _log.info(
            "Pruned agent %s (session=%s, old_state=%s)",
            agent_id,
            agent.session_id,
            old_state.value,
        )
        return True

    def prune_finished_stale(self) -> int:
        """Prune all finished and stale agents.

        Returns:
            Number of agents pruned.
        """
        pruned = 0
        for agent_id, agent in list(self._agents.items()):
            if agent.is_prunable():
                if self.prune_agent(agent_id):
                    pruned += 1

        if pruned > 0:
            _log.info("Pruned %d finished/stale agents", pruned)

        return pruned

    def get_session_stats(self, session_id: str) -> dict[str, Any]:
        """Get statistics for a session."""
        session = self._sessions.get(session_id)
        if session is None:
            return {"session_id": session_id, "exists": False}

        return {
            "session_id": session_id,
            "exists": True,
            "active_count": session.active_count(),
            "running_count": session.running_count(),
            "total_registered": len(session.agents),
            "by_depth": {
                depth: len(session.get_by_depth(depth))
                for depth in range(MAX_HIERARCHY_DEPTH + 1)
            },
        }

    def get_system_stats(self) -> dict[str, Any]:
        """Get system-wide statistics."""
        by_state: dict[str, int] = {}
        by_depth: dict[int, int] = {}

        for agent in self._agents.values():
            state_key = agent.state.value
            by_state[state_key] = by_state.get(state_key, 0) + 1
            by_depth[agent.depth] = by_depth.get(agent.depth, 0) + 1

        return {
            "total_active": self.total_active_count(),
            "system_cap": self._system_cap,
            "session_cap": self._session_cap,
            "sessions_count": len(self._sessions),
            "by_state": by_state,
            "by_depth": by_depth,
            "can_spawn": self.can_spawn_system_wide(),
        }


# Global registry instance
_global_registry: HierarchicalAgentRegistry | None = None


def get_global_registry() -> HierarchicalAgentRegistry:
    """Get the global agent registry (singleton)."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HierarchicalAgentRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry (for testing)."""
    global _global_registry
    _global_registry = None


class HierarchicalDispatcher:
    """Dispatcher supporting L^N agent hierarchies with caps and pruning.

    Extends the basic SubAgentDispatcher to support:
    - Hierarchical agent relationships (parent-child)
    - Depth-limited spawning (max 2 levels)
    - System and session caps
    - Automatic pruning of finished/stale agents

    Usage:
        registry = get_global_registry()
        dispatcher = HierarchicalDispatcher(
            capability_index=capability_index,
            registry=registry,
        )

        # Dispatch a root agent
        result = await dispatcher.dispatch_hierarchical(
            HierarchicalDispatchRequest(
                prompt="Review the code",
                session_id="session-123",
            )
        )

        # The agent can spawn children up to depth 2
    """

    def __init__(
        self,
        capability_index: CapabilityIndex,
        registry: HierarchicalAgentRegistry | None = None,
        compute_pool: ComputePoolManager | None = None,
        hitl_workflow: HITLApprovalWorkflow | None = None,
        base_dispatcher: SubAgentDispatcher | None = None,
    ) -> None:
        self._capability_index = capability_index
        self._registry = registry or get_global_registry()
        self._compute_pool = compute_pool
        self._hitl_workflow = hitl_workflow
        self._base_dispatcher = base_dispatcher

        # Import here to avoid circular imports
        if self._base_dispatcher is None:
            from thegent.agents.sub_agent_dispatcher import SubAgentDispatcher as BaseDispatcher

            self._base_dispatcher = BaseDispatcher(
                capability_index=capability_index,
                compute_pool=compute_pool,
                hitl_workflow=hitl_workflow,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def dispatch_hierarchical(
        self,
        request: HierarchicalDispatchRequest,
    ) -> HierarchicalDispatchResult:
        """Dispatch an agent hierarchically.

        Args:
            request: The dispatch request.

        Returns:
            HierarchicalDispatchResult with agent info.

        Raises:
            AgentCapExceededError: If caps would be exceeded.
            MaxDepthExceededError: If max depth would be exceeded.
        """
        # Determine depth
        depth = 0
        parent = None
        if request.parent_agent_id:
            parent = self._registry.get_agent(request.parent_agent_id)
            if parent is None:
                raise ValueError(f"Parent agent {request.parent_agent_id} not found")
            depth = parent.depth + 1

            # Check depth limit
            if depth > MAX_HIERARCHY_DEPTH:
                raise MaxDepthExceededError(
                    f"Max hierarchy depth ({MAX_HIERARCHY_DEPTH}) exceeded. "
                    f"Requested depth: {depth}"
                )

        # Check caps
        if not self._registry.can_spawn_system_wide():
            # Try pruning first
            pruned = self._registry.prune_finished_stale()
            if not self._registry.can_spawn_system_wide():
                raise AgentCapExceededError(
                    f"System agent cap ({self._registry.system_cap}) exceeded. "
                    f"Pruned {pruned} agents but still at capacity."
                )

        if not self._registry.can_spawn_session(request.session_id):
            raise AgentCapExceededError(
                f"Session agent cap ({self._registry.session_cap}) exceeded "
                f"for session {request.session_id}"
            )

        # Create agent record
        import uuid

        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        agent = HierarchicalAgent(
            agent_id=agent_id,
            session_id=request.session_id,
            parent_id=request.parent_agent_id,
            depth=depth,
            task_prompt=request.prompt,
            metadata={
                "agent_hint": request.agent_hint,
                "max_children": request.max_children,
                "spawn_depth": request.spawn_depth,
                **request.context,
            },
        )

        # Register agent
        self._registry.register_agent(agent)

        # Update state to running
        self._registry.update_agent_state(agent_id, AgentLifecycleState.RUNNING)

        try:
            # Dispatch via base dispatcher
            from thegent.agents.sub_agent_dispatcher import SubAgentTask

            task = SubAgentTask(
                prompt=request.prompt,
                agent_hint=request.agent_hint,
                context={
                    **request.context,
                    "hierarchical_agent_id": agent_id,
                    "hierarchical_depth": depth,
                    "hierarchical_max_children": request.max_children,
                    "hierarchical_spawn_depth": request.spawn_depth,
                },
            )

            base_result = await self._base_dispatcher.dispatch(task)

            # Update agent with result
            self._registry.update_agent_state(
                agent_id,
                AgentLifecycleState.FINISHED if base_result.success else AgentLifecycleState.FAILED,
                result=base_result.output,
                error=base_result.error,
            )

            return HierarchicalDispatchResult(
                agent_id=agent_id,
                session_id=request.session_id,
                depth=depth,
                state=AgentLifecycleState.FINISHED if base_result.success else AgentLifecycleState.FAILED,
                output=base_result.output,
                error=base_result.error,
            )

        except Exception as exc:
            self._registry.update_agent_state(
                agent_id,
                AgentLifecycleState.FAILED,
                error=str(exc),
            )
            return HierarchicalDispatchResult(
                agent_id=agent_id,
                session_id=request.session_id,
                depth=depth,
                state=AgentLifecycleState.FAILED,
                error=str(exc),
            )

    async def dispatch_batch_hierarchical(
        self,
        requests: list[HierarchicalDispatchRequest],
    ) -> list[HierarchicalDispatchResult]:
        """Dispatch multiple agents in parallel.

        Respects caps by checking before each dispatch and pruning if needed.
        """
        results: list[HierarchicalDispatchResult] = []

        for request in requests:
            try:
                result = await self.dispatch_hierarchical(request)
                results.append(result)
            except AgentCapExceededError as exc:
                # Create failed result for cap-exceeded request
                results.append(
                    HierarchicalDispatchResult(
                        agent_id="",
                        session_id=request.session_id,
                        depth=0,
                        state=AgentLifecycleState.FAILED,
                        error=str(exc),
                    )
                )

        return results

    def spawn_child_request(
        self,
        parent_agent_id: str,
        child_prompt: str,
        session_id: str | None = None,
        agent_hint: str | None = None,
    ) -> HierarchicalDispatchRequest:
        """Create a request to spawn a child of an existing agent.

        This is used by agents to spawn their own children programmatically.
        """
        parent = self._registry.get_agent(parent_agent_id)
        if parent is None:
            raise ValueError(f"Parent agent {parent_agent_id} not found")

        if parent.depth >= MAX_HIERARCHY_DEPTH:
            raise MaxDepthExceededError(
                f"Parent at max depth ({parent.depth}), cannot spawn children"
            )

        return HierarchicalDispatchRequest(
            prompt=child_prompt,
            session_id=session_id or parent.session_id,
            parent_agent_id=parent_agent_id,
            max_children=parent.metadata.get("max_children", 7),
            spawn_depth=max(1, parent.metadata.get("spawn_depth", 1) - 1),
            agent_hint=agent_hint,
        )

    def can_spawn_child(self, agent_id: str) -> bool:
        """Check if an agent can spawn a child.

        Checks:
        - Agent exists and is running
        - Agent is not at max depth
        - Caps are not exceeded
        """
        agent = self._registry.get_agent(agent_id)
        if agent is None or agent.state != AgentLifecycleState.RUNNING:
            return False

        if agent.depth >= MAX_HIERARCHY_DEPTH:
            return False

        return (
            self._registry.can_spawn_system_wide()
            and self._registry.can_spawn_session(agent.session_id)
        )

    def prune_finished_stale(self) -> int:
        """Prune all finished and stale agents."""
        return self._registry.prune_finished_stale()

    def get_agent_tree(self, agent_id: str) -> dict[str, Any]:
        """Get the full tree rooted at an agent."""
        agent = self._registry.get_agent(agent_id)
        if agent is None:
            return {}

        def build_tree(a: HierarchicalAgent) -> dict[str, Any]:
            children = []
            for child in self._registry.get_children(a.agent_id):
                children.append(build_tree(child))
            return {
                "agent_id": a.agent_id,
                "depth": a.depth,
                "state": a.state.value,
                "prompt": a.task_prompt[:60] + "..." if len(a.task_prompt) > 60 else a.task_prompt,
                "children": children,
            }

        return build_tree(agent)

    def get_system_stats(self) -> dict[str, Any]:
        """Get system-wide statistics."""
        return self._registry.get_system_stats()

    def get_session_stats(self, session_id: str) -> dict[str, Any]:
        """Get session statistics."""
        return self._registry.get_session_stats(session_id)


__all__ = [
    "AgentCapExceededError",
    "AgentLifecycleState",
    "FINISHED_PRUNE_DELAY_SECONDS",
    "HierarchicalAgent",
    "HierarchicalAgentRegistry",
    "HierarchicalDispatcher",
    "HierarchicalDispatchRequest",
    "HierarchicalDispatchResult",
    "MAX_HIERARCHY_DEPTH",
    "MaxDepthExceededError",
    "SESSION_AGENT_CAP",
    "STALE_THRESHOLD_SECONDS",
    "SYSTEM_AGENT_CAP",
    "SessionAgentRegistry",
    "get_global_registry",
    "reset_global_registry",
]
