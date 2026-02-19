# cost_controller API Reference

> **Source**: `src/thegent/governance/cost_controller.py`

Call-count budget management for AgilePlus autonomous governance.

Tracks daily agent trigger counts against a configurable budget (default 20/day)
and enforces tiered throttling as utilization increases. Budget tiers and limits
are loaded from contracts/health-targets.json.

---

## BudgetTier

Throttle tier based on daily budget utilization percentage.

**Inherits from**: `str, Enum`

---

## CostController

Manages daily agent-call budgets with tiered throttling.

Budget is measured in agent trigger count (not dollars). When utilization
crosses tier thresholds the controller progressively restricts which agent
types may be spawned, ultimately halting all spawns at 95%+ utilization.

### Methods

#### CostController.__init__

```python
__init__(self, session_dir, health_targets_path)
```

#### CostController.calls_remaining

Number of agent calls remaining in today's budget.

```python
calls_remaining(self)
```

#### CostController.can_spawn

Return False when budget exhausted or insufficient for estimated_calls.

```python
can_spawn(self, estimated_calls)
```

#### CostController.get_tier

Determine the current budget tier from today's utilization.

```python
get_tier(self)
```

#### CostController.get_today_usage

Load or create today's usage record from the JSONL ledger.

```python
get_today_usage(self)
```

#### CostController.record_call

Record one agent trigger against today's budget.

```python
record_call(self, dimension, agent)
```

#### CostController.usage_path

```python
usage_path(self)
```

---

## DailyUsage

Snapshot of agent call consumption for a single calendar day.

**Inherits from**: `BaseModel`

---

## calls_remaining

Number of agent calls remaining in today's budget.

```python
calls_remaining(self)
```

---

## can_spawn

Return False when budget exhausted or insufficient for estimated_calls.

```python
can_spawn(self, estimated_calls)
```

---

## get_tier

Determine the current budget tier from today's utilization.

```python
get_tier(self)
```

---

## get_today_usage

Load or create today's usage record from the JSONL ledger.

```python
get_today_usage(self)
```

---

## record_call

Record one agent trigger against today's budget.

```python
record_call(self, dimension, agent)
```

---

## usage_path

```python
usage_path(self)
```

---

