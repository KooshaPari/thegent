# evolution API Reference

> **Source**: `src/thegent/planning/evolution.py`

WP-37003: Infinite Plan Evolution Loop.
Continously evolves the project plan (DAG) as new information is discovered.

---

## PlanEvolver

Orchestrates the continuous evolution of the Work Breakdown Structure and DAG.

### Methods

#### PlanEvolver.__init__

```python
__init__(self, current_dag)
```

#### PlanEvolver.evolve_dag

WP-37003: Analyze discovery events and append new work packages to the plan.

```python
evolve_dag(self, discovery_events)
```

#### PlanEvolver.sandbox_evolution

Run a simulation to see if the evolved plan is faster or cheaper.

```python
sandbox_evolution(self, proposed_changes)
```

---

## evolve_dag

WP-37003: Analyze discovery events and append new work packages to the plan.

```python
evolve_dag(self, discovery_events)
```

---

## sandbox_evolution

Run a simulation to see if the evolved plan is faster or cheaper.

```python
sandbox_evolution(self, proposed_changes)
```

---

