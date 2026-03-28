# sub_agent_dispatcher API Reference

> **Source**: `src/thegent/orchestration/sub_agent_dispatcher.py`

SubAgentDispatcher: CapabilityIndex-backed dispatch with budget enforcement.

Provides CapabilityIndex for mapping capability strings to agent names, and
SubAgentDispatcher for dispatching SubAgentRequest objects to sub-agents with
optional token budget enforcement and structured event logging.

Events are published to a SubAgentEventQueue so that real-time consumers
(MCP tool, UnifiedWorkerDaemon) can observe dispatch lifecycle transitions.

WL-089: When a ComputePoolManager is provided via the compute_pool parameter,
SubAgentDispatcher will delegate requests whose agent_type is NOT a recognized
CLI harness (e.g. "codex", "claude", "gemini") to the remote compute pool via
RemoteDispatchBackend. CLI harnesses are dispatched locally as before.

# @trace FR-ORC-082
# @trace WL-085
# @trace WL-089

---

## CapabilityIndex

Maps capability strings to agent names.

Usage::

    index = CapabilityIndex()
    index.register("code_review", "reviewer-agent")
    agent_name = index.lookup("code_review")

# @trace FR-ORC-082

### Methods

#### CapabilityIndex.__init__

```python
__init__(self: Any)
```

---

#### CapabilityIndex.lookup

```python
lookup(self: Any, capability: str)
```

Return the agent_name registered for capability.

**Parameters**:

- `capability`: Capability identifier string to look up.

**Returns**: The agent_name registered for the capability.

---

#### CapabilityIndex.register

```python
register(self: Any, capability: str, agent_name: str)
```

Register an agent_name as the handler for capability.

**Parameters**:

- `capability`: Capability identifier string.
- `agent_name`: Name of the agent that handles the capability.

---

---

## SubAgentDispatcher

Dispatches SubAgentRequest objects with optional budget enforcement.

This is a synchronous dispatcher stub. The actual agent execution logic
is out of scope; dispatch() returns a COMPLETED SubAgentResult modelling
the correct interface. Budget checking, event emission, and concurrent
dispatch logic are fully implemented.

Events are published to the provided *event_queue* (or the process-global
queue when none is supplied) after each dispatch lifecycle transition.

WL-089: When *compute_pool* is provided, requests whose agent_type is NOT
a recognized CLI harness are delegated to the remote Tailscale compute
pool via a :class:`~thegent.orchestration.remote_dispatch.RemoteDispatchBackend`
constructed automatically from *compute_pool*. CLI harness requests are
dispatched locally (or via *remote_backend* if set explicitly).

### Methods

#### SubAgentDispatcher.__init__

```python
__init__(self: Any, capability_index: CapabilityIndex, budget_tracker: Any, event_queue: Any, remote_backend: Any, compute_pool: Any)
```

---

#### SubAgentDispatcher.dispatch

```python
dispatch(self: Any, request: SubAgentRequest)
```

Dispatch a single SubAgentRequest and return a SubAgentResult.

Emits DISPATCH_STARTED and DISPATCH_COMPLETED SubAgentEvents to the
event queue. Checks the budget_tracker before dispatching if one was
provided.

**Parameters**:

- `request`: The request to dispatch.

**Returns**: SubAgentResult with status COMPLETED.

---

#### SubAgentDispatcher.dispatch_concurrent

```python
dispatch_concurrent(self: Any, requests: list[SubAgentRequest])
```

Dispatch multiple requests concurrently using asyncio.gather.

Uses asyncio.run() to execute all requests concurrently. Results are
returned in the same order as the input requests.

**Parameters**:

- `requests`: List of SubAgentRequest objects to dispatch.

**Returns**: List of SubAgentResult objects in the same order as requests.

---

---

## dispatch

```python
dispatch(self: Any, request: SubAgentRequest)
```

Dispatch a single SubAgentRequest and return a SubAgentResult.

Emits DISPATCH_STARTED and DISPATCH_COMPLETED SubAgentEvents to the
event queue. Checks the budget_tracker before dispatching if one was
provided.

**Parameters**:

- `request`: The request to dispatch.

**Returns**: SubAgentResult with status COMPLETED.

**Raises**:

- `BudgetExceededError`: If budget_tracker is set and the request
exceeds its node budget.

---

## dispatch_concurrent

```python
dispatch_concurrent(self: Any, requests: list[SubAgentRequest])
```

Dispatch multiple requests concurrently using asyncio.gather.

Uses asyncio.run() to execute all requests concurrently. Results are
returned in the same order as the input requests.

**Parameters**:

- `requests`: List of SubAgentRequest objects to dispatch.

**Returns**: List of SubAgentResult objects in the same order as requests.

---

## is_cli_harness

```python
is_cli_harness(agent_type: str)
```

Return True when agent_type names a recognized CLI agent harness.

CLI harnesses (e.g. "codex", "claude", "gemini") are dispatched locally.
Any other agent_type is treated as a compute node task and, when a
compute_pool is configured, delegated to ComputePoolManager.submit().

**Parameters**:

- `agent_type`: The agent_type field from a SubAgentRequest.

**Returns**: True if agent_type is a known CLI harness name.

---

## lookup

```python
lookup(self: Any, capability: str)
```

Return the agent_name registered for capability.

**Parameters**:

- `capability`: Capability identifier string to look up.

**Returns**: The agent_name registered for the capability.

**Raises**:

- `KeyError`: If no agent is registered for the capability.

---

## register

```python
register(self: Any, capability: str, agent_name: str)
```

Register an agent_name as the handler for capability.

**Parameters**:

- `capability`: Capability identifier string.
- `agent_name`: Name of the agent that handles the capability.

---

