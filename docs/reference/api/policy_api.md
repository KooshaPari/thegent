# policy API Reference

> **Source**: `src/thegent/contracts/policy.py`

Normalization policy and fallback evaluation for agent outputs.

Defines rules for when a normalized message is acceptable and when a fallback
to plain text extraction should be flagged or blocked.

---

## FallbackPolicy

Configuration for normalization fallback behavior and SLO budgets.

---

## PolicyRegistry

Registry for named fallback policies.

### Methods

#### PolicyRegistry.__init__

```python
__init__(self)
```

#### PolicyRegistry.get

Get policy by name, falling back to default.

```python
get(self, name)
```

#### PolicyRegistry.register

Register a named policy.

```python
register(self, name, policy)
```

---

## evaluate_fallback

Evaluate if a normalization result violates fallback policies.

Returns:
    List of policy violation strings. Empty if valid.

```python
evaluate_fallback(provider, confidence, is_fallback, policy, stats)
```

---

## get

Get policy by name, falling back to default.

```python
get(self, name)
```

---

## get_policy_registry

Get global policy registry (singleton).

---

## register

Register a named policy.

```python
register(self, name, policy)
```

---

