# dispatch_graph API Reference

> **Source**: `src/thegent/routing/dispatch_graph.py`

WP-10003: Dispatch graph implementation.

Provides deterministic resolution of operations through a policy-aware dispatch graph.

---

## DispatchResolver

Resolves an OperationEnvelopeV2 to a specific execution path.

### Methods

#### DispatchResolver.__init__

```python
__init__(self, registry)
```

#### DispatchResolver.add_alias

Register an alias for a command (WP-10005).

```python
add_alias(self, alias, target_command)
```

#### DispatchResolver.resolve

Resolve the operation to a dispatch path.

Returns:
    Dict with 'dispatch_path', 'resolved_command', 'status'.

```python
resolve(self, envelope)
```

---

## add_alias

Register an alias for a command (WP-10005).

```python
add_alias(self, alias, target_command)
```

---

## resolve

Resolve the operation to a dispatch path.

Returns:
    Dict with 'dispatch_path', 'resolved_command', 'status'.

```python
resolve(self, envelope)
```

---

