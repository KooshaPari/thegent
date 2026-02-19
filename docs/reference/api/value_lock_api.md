# value_lock API Reference

> **Source**: `src/thegent/governance/value_lock.py`

WP-29001: Value-Lock (Immutable Ethical Constraints).
Provides a mechanism to lock core agent values and ethical constraints.
Ensures that even if self-evolution occurs, fundamental alignment principles cannot be removed.

---

## LockedPrinciple

An ethically-locked principle that cannot be modified by autonomous loops.

**Inherits from**: `BaseModel`

---

## ValueLock

Manages immutable ethical constraints for thegent.

### Methods

#### ValueLock.__init__

```python
__init__(self, lock_path)
```

#### ValueLock.lock_principle

Ethically lock a principle, preventing future modification.

```python
lock_principle(self, principle_id, description)
```

#### ValueLock.validate_change

Validate if a proposed change violates a Value-Lock.

```python
validate_change(self, principle_id, new_description)
```

---

## lock_principle

Ethically lock a principle, preventing future modification.

```python
lock_principle(self, principle_id, description)
```

---

## validate_change

Validate if a proposed change violates a Value-Lock.

```python
validate_change(self, principle_id, new_description)
```

---

