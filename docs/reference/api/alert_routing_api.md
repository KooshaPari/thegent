# alert_routing API Reference

> **Source**: `src/thegent/integrations/alert_routing.py`

Alert Routing Hooks for pluggable alert handling.

WL-318: Alert Routing Hooks
Provides pluggable alert routing hooks for webhook, email, and event bus integration.

---

## Alert

An alert event with severity, message, and context.

---

## AlertRouter

Router for pluggable alert handling hooks.

### Methods

#### AlertRouter.__init__

```python
__init__(self: Any)
```

Initialize the alert router.

---

#### AlertRouter.list_hooks

```python
list_hooks(self: Any)
```

List all registered hook names.

**Returns**: Sorted list of hook names.

---

#### AlertRouter.register_hook

```python
register_hook(self: Any, name: str, fn: Callable[(Any, None)])
```

Register an alert routing hook.

**Parameters**:

- `name`: Unique name for the hook.
- `fn`: Callable that accepts an Alert and returns None.

---

#### AlertRouter.route

```python
route(self: Any, alert: Alert)
```

Route an alert to all registered hooks.

**Parameters**:

- `alert`: Alert to route.

**Returns**: Number of hooks called.

---

#### AlertRouter.unregister_hook

```python
unregister_hook(self: Any, name: str)
```

Unregister an alert routing hook.

**Parameters**:

- `name`: Name of hook to remove.

---

---

## AlertSeverity

Alert severity classification.

**Inherits from**: `str, Enum`

---

## list_hooks

```python
list_hooks(self: Any)
```

List all registered hook names.

**Returns**: Sorted list of hook names.

---

## register_hook

```python
register_hook(self: Any, name: str, fn: Callable[(Any, None)])
```

Register an alert routing hook.

**Parameters**:

- `name`: Unique name for the hook.
- `fn`: Callable that accepts an Alert and returns None.

---

## route

```python
route(self: Any, alert: Alert)
```

Route an alert to all registered hooks.

**Parameters**:

- `alert`: Alert to route.

**Returns**: Number of hooks called.

---

## unregister_hook

```python
unregister_hook(self: Any, name: str)
```

Unregister an alert routing hook.

**Parameters**:

- `name`: Name of hook to remove.

**Raises**:

- `KeyError`: If hook with given name does not exist.

---

