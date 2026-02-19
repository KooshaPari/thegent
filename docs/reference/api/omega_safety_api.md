# omega_safety API Reference

> **Source**: `src/thegent/verification/omega_safety.py`

WP-45002: Universal Safety Invariants (Omega).
Enforces system-wide, non-negotiable safety properties across all agent actions.

---

## OmegaInvariantViolation

Details of a universal safety invariant violation.

**Inherits from**: `BaseModel`

---

## OmegaSafetyGuard

The final safety gate for thegent (Phase 45).
Enforces 'Omega' invariants which are universal and cannot be overridden.

### Methods

#### OmegaSafetyGuard.__init__

```python
__init__(self)
```

#### OmegaSafetyGuard.is_safe

Convenience method to check if an action is safe according to Omega invariants.

```python
is_safe(self, action_id, action_data)
```

#### OmegaSafetyGuard.verify_action

Verify an action against all universal Omega invariants.

```python
verify_action(self, action_id, action_data)
```

---

## is_safe

Convenience method to check if an action is safe according to Omega invariants.

```python
is_safe(self, action_id, action_data)
```

---

## verify_action

Verify an action against all universal Omega invariants.

```python
verify_action(self, action_id, action_data)
```

---

