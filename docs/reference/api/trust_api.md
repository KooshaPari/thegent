# trust API Reference

> **Source**: `src/thegent/governance/trust.py`

WP-3007: Trust boundary checks.

---

## TrustBoundaryChecker

Enforces trust boundaries between agents and tasks.

### Methods

#### TrustBoundaryChecker.__init__

```python
__init__(self, settings)
```

#### TrustBoundaryChecker.check_data_flow

Verify data flow from source to destination is allowed.

```python
check_data_flow(self, source_agent, dest_agent)
```

#### TrustBoundaryChecker.evaluate_routing

Evaluate if routing a task to an agent violates trust boundaries.
Checks for sensitive keywords in prompt vs agent trust level.

```python
evaluate_routing(self, task_prompt, target_agent)
```

#### TrustBoundaryChecker.get_agent_trust

Return trust level for an agent.

```python
get_agent_trust(self, agent_name)
```

---

## TrustLevel

Trust levels for agents and domains.

---

## check_data_flow

Verify data flow from source to destination is allowed.

```python
check_data_flow(self, source_agent, dest_agent)
```

---

## evaluate_routing

Evaluate if routing a task to an agent violates trust boundaries.
Checks for sensitive keywords in prompt vs agent trust level.

```python
evaluate_routing(self, task_prompt, target_agent)
```

---

## get_agent_trust

Return trust level for an agent.

```python
get_agent_trust(self, agent_name)
```

---

