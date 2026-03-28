# hierarchical_dispatcher API Reference

> **Source**: `src/thegent/orchestration/hierarchical_dispatcher.py`

Hierarchical L^N Agent Dispatcher with caps and automatic pruning.

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

---

## AgentCapExceededError

Raised when agent cap would be exceeded.

**Inherits from**: `RuntimeError`

---

## AgentLifecycleState

Lifecycle state of a hierarchical agent.

**Inherits from**: `str, Enum`

---

## HierarchicalAgent

Represents an agent in the hierarchical dispatch tree.

### Methods

#### HierarchicalAgent.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Deserialize from dictionary.

---

#### HierarchicalAgent.is_prunable

```python
is_prunable(self: Any, delay: float)
```

Check if agent can be pruned.

---

#### HierarchicalAgent.is_stale

```python
is_stale(self: Any, threshold: float)
```

Check if agent is stale (no heartbeat for threshold seconds).

---

#### HierarchicalAgent.to_dict

```python
to_dict(self: Any)
```

Serialize to dictionary.

---

#### HierarchicalAgent.update_heartbeat

```python
update_heartbeat(self: Any)
```

Update last heartbeat to current time.

---

---

## HierarchicalAgentRegistry

Global registry for hierarchical agents across all sessions.

Enforces system-wide agent cap and provides pruning capabilities.

### Methods

#### HierarchicalAgentRegistry.__init__

```python
__init__(self: Any, system_cap: int, session_cap: int)
```

---

#### HierarchicalAgentRegistry.can_spawn_session

```python
can_spawn_session(self: Any, session_id: str)
```

Check if a session can accept more agents.

---

#### HierarchicalAgentRegistry.can_spawn_system_wide

```python
can_spawn_system_wide(self: Any)
```

Check if system can accept more agents.

---

#### HierarchicalAgentRegistry.get_agent

```python
get_agent(self: Any, agent_id: str)
```

Get an agent by ID.

---

#### HierarchicalAgentRegistry.get_children

```python
get_children(self: Any, agent_id: str)
```

Get all direct children of an agent.

---

#### HierarchicalAgentRegistry.get_descendants

```python
get_descendants(self: Any, agent_id: str)
```

Get all descendants (children + grandchildren) of an agent.

---

#### HierarchicalAgentRegistry.get_or_create_session

```python
get_or_create_session(self: Any, session_id: str)
```

Get or create a session registry.

---

#### HierarchicalAgentRegistry.get_session_stats

```python
get_session_stats(self: Any, session_id: str)
```

Get statistics for a session.

---

#### HierarchicalAgentRegistry.get_system_stats

```python
get_system_stats(self: Any)
```

Get system-wide statistics.

---

#### HierarchicalAgentRegistry.prune_agent

```python
prune_agent(self: Any, agent_id: str)
```

Mark an agent as pruned and remove from active count.

**Returns**: True if agent was pruned, False if not prunable.

---

#### HierarchicalAgentRegistry.prune_finished_stale

```python
prune_finished_stale(self: Any)
```

Prune all finished and stale agents.

**Returns**: Number of agents pruned.

---

#### HierarchicalAgentRegistry.register_agent

```python
register_agent(self: Any, agent: HierarchicalAgent)
```

Register a new agent.

---

#### HierarchicalAgentRegistry.session_cap

```python
session_cap(self: Any)
```

---

#### HierarchicalAgentRegistry.system_cap

```python
system_cap(self: Any)
```

---

#### HierarchicalAgentRegistry.total_active_count

```python
total_active_count(self: Any)
```

Count total active agents across all sessions.

---

#### HierarchicalAgentRegistry.update_agent_state

```python
update_agent_state(self: Any, agent_id: str, state: AgentLifecycleState, result: Any, error: Any)
```

Update an agent's state.

---

---

## HierarchicalDispatchRequest

Request for hierarchical agent dispatch.

---

## HierarchicalDispatchResult

Result from hierarchical dispatch.

---

## HierarchicalDispatcher

Dispatcher supporting L^N agent hierarchies with caps and pruning.

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

### Methods

#### HierarchicalDispatcher.__init__

```python
__init__(self: Any, capability_index: CapabilityIndex, registry: Any, compute_pool: Any, hitl_workflow: Any, base_dispatcher: Any)
```

---

#### HierarchicalDispatcher.can_spawn_child

```python
can_spawn_child(self: Any, agent_id: str)
```

Check if an agent can spawn a child.

Checks:
- Agent exists and is running
- Agent is not at max depth
- Caps are not exceeded

---

#### HierarchicalDispatcher.get_agent_tree

```python
get_agent_tree(self: Any, agent_id: str)
```

Get the full tree rooted at an agent.

---

#### HierarchicalDispatcher.get_session_stats

```python
get_session_stats(self: Any, session_id: str)
```

Get session statistics.

---

#### HierarchicalDispatcher.get_system_stats

```python
get_system_stats(self: Any)
```

Get system-wide statistics.

---

#### HierarchicalDispatcher.prune_finished_stale

```python
prune_finished_stale(self: Any)
```

Prune all finished and stale agents.

---

#### HierarchicalDispatcher.spawn_child_request

```python
spawn_child_request(self: Any, parent_agent_id: str, child_prompt: str, session_id: Any, agent_hint: Any)
```

Create a request to spawn a child of an existing agent.

This is used by agents to spawn their own children programmatically.

---

---

## MaxDepthExceededError

Raised when max hierarchy depth would be exceeded.

**Inherits from**: `RuntimeError`

---

## SessionAgentRegistry

Registry of agents for a single session.

Tracks all agents within a session and enforces session cap.

### Methods

#### SessionAgentRegistry.active_count

```python
active_count(self: Any)
```

Count active (non-pruned) agents.

---

#### SessionAgentRegistry.can_spawn

```python
can_spawn(self: Any)
```

Check if we can spawn more agents in this session.

---

#### SessionAgentRegistry.get_by_depth

```python
get_by_depth(self: Any, depth: int)
```

Get all agents at a specific depth.

---

#### SessionAgentRegistry.running_count

```python
running_count(self: Any)
```

Count currently running agents.

---

---

## active_count

```python
active_count(self: Any)
```

Count active (non-pruned) agents.

---

## build_tree

```python
build_tree(a: HierarchicalAgent) -> dict[(str, Any)]
```

---

## can_spawn

```python
can_spawn(self: Any)
```

Check if we can spawn more agents in this session.

---

## can_spawn_child

```python
can_spawn_child(self: Any, agent_id: str)
```

Check if an agent can spawn a child.

Checks:
- Agent exists and is running
- Agent is not at max depth
- Caps are not exceeded

---

## can_spawn_session

```python
can_spawn_session(self: Any, session_id: str)
```

Check if a session can accept more agents.

---

## can_spawn_system_wide

```python
can_spawn_system_wide(self: Any)
```

Check if system can accept more agents.

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Deserialize from dictionary.

---

## get_agent

```python
get_agent(self: Any, agent_id: str)
```

Get an agent by ID.

---

## get_agent_tree

```python
get_agent_tree(self: Any, agent_id: str)
```

Get the full tree rooted at an agent.

---

## get_by_depth

```python
get_by_depth(self: Any, depth: int)
```

Get all agents at a specific depth.

---

## get_children

```python
get_children(self: Any, agent_id: str)
```

Get all direct children of an agent.

---

## get_descendants

```python
get_descendants(self: Any, agent_id: str)
```

Get all descendants (children + grandchildren) of an agent.

---

## get_global_registry

Get the global agent registry (singleton).

---

## get_or_create_session

```python
get_or_create_session(self: Any, session_id: str)
```

Get or create a session registry.

---

## get_session_stats

```python
get_session_stats(self: Any, session_id: str)
```

Get session statistics.

---

## get_system_stats

```python
get_system_stats(self: Any)
```

Get system-wide statistics.

---

## is_prunable

```python
is_prunable(self: Any, delay: float)
```

Check if agent can be pruned.

---

## is_stale

```python
is_stale(self: Any, threshold: float)
```

Check if agent is stale (no heartbeat for threshold seconds).

---

## prune_agent

```python
prune_agent(self: Any, agent_id: str)
```

Mark an agent as pruned and remove from active count.

**Returns**: True if agent was pruned, False if not prunable.

---

## prune_finished_stale

```python
prune_finished_stale(self: Any)
```

Prune all finished and stale agents.

---

## register_agent

```python
register_agent(self: Any, agent: HierarchicalAgent)
```

Register a new agent.

**Raises**:

- `AgentCapExceededError`: If caps would be exceeded.

---

## reset_global_registry

Reset the global registry (for testing).

---

## running_count

```python
running_count(self: Any)
```

Count currently running agents.

---

## session_cap

```python
session_cap(self: Any) -> int
```

---

## spawn_child_request

```python
spawn_child_request(self: Any, parent_agent_id: str, child_prompt: str, session_id: Any, agent_hint: Any)
```

Create a request to spawn a child of an existing agent.

This is used by agents to spawn their own children programmatically.

---

## system_cap

```python
system_cap(self: Any) -> int
```

---

## to_dict

```python
to_dict(self: Any)
```

Serialize to dictionary.

---

## total_active_count

```python
total_active_count(self: Any)
```

Count total active agents across all sessions.

---

## update_agent_state

```python
update_agent_state(self: Any, agent_id: str, state: AgentLifecycleState, result: Any, error: Any)
```

Update an agent's state.

---

## update_heartbeat

```python
update_heartbeat(self: Any)
```

Update last heartbeat to current time.

---

