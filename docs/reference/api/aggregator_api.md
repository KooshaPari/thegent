# aggregator API Reference

> **Source**: `src/thegent/orchestration/aggregator.py`

WL-083: ResultAggregator — Aggregate inter-agent messages with cost tracking.

Aggregates InterAgentMessage objects produced by agents and produces an
AggregationResult summary with total count, type breakdown, success/failure
tracking, token sum per wave, global budget overrun detection, and structured
output dict keyed by node_id.

# @trace WL-083

---

## AggregationResult

Structured result from aggregating inter-agent messages.

**Inherits from**: `BaseModel`

---

## GlobalBudgetExceededError

Raised when total token usage exceeds the global budget.

**Inherits from**: `RuntimeError`

### Methods

#### GlobalBudgetExceededError.__init__

```python
__init__(self: Any)
```

---

---

## ResultAggregator

Collect InterAgentMessage objects and produce aggregated results.

Supports:
- Token sum across waves
- Partial failure tracking
- Global budget overrun detection
- Structured output dict keyed by node_id

Usage::

    agg = ResultAggregator(global_budget=100000)
    for msg in messages:
        agg.add(msg, wave_id="wave-1", node_id=msg.sender_id)
    result = agg.aggregate()

# @trace WL-083

### Methods

#### ResultAggregator.__init__

```python
__init__(self: Any, global_budget: Any, tokens_per_message: int)
```

Initialize the ResultAggregator.

**Parameters**:

- `global_budget`: Optional global token budget. If provided and total
tokens exceed this, GlobalBudgetExceededError is raised on aggregate().
- `tokens_per_message`: Default tokens to count per message for budget tracking.

---

#### ResultAggregator.add

```python
add(self: Any, message: Any, wave_id: Any, node_id: Any, tokens: Any)
```

Append an InterAgentMessage for later aggregation.

**Parameters**:

- `message`: An InterAgentMessage instance.
- `wave_id`: Optional wave identifier for token tracking.
- `node_id`: Optional node identifier for by-node aggregation.
- `tokens`: Optional token count for this message. Defaults to tokens_per_message.

---

#### ResultAggregator.aggregate

```python
aggregate(self: Any)
```

Produce an AggregationResult from all stored messages.

**Returns**: Dictionary with total, by_type, results, errors, passed, by_node,
tokens_by_wave, budget_overrun, and total_tokens.

---

#### ResultAggregator.clear

```python
clear(self: Any)
```

Reset all internal state.

# @trace WL-083

---

#### ResultAggregator.summary

```python
summary(self: Any)
```

Return a human-readable summary string.

# @trace WL-083

---

---

## add

```python
add(self: Any, message: Any, wave_id: Any, node_id: Any, tokens: Any)
```

Append an InterAgentMessage for later aggregation.

**Parameters**:

- `message`: An InterAgentMessage instance.
- `wave_id`: Optional wave identifier for token tracking.
- `node_id`: Optional node identifier for by-node aggregation.
- `tokens`: Optional token count for this message. Defaults to tokens_per_message.

---

## aggregate

```python
aggregate(self: Any)
```

Produce an AggregationResult from all stored messages.

**Returns**: Dictionary with total, by_type, results, errors, passed, by_node,
tokens_by_wave, budget_overrun, and total_tokens.

**Raises**:

- `GlobalBudgetExceededError`: If global_budget was set and total tokens exceed it.

---

## clear

```python
clear(self: Any)
```

Reset all internal state.

# @trace WL-083

---

## summary

```python
summary(self: Any)
```

Return a human-readable summary string.

# @trace WL-083

---

