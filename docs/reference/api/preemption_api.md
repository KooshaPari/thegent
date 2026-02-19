# preemption API Reference

> **Source**: `src/thegent/routing/preemption.py`

WP-11004: Preemption and saturation avoidance policies.

Defines rules for preempting non-critical tasks to avoid service saturation.

---

## PreemptionPolicy

Policy engine for task preemption and saturation control.

### Methods

#### PreemptionPolicy.evaluate_preemption

Determine if a task should be preempted based on load and lane.

```python
evaluate_preemption(self, system_load, task_lane)
```

---

## evaluate_preemption

Determine if a task should be preempted based on load and lane.

```python
evaluate_preemption(self, system_load, task_lane)
```

---

