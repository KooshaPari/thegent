# cost_tracker API Reference

> **Source**: `src/thegent/routing/cost_tracker.py`

Cost tracking for LiteLLM routing.

Tracks LLM costs across sessions with budget alerts and JSONL logging
for integration with the Donut Architecture harvest system.

---

## CostEntry

Single cost tracking entry.

### Methods

#### CostEntry.to_json

Serialize entry to JSON dict.

```python
to_json(self)
```

---

## CostTracker

Track LLM costs across sessions.

### Methods

#### CostTracker.__init__

Initialize cost tracker.

Args:
    log_path: Path to JSONL cost log file.
    daily_budget: Optional daily budget limit in USD.

```python
__init__(self, log_path, daily_budget)
```

#### CostTracker.clear

Reset all tracking state.

```python
clear(self)
```

#### CostTracker.daily_budget

Configured daily budget.

```python
daily_budget(self)
```

#### CostTracker.get_budget_remaining

Get remaining budget, or None if no budget set.

```python
get_budget_remaining(self)
```

#### CostTracker.get_daily_spend

Get today's total spend in USD.

```python
get_daily_spend(self)
```

#### CostTracker.get_stats

Get cost statistics summary.

```python
get_stats(self)
```

#### CostTracker.is_over_budget

Check if daily budget is exceeded.

```python
is_over_budget(self)
```

#### CostTracker.log_path

Path to the cost log file.

```python
log_path(self)
```

#### CostTracker.track

Track a single LLM call cost.

Args:
    provider: Provider name (e.g., "openai", "anthropic")
    model: Model name (e.g., "gpt-4", "claude-opus")
    usage: Dict with prompt_tokens and completion_tokens
    cost: Cost in USD
    latency_ms: Request latency in milliseconds
    session_id: Optional session identifier
    is_error: Whether the request resulted in an error
    is_fallback: Whether this was a fallback routing

Returns:
    The created CostEntry

```python
track(self, provider, model, usage, cost, latency_ms, session_id, is_error, is_fallback)
```

---

## RoutingStats

Routing statistics summary.

---

## clear

Reset all tracking state.

```python
clear(self)
```

---

## daily_budget

Configured daily budget.

```python
daily_budget(self)
```

---

## get_budget_remaining

Get remaining budget, or None if no budget set.

```python
get_budget_remaining(self)
```

---

## get_cost_tracker

Get global cost tracker instance.

Initializes with settings from config on first call.

---

## get_daily_spend

Get today's total spend in USD.

```python
get_daily_spend(self)
```

---

## get_stats

Get cost statistics summary.

```python
get_stats(self)
```

---

## is_over_budget

Check if daily budget is exceeded.

```python
is_over_budget(self)
```

---

## log_path

Path to the cost log file.

```python
log_path(self)
```

---

## reset_cost_tracker

Reset the global cost tracker (useful for testing).

---

## to_json

Serialize entry to JSON dict.

```python
to_json(self)
```

---

## track

Track a single LLM call cost.

Args:
    provider: Provider name (e.g., "openai", "anthropic")
    model: Model name (e.g., "gpt-4", "claude-opus")
    usage: Dict with prompt_tokens and completion_tokens
    cost: Cost in USD
    latency_ms: Request latency in milliseconds
    session_id: Optional session identifier
    is_error: Whether the request resulted in an error
    is_fallback: Whether this was a fallback routing

Returns:
    The created CostEntry

```python
track(self, provider, model, usage, cost, latency_ms, session_id, is_error, is_fallback)
```

---

