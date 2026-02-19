# omega API Reference

> **Source**: `src/thegent/planning/omega.py`

WP-45001: Entropy-Minimizing Execution Loop (Omega).
Optimizes execution by minimizing planning entropy and pruning redundant actions.

---

## OmegaExecutionResult

Result of an entropy-minimized execution step.

**Inherits from**: `BaseModel`

---

## OmegaLoop

The final-stage execution loop for thegent (Phase 45).
Focuses on minimizing entropy (wasted effort, redundant plans, and uncertainty).

### Methods

#### OmegaLoop.__init__

```python
__init__(self, agent_id)
```

#### OmegaLoop.calculate_entropy

Calculate the entropy (unpredictability/redundancy) of a proposed plan.

```python
calculate_entropy(self, plan)
```

#### OmegaLoop.minimize_entropy

Optimize a plan by pruning redundant or high-entropy actions.

```python
minimize_entropy(self, cycle_id, proposed_plan)
```

---

## calculate_entropy

Calculate the entropy (unpredictability/redundancy) of a proposed plan.

```python
calculate_entropy(self, plan)
```

---

## minimize_entropy

Optimize a plan by pruning redundant or high-entropy actions.

```python
minimize_entropy(self, cycle_id, proposed_plan)
```

---

