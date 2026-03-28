# hitl API Reference

> **Source**: `src/thegent/governance/hitl.py`

Human-in-the-loop (HITL) coordination and approval workflows (WP-3001, WP-3008).

Traces to: G-GP-05, FR-GOV-HITL (WL-019)

---

## GovernanceEventLog

Writes and reads governance events from governance_events.jsonl (WL-019-A).

### Methods

#### GovernanceEventLog.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### GovernanceEventLog.emit

```python
emit(self: Any, event: dict[(str, Any)])
```

Append a governance event to the log.

---

#### GovernanceEventLog.list_pending_approvals

```python
list_pending_approvals(self: Any, run_id: Any)
```

Return all await_approval events that are not yet resolved.

---

#### GovernanceEventLog.update_status

```python
update_status(self: Any, run_id: str, new_status: str, reason: Any)
```

Update the status of a pending await_approval event. Returns True on success.

---

---

## HITLApprovalWorkflow

Implements the approve/reject workflow for HITL-blocked runs (WL-019-B).

Reads pending approvals from governance_events.jsonl and updates their
status to 'approved' or 'rejected', then signals continuation or
cancellation of the blocked run.

### Methods

#### HITLApprovalWorkflow.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### HITLApprovalWorkflow.approve

```python
approve(self: Any, run_id: str, reason: Any)
```

Approve a HITL-blocked run.

Updates governance_events.jsonl status to 'approved'.
Returns a result dict with success status and run_id.
Raises ValueError if no pending approval found for run_id.

---

#### HITLApprovalWorkflow.await_approval

```python
await_approval(self: Any, run_id: str, policy: str, reason: str, agent: str, lane: str, owner: str, environment: str, checkpoint: str, unified_diff: Any)
```

Emit an await_approval event for a run requiring human approval.

**Parameters**:

- `run_id`: Unique identifier for the run
- `policy`: Policy name that triggered the approval requirement
- `reason`: Human-readable reason for the approval requirement
- `agent`: Agent name executing the run
- `lane`: Execution lane (standard, critical, recovery)
- `owner`: Owner of the run
- `environment`: Execution environment (development, production)
- `checkpoint`: Checkpoint name (pre_execution, post_execution)
- `unified_diff`: Optional unified diff string for code review

**Returns**: Dict with event_id and run_id

---

#### HITLApprovalWorkflow.list_pending

```python
list_pending(self: Any)
```

Return all pending HITL approval events.

---

#### HITLApprovalWorkflow.reject

```python
reject(self: Any, run_id: str, reason: Any)
```

Reject a HITL-blocked run.

Updates governance_events.jsonl status to 'rejected'.
Returns a result dict with success status and run_id.
Raises ValueError if no pending approval found for run_id.

---

---

## HITLDecision

Result of a HITL gate evaluation (WL-019-A).

**Inherits from**: `SerializableMixin`

### Methods

#### HITLDecision.__init__

```python
__init__(self: Any, required: bool, run_id: str, policy: str, reason: str, checkpoint: str)
```

---

---

## HITLManager

Manages human-in-the-loop signals and approvals (legacy compat, WP-3001).

### Methods

#### HITLManager.__init__

```python
__init__(self: Any)
```

---

#### HITLManager.approve

```python
approve(self: Any, request_id: str)
```

Record an approval for a request.

---

#### HITLManager.is_approved

```python
is_approved(self: Any, request_id: str)
```

Check if a request has been approved.

---

#### HITLManager.request_approval

```python
request_approval(self: Any, request_id: str, action: str, context: dict[(str, Any)])
```

Issue an approval request and return its ID.

---

---

## PolicyEngine

Evaluates HITL gate decisions for a run context (WL-019-A).

This is a standalone HITL-focused policy evaluator. The main execution
PolicyEngine lives in thegent.execution and handles broader policy
(cost, trust score, circuit breaker, OPA).  This class handles the
require_human_approval checkpoint logic and emits await_approval events.

### Methods

#### PolicyEngine.__init__

```python
__init__(self: Any, settings: Any, session_dir: Any)
```

---

#### PolicyEngine.await_approval

```python
await_approval(self: Any, run_id: str, policy: str, reason: str, agent: str, lane: str, checkpoint: str)
```

Emit an await_approval event for a run requiring human approval.

**Parameters**:

- `run_id`: Unique identifier for the run
- `policy`: Policy name that triggered the approval requirement
- `reason`: Human-readable reason for the approval requirement
- `agent`: Agent name executing the run
- `lane`: Execution lane (standard, critical, recovery)
- `checkpoint`: Checkpoint name (pre_execution, post_execution)

**Returns**: Event dict that was emitted

---

#### PolicyEngine.evaluate_hitl

```python
evaluate_hitl(self: Any, run_context: RunContext)
```

Evaluate whether the run requires human approval (G-GP-05, WL-019-A).

When the require_human_approval policy fires:
- Block run execution
- Emit await_approval event to governance_events.jsonl
- Return HITLDecision(required=True, run_id=..., policy=...)

---

---

## RunContext

Lightweight context object used by evaluate_hitl (WL-019-A).

### Methods

#### RunContext.__init__

```python
__init__(self: Any, run_id: str, agent: str, lane: str, confidence: Any, owner: str, prompt: str, environment: str)
```

---

---

## approve

```python
approve(self: Any, request_id: str)
```

Record an approval for a request.

---

## await_approval

```python
await_approval(self: Any, run_id: str, policy: str, reason: str, agent: str, lane: str, owner: str, environment: str, checkpoint: str, unified_diff: Any)
```

Emit an await_approval event for a run requiring human approval.

**Parameters**:

- `run_id`: Unique identifier for the run
- `policy`: Policy name that triggered the approval requirement
- `reason`: Human-readable reason for the approval requirement
- `agent`: Agent name executing the run
- `lane`: Execution lane (standard, critical, recovery)
- `owner`: Owner of the run
- `environment`: Execution environment (development, production)
- `checkpoint`: Checkpoint name (pre_execution, post_execution)
- `unified_diff`: Optional unified diff string for code review

**Returns**: Dict with event_id and run_id

---

## emit

```python
emit(self: Any, event: dict[(str, Any)])
```

Append a governance event to the log.

---

## evaluate_hitl

```python
evaluate_hitl(self: Any, run_context: RunContext)
```

Evaluate whether the run requires human approval (G-GP-05, WL-019-A).

When the require_human_approval policy fires:
- Block run execution
- Emit await_approval event to governance_events.jsonl
- Return HITLDecision(required=True, run_id=..., policy=...)

---

## is_approved

```python
is_approved(self: Any, request_id: str)
```

Check if a request has been approved.

---

## list_pending

```python
list_pending(self: Any)
```

Return all pending HITL approval events.

---

## list_pending_approvals

```python
list_pending_approvals(self: Any, run_id: Any)
```

Return all await_approval events that are not yet resolved.

---

## reject

```python
reject(self: Any, run_id: str, reason: Any)
```

Reject a HITL-blocked run.

Updates governance_events.jsonl status to 'rejected'.
Returns a result dict with success status and run_id.
Raises ValueError if no pending approval found for run_id.

---

## request_approval

```python
request_approval(self: Any, request_id: str, action: str, context: dict[(str, Any)])
```

Issue an approval request and return its ID.

---

## update_status

```python
update_status(self: Any, run_id: str, new_status: str, reason: Any)
```

Update the status of a pending await_approval event. Returns True on success.

---

