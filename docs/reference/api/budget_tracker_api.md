# budget_tracker API Reference

> **Source**: `src/thegent/orchestration/budget_tracker.py`

WL-086: BudgetTracker — Per-Node Token Budget Enforcement.

Wraps JSONL output from CodexProxyRunner / DirectAgentRunner to parse token
usage and enforce ``budget_tokens`` per node.  Raises :class:`BudgetExceededError`
(fail-loud, no silent continuation) when the accumulated token count for a node
exceeds the budget declared in ``node.metadata["budget_tokens"]``.

Supports two constructor patterns:
1. BudgetTracker(budgets={"node_id": 1000}) - dict-based
2. BudgetTracker(plan) - OrchestrationPlan-based

# @trace FR-ORC-086
# @trace WL-086

---

## BudgetExceededError

Raised when a node's accumulated token usage exceeds its budget.

**Inherits from**: `RuntimeError`

### Methods

#### BudgetExceededError.__init__

```python
__init__(self: Any, node_id: str, budget: int, actual: int)
```

---

---

## BudgetTracker

Per-node token budget enforcement.

Supports two constructor patterns:
1. ``BudgetTracker(budgets={"node_id": 1000})`` - dict-based
2. ``BudgetTracker(plan)`` - OrchestrationPlan-based

Accumulates token usage per node and raises :class:`BudgetExceededError`
immediately when a node's budget is exceeded.  There is no silent degradation
or continuation — callers receive a hard exception.

# @trace FR-ORC-086
# @trace WL-086

### Methods

#### BudgetTracker.__init__

```python
__init__(self: Any, plan_or_budgets: OrchestrationPlan | dict[str, int] | None)
```

---

#### BudgetTracker.all_usage

```python
all_usage(self: Any)
```

Snapshot of all accumulated usage as ``{node_id: tokens_used}``.

# @trace FR-ORC-086
# @trace WL-086

---

#### BudgetTracker.check

```python
check(self: Any, node_id: str, tokens: int)
```

Check whether consuming tokens would exceed the node's budget.

This is a point-in-time check against the budget only — it does NOT
consider cumulative usage. Use record() to enforce cumulative limits.

**Parameters**:

- `node_id`: ID of the plan node to check.
- `tokens`: The token count to check against the budget.

---

#### BudgetTracker.get_usage

```python
get_usage(self: Any, node_id: str)
```

Return accumulated tokens used for node_id.

Alias for usage().

**Parameters**:

- `node_id`: ID of the plan node to query.

---

#### BudgetTracker.parse_tokens_from_result

```python
parse_tokens_from_result(stdout: str)
```

Parse total token count from agent JSONL stdout.

Understands both OpenAI-style ``prompt_tokens + completion_tokens`` and
the ``total_tokens`` fallback.  Non-JSON lines are silently skipped.

**Parameters**:

- `stdout`: Raw JSONL output from an agent run.

**Returns**: Total tokens parsed from all ``"usage"`` lines; ``0`` if none found.

---

#### BudgetTracker.record

```python
record(self: Any, node_id: str, tokens: int)
```

Record token usage for a node, raising if cumulative exceeds budget.

**Parameters**:

- `node_id`: ID of the plan node to record usage for.
- `tokens`: Number of tokens consumed in this call.

---

#### BudgetTracker.remaining

```python
remaining(self: Any, node_id: str)
```

Return tokens remaining in the budget for node_id.

**Parameters**:

- `node_id`: ID of the plan node to query.

**Returns**: Budget minus cumulative usage for the node.

---

#### BudgetTracker.reset

```python
reset(self: Any, node_id: str)
```

Reset cumulative usage to zero for node_id.

**Parameters**:

- `node_id`: ID of the plan node to reset.

---

#### BudgetTracker.reset_usage

```python
reset_usage(self: Any, node_id: str)
```

Reset accumulated usage for node_id to zero.

Alias for reset().

**Parameters**:

- `node_id`: ID of the plan node to reset.

---

#### BudgetTracker.track

```python
track(self: Any, node_id: str, tokens_used: int)
```

Accumulate tokens_used for node_id and enforce the budget.

Alias for record() - accumulates usage and raises if budget exceeded.

**Parameters**:

- `node_id`: ID of the plan node to track usage for.
- `tokens_used`: Number of tokens consumed in this call.

---

#### BudgetTracker.track_result_stdout

```python
track_result_stdout(self: Any, node_id: str, stdout: str)
```

Parse tokens from *stdout* and track them for *node_id*.

**Parameters**:

- `node_id`: ID of the plan node to track.
- `stdout`: Raw JSONL stdout from an agent run.

**Returns**: Number of tokens parsed from *stdout* in this call.

---

#### BudgetTracker.usage

```python
usage(self: Any, node_id: str)
```

Return cumulative token usage recorded for node_id.

**Parameters**:

- `node_id`: ID of the plan node to query.

**Returns**: Total tokens recorded so far for the node.

---

---

## all_usage

```python
all_usage(self: Any)
```

Snapshot of all accumulated usage as ``{node_id: tokens_used}``.

# @trace FR-ORC-086
# @trace WL-086

---

## check

```python
check(self: Any, node_id: str, tokens: int)
```

Check whether consuming tokens would exceed the node's budget.

This is a point-in-time check against the budget only — it does NOT
consider cumulative usage. Use record() to enforce cumulative limits.

**Parameters**:

- `node_id`: ID of the plan node to check.
- `tokens`: The token count to check against the budget.

**Raises**:

- `KeyError`: If node_id is not in the configured budgets.
- `BudgetExceededError`: If tokens > budget for node_id.

---

## get_usage

```python
get_usage(self: Any, node_id: str)
```

Return accumulated tokens used for node_id.

Alias for usage().

**Parameters**:

- `node_id`: ID of the plan node to query.

**Raises**:

- `KeyError`: If node_id does not exist in the configured budgets.

---

## parse_tokens_from_result

```python
parse_tokens_from_result(stdout: str)
```

Parse total token count from agent JSONL stdout.

Understands both OpenAI-style ``prompt_tokens + completion_tokens`` and
the ``total_tokens`` fallback.  Non-JSON lines are silently skipped.

**Parameters**:

- `stdout`: Raw JSONL output from an agent run.

**Returns**: Total tokens parsed from all ``"usage"`` lines; ``0`` if none found.

---

## record

```python
record(self: Any, node_id: str, tokens: int)
```

Record token usage for a node, raising if cumulative exceeds budget.

**Parameters**:

- `node_id`: ID of the plan node to record usage for.
- `tokens`: Number of tokens consumed in this call.

**Raises**:

- `KeyError`: If node_id is not in the configured budgets.
- `BudgetExceededError`: If cumulative usage after this call > budget.

---

## remaining

```python
remaining(self: Any, node_id: str)
```

Return tokens remaining in the budget for node_id.

**Parameters**:

- `node_id`: ID of the plan node to query.

**Returns**: Budget minus cumulative usage for the node.

**Raises**:

- `KeyError`: If node_id is not in the configured budgets.

---

## reset

```python
reset(self: Any, node_id: str)
```

Reset cumulative usage to zero for node_id.

**Parameters**:

- `node_id`: ID of the plan node to reset.

**Raises**:

- `KeyError`: If node_id is not in the configured budgets.

---

## reset_usage

```python
reset_usage(self: Any, node_id: str)
```

Reset accumulated usage for node_id to zero.

Alias for reset().

**Parameters**:

- `node_id`: ID of the plan node to reset.

**Raises**:

- `KeyError`: If node_id does not exist in the configured budgets.

---

## track

```python
track(self: Any, node_id: str, tokens_used: int)
```

Accumulate tokens_used for node_id and enforce the budget.

Alias for record() - accumulates usage and raises if budget exceeded.

**Parameters**:

- `node_id`: ID of the plan node to track usage for.
- `tokens_used`: Number of tokens consumed in this call.

**Raises**:

- `KeyError`: If node_id does not exist in the configured budgets.
- `BudgetExceededError`: If the accumulated token usage exceeds the
node's budget.

---

## track_result_stdout

```python
track_result_stdout(self: Any, node_id: str, stdout: str)
```

Parse tokens from *stdout* and track them for *node_id*.

**Parameters**:

- `node_id`: ID of the plan node to track.
- `stdout`: Raw JSONL stdout from an agent run.

**Returns**: Number of tokens parsed from *stdout* in this call.

**Raises**:

- `KeyError`: If *node_id* does not exist in the plan.
- `BudgetExceededError`: If the accumulated token usage exceeds the
node's budget.

---

## usage

```python
usage(self: Any, node_id: str)
```

Return cumulative token usage recorded for node_id.

**Parameters**:

- `node_id`: ID of the plan node to query.

**Returns**: Total tokens recorded so far for the node.

**Raises**:

- `KeyError`: If node_id is not in the configured budgets.

---

