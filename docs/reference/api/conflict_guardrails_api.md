# conflict_guardrails API Reference

> **Source**: `src/thegent/integrations/conflict_guardrails.py`

Conflict growth guardrails for sync operations.

Enforces hard limits and warning thresholds on conflict counts during
reconciliation and sync cycles.

FR traceability: WL-304 (Conflict Growth Guardrails)

---

## ConflictGrowthGuardrail

Enforces limits on conflict growth.

### Methods

#### ConflictGrowthGuardrail.__init__

```python
__init__(self: Any, max_conflicts: int, warn_threshold: int)
```

Initialize the guardrail.

**Parameters**:

- `max_conflicts`: Hard limit on conflicts (default: 50).
- `warn_threshold`: Warning threshold (default: 25).

---

#### ConflictGrowthGuardrail.check

```python
check(self: Any, current_count: int)
```

Check if conflict count exceeds the hard limit.

**Parameters**:

- `current_count`: Current number of conflicts.

---

#### ConflictGrowthGuardrail.status

```python
status(self: Any, current_count: int)
```

Get status dict for conflict count.

**Parameters**:

- `current_count`: Current number of conflicts.

**Returns**: Dict with keys: count, warn (bool), exceeded (bool).

---

#### ConflictGrowthGuardrail.warn_level

```python
warn_level(self: Any, current_count: int)
```

Check if conflict count is at warning level.

**Parameters**:

- `current_count`: Current number of conflicts.

**Returns**: True if current_count >= warn_threshold.

---

---

## ConflictLimitExceeded

Raised when conflict count exceeds the hard limit.

**Inherits from**: `Exception`

---

## check

```python
check(self: Any, current_count: int)
```

Check if conflict count exceeds the hard limit.

**Parameters**:

- `current_count`: Current number of conflicts.

**Raises**:

- `ConflictLimitExceeded`: If current_count > max_conflicts.
- `ValueError`: If current_count is negative.

---

## status

```python
status(self: Any, current_count: int)
```

Get status dict for conflict count.

**Parameters**:

- `current_count`: Current number of conflicts.

**Returns**: Dict with keys: count, warn (bool), exceeded (bool).

**Raises**:

- `ValueError`: If current_count is negative.

---

## warn_level

```python
warn_level(self: Any, current_count: int)
```

Check if conflict count is at warning level.

**Parameters**:

- `current_count`: Current number of conflicts.

**Returns**: True if current_count >= warn_threshold.

**Raises**:

- `ValueError`: If current_count is negative.

---

