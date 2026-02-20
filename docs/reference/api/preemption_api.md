# preemption API Reference

> **Source**: `src/thegent/routing/preemption.py`

WP-11004: Preemption and saturation avoidance policies.

Defines rules for preempting non-critical tasks to avoid service saturation.

---

## PreemptionPolicy

Policy engine for task preemption and saturation control.

### Methods

#### PreemptionPolicy.evaluate_preemption

```python
evaluate_preemption(self: Any, system_load: float, task_lane: str)
```

Determine if a task should be preempted based on load and lane.

---

---

## evaluate_preemption

```python
evaluate_preemption(self: Any, system_load: float, task_lane: str)
```

Determine if a task should be preempted based on load and lane.

---

