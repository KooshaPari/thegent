# policy_gate API Reference

> **Source**: `src/thegent/ports/driven/policy_gate.py`

Protocol for governance policy evaluation.

---

## PolicyGate

Port interface for governance policy evaluation.

Breaks governance ↔ execution circular dependency by allowing
execution logic to query policy decisions without importing
governance implementation details.

**Inherits from**: `Protocol`

### Methods

#### PolicyGate.evaluate_policy

```python
evaluate_policy(self: Any, action: str, context: dict[(str, Any)])
```

Evaluate whether an action is allowed under current policies.

**Parameters**:

- `action`: Action identifier (e.g., 'agent.spawn', 'hook.execute', 'file.write').
- `context`: Policy evaluation context (e.g., {'agent_type': 'free', 'module': 'cli'}).

**Returns**: True if action is allowed, False otherwise.

---

#### PolicyGate.get_active_policies

```python
get_active_policies(self: Any)
```

Get list of currently active policy names.

**Returns**: List of active policy identifiers.

---

---

## evaluate_policy

```python
evaluate_policy(self: Any, action: str, context: dict[(str, Any)])
```

Evaluate whether an action is allowed under current policies.

**Parameters**:

- `action`: Action identifier (e.g., 'agent.spawn', 'hook.execute', 'file.write').
- `context`: Policy evaluation context (e.g., {'agent_type': 'free', 'module': 'cli'}).

**Returns**: True if action is allowed, False otherwise.

---

## get_active_policies

```python
get_active_policies(self: Any)
```

Get list of currently active policy names.

**Returns**: List of active policy identifiers.

---

