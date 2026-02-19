# lock_free API Reference

> **Source**: `src/thegent/orchestration/lock_free.py`

WP-21003: Lock-Free Agent State Transitions.
MTSP-13/14: Use atomic versioned state to allow high-concurrency multi-tenant access
without traditional mutex locking overhead.

---

## AtomicState

A versioned state object for lock-free transitions.

---

## LockFreeStateManager

Manages agent state transitions using Compare-And-Swap (CAS) principles.

### Methods

#### LockFreeStateManager.__init__

```python
__init__(self)
```

#### LockFreeStateManager.compare_and_swap

Perform a lock-free transition.
Returns True if transition successful (version matched), False otherwise.

```python
compare_and_swap(self, key, expected_version, new_value)
```

#### LockFreeStateManager.get_state

Get the current versioned state.

```python
get_state(self, key)
```

#### LockFreeStateManager.set_state

Set state with a new version.

```python
set_state(self, key, value)
```

---

## compare_and_swap

Perform a lock-free transition.
Returns True if transition successful (version matched), False otherwise.

```python
compare_and_swap(self, key, expected_version, new_value)
```

---

## get_state

Get the current versioned state.

```python
get_state(self, key)
```

---

## set_state

Set state with a new version.

```python
set_state(self, key, value)
```

---

