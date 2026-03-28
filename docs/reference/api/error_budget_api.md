# error_budget API Reference

> **Source**: `src/thegent/integrations/error_budget.py`

Error Budget and Escalation Thresholds for autosync reliability.

# @trace WL-170

---

## ErrorBudgetConfig

Configuration for error budget tracking and escalation.

---

## ErrorBudgetTracker

Track error budget and determine escalation/hard-fail behavior.

### Methods

#### ErrorBudgetTracker.__init__

```python
__init__(self: Any, config: Any)
```

Initialize the error budget tracker.

**Parameters**:

- `config`: ErrorBudgetConfig instance. Uses defaults if None.

---

#### ErrorBudgetTracker.get_stats

```python
get_stats(self: Any)
```

Get current tracking statistics.

**Returns**: Dictionary with success_count, failure_count, consecutive_failures,
total_operations, and current_failure_rate.

---

#### ErrorBudgetTracker.record_failure

```python
record_failure(self: Any)
```

Record a failed operation.

---

#### ErrorBudgetTracker.record_success

```python
record_success(self: Any)
```

Record a successful operation.

---

#### ErrorBudgetTracker.reset

```python
reset(self: Any)
```

Reset all counters.

---

#### ErrorBudgetTracker.should_escalate

```python
should_escalate(self: Any)
```

Determine if escalation is needed.

Escalation happens when total failures exceed escalation_after threshold.

**Returns**: True if escalation is recommended, False otherwise.

---

#### ErrorBudgetTracker.should_hard_fail

```python
should_hard_fail(self: Any)
```

Determine if hard failure should occur.

Hard fail happens when:
- Consecutive failures exceed max_consecutive_failures, OR
- Failure rate exceeds max_failure_rate

**Returns**: True if hard failure should occur, False otherwise.

---

---

## get_stats

```python
get_stats(self: Any)
```

Get current tracking statistics.

**Returns**: Dictionary with success_count, failure_count, consecutive_failures,
total_operations, and current_failure_rate.

---

## record_failure

```python
record_failure(self: Any)
```

Record a failed operation.

---

## record_success

```python
record_success(self: Any)
```

Record a successful operation.

---

## reset

```python
reset(self: Any)
```

Reset all counters.

---

## should_escalate

```python
should_escalate(self: Any)
```

Determine if escalation is needed.

Escalation happens when total failures exceed escalation_after threshold.

**Returns**: True if escalation is recommended, False otherwise.

---

## should_hard_fail

```python
should_hard_fail(self: Any)
```

Determine if hard failure should occur.

Hard fail happens when:
- Consecutive failures exceed max_consecutive_failures, OR
- Failure rate exceeds max_failure_rate

**Returns**: True if hard failure should occur, False otherwise.

---

