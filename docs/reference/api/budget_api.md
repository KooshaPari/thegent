# budget API Reference

> **Source**: `src/thegent/utils/routing_impl/budget.py`

GW-29/GW-30/GW-31: Budget hierarchy with reset periods and soft alerts.

Implements Team -> User -> Key spending hierarchy.
Budget reset periods: daily, weekly, monthly.
Soft alert at 80% spend, hard block at 100%.

# @trace FR-BUDGET-029 FR-BUDGET-030 FR-BUDGET-031

---

## BudgetCheckResult

Result of checking the budget hierarchy for a request.

---

## BudgetHierarchy

Team -> User -> Key budget hierarchy.

Records spending at all levels simultaneously.
Hard-blocks a request if ANY level is exhausted.
Emits a soft alert (via BudgetCheckResult) if ANY level is at threshold.

### Methods

#### BudgetHierarchy.__init__

```python
__init__(self: Any)
```

---

#### BudgetHierarchy.check_budget

```python
check_budget(self: Any, entity_ids: list[str])
```

Check if any entity in the hierarchy has exhausted its budget.

Iterates entity_ids in order (team -> user -> key). Returns on the
first exhausted entity. Collects all entities at the soft-alert threshold.

**Parameters**:

- `entity_ids`: Ordered list of entity identifiers to check.

**Returns**: BudgetCheckResult with allowed, soft_alert, blocking_entity, and
alert_entities populated.

---

#### BudgetHierarchy.get

```python
get(self: Any, entity_id: str)
```

Return the budget record for entity_id, or None if not registered.

---

#### BudgetHierarchy.record_spend

```python
record_spend(self: Any, entity_ids: list[str], cost_usd: float)
```

Record cost_usd against all given entity_ids (team, user, key chain).

Automatically resets periods that have elapsed before adding spend.

**Parameters**:

- `entity_ids`: Ordered list of entity identifiers (e.g. [team_id, user_id, key_id]).
- `cost_usd`: Amount spent in USD to add to each entity's record.

---

#### BudgetHierarchy.register

```python
register(self: Any, record: BudgetRecord)
```

Register or replace a budget record.

---

---

## BudgetPeriod

Supported budget reset period lengths.

**Inherits from**: `str, Enum`

---

## BudgetRecord

Budget state for a single entity (team, user, or key).

Tracks cumulative spend within the current period. The period auto-resets
when BudgetResetChecker.maybe_reset() is called and the period has elapsed.

### Methods

#### BudgetRecord.fraction_used

```python
fraction_used(self: Any)
```

Fraction of budget used (0.0-1.0+). Returns 0.0 when budget_usd=0.

---

#### BudgetRecord.is_exhausted

```python
is_exhausted(self: Any)
```

True when spend >= budget (hard block).

When budget_usd is 0 the budget is unlimited and this always returns False.

---

#### BudgetRecord.is_soft_alert

```python
is_soft_alert(self: Any)
```

True when spend >= alert_threshold * budget but not yet exhausted.

When budget_usd is 0 there is no limit so this always returns False.

---

---

## BudgetResetChecker

Checks if a BudgetRecord's period has elapsed and resets it if so.

### Methods

#### BudgetResetChecker.maybe_reset

```python
maybe_reset(cls: Any, record: BudgetRecord)
```

Reset record.spent_usd to 0 and update period_start if period elapsed.

**Parameters**:

- `record`: The BudgetRecord to inspect and potentially reset.

**Returns**: True if a reset occurred, False otherwise.

---

---

## check_budget

```python
check_budget(self: Any, entity_ids: list[str])
```

Check if any entity in the hierarchy has exhausted its budget.

Iterates entity_ids in order (team -> user -> key). Returns on the
first exhausted entity. Collects all entities at the soft-alert threshold.

**Parameters**:

- `entity_ids`: Ordered list of entity identifiers to check.

**Returns**: BudgetCheckResult with allowed, soft_alert, blocking_entity, and
alert_entities populated.

---

## fraction_used

```python
fraction_used(self: Any)
```

Fraction of budget used (0.0-1.0+). Returns 0.0 when budget_usd=0.

---

## get

```python
get(self: Any, entity_id: str)
```

Return the budget record for entity_id, or None if not registered.

---

## get_budget_hierarchy

Return the process-global BudgetHierarchy singleton.

---

## is_exhausted

```python
is_exhausted(self: Any)
```

True when spend >= budget (hard block).

When budget_usd is 0 the budget is unlimited and this always returns False.

---

## is_soft_alert

```python
is_soft_alert(self: Any)
```

True when spend >= alert_threshold * budget but not yet exhausted.

When budget_usd is 0 there is no limit so this always returns False.

---

## maybe_reset

```python
maybe_reset(cls: Any, record: BudgetRecord)
```

Reset record.spent_usd to 0 and update period_start if period elapsed.

**Parameters**:

- `record`: The BudgetRecord to inspect and potentially reset.

**Returns**: True if a reset occurred, False otherwise.

---

## record_spend

```python
record_spend(self: Any, entity_ids: list[str], cost_usd: float)
```

Record cost_usd against all given entity_ids (team, user, key chain).

Automatically resets periods that have elapsed before adding spend.

**Parameters**:

- `entity_ids`: Ordered list of entity identifiers (e.g. [team_id, user_id, key_id]).
- `cost_usd`: Amount spent in USD to add to each entity's record.

---

## register

```python
register(self: Any, record: BudgetRecord)
```

Register or replace a budget record.

---

## reset_budget_hierarchy

Reset the singleton (for testing only).

---

