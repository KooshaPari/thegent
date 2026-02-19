# multiverse API Reference

> **Source**: `src/thegent/planning/multiverse.py`

WP-38001: Alternate Reality Simulator (Plan Forks).
Allows the agent to simulate parallel timelines for a project plan to evaluate risks and opportunities.

---

## TimelineFork

A parallel version of the project plan.

---

## multiverseSimulator

Simulates multiple plan 'forks' simultaneously.

### Methods

#### multiverseSimulator.__init__

```python
__init__(self, current_plan)
```

#### multiverseSimulator.create_fork

WP-38001: Create a new parallel timeline for simulation.

```python
create_fork(self, divergence_wp, proposed_delta)
```

#### multiverseSimulator.merge_timeline

WP-38003: Reconcile a parallel timeline back into the main branch.

```python
merge_timeline(self, fork_id)
```

#### multiverseSimulator.simulate_impact

WP-38002: Analyze the impact of a specific fork.

```python
simulate_impact(self, fork_id)
```

---

## create_fork

WP-38001: Create a new parallel timeline for simulation.

```python
create_fork(self, divergence_wp, proposed_delta)
```

---

## merge_timeline

WP-38003: Reconcile a parallel timeline back into the main branch.

```python
merge_timeline(self, fork_id)
```

---

## simulate_impact

WP-38002: Analyze the impact of a specific fork.

```python
simulate_impact(self, fork_id)
```

---

