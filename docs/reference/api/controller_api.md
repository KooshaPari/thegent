# controller API Reference

> **Source**: `src/thegent/sync/controller.py`

Sync maintenance freeze controls.

# @trace WL-206

---

## FreezeState

---

## SyncController

Controls write freeze/unfreeze state for sync operations.

### Methods

#### SyncController.__init__

```python
__init__(self: Any, state_path: Path)
```

---

#### SyncController.assert_writes_allowed

```python
assert_writes_allowed(self: Any)
```

---

#### SyncController.freeze

```python
freeze(self: Any)
```

---

#### SyncController.is_frozen

```python
is_frozen(self: Any)
```

---

#### SyncController.status

```python
status(self: Any)
```

---

#### SyncController.unfreeze

```python
unfreeze(self: Any)
```

---

---

## assert_writes_allowed

```python
assert_writes_allowed(self: Any) -> None
```

---

## freeze

```python
freeze(self: Any) -> FreezeState
```

---

## is_frozen

```python
is_frozen(self: Any) -> bool
```

---

## status

```python
status(self: Any) -> Any
```

---

## unfreeze

```python
unfreeze(self: Any) -> None
```

---

