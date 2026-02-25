"""Hierarchical agent dispatch module."""

from thegent.orchestration.hierarchical_dispatcher import (
    AgentCapExceededError,
    AgentLifecycleState,
    HierarchicalAgent,
    HierarchicalAgentRegistry,
    HierarchicalDispatcher,
    HierarchicalDispatchRequest,
    HierarchicalDispatchResult,
    MAX_HIERARCHY_DEPTH,
    MaxDepthExceededError,
    SESSION_AGENT_CAP,
    SYSTEM_AGENT_CAP,
    get_global_registry,
    reset_global_registry,
)

__all__ = [
    "AgentCapExceededError",
    "AgentLifecycleState",
    "HierarchicalAgent",
    "HierarchicalAgentRegistry",
    "HierarchicalDispatcher",
    "HierarchicalDispatchRequest",
    "HierarchicalDispatchResult",
    "MAX_HIERARCHY_DEPTH",
    "MaxDepthExceededError",
    "SESSION_AGENT_CAP",
    "SYSTEM_AGENT_CAP",
    "get_global_registry",
    "reset_global_registry",
]
