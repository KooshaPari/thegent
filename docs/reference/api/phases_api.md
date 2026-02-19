# phases API Reference

> **Source**: `src/thegent/orchestration/phases.py`

Deterministic phase transition contracts (WP-1004, FR-004).

Defines allowed state transitions for orchestration. Same (from_state, to_state)
always yields same result — deterministic for replay and idempotency.

---

## PhaseTransitionContract

Deterministic contract for phase transitions.

Usage:
    contract = PhaseTransitionContract()
    assert contract.validate("pending", "running")
    assert not contract.validate("completed", "running")

### Methods

#### PhaseTransitionContract.allowed_targets

Return allowed target states for from_state.

```python
allowed_targets(cls, from_state)
```

#### PhaseTransitionContract.validate

Return True iff transition from_state -> to_state is allowed.

```python
validate(cls, from_state, to_state)
```

---

## allowed_targets

Return allowed target states for from_state.

```python
allowed_targets(cls, from_state)
```

---

## validate

Return True iff transition from_state -> to_state is allowed.

```python
validate(cls, from_state, to_state)
```

---

## validate_transition

Validate phase transition (from_state -> to_state). Deterministic.

```python
validate_transition(from_state, to_state)
```

---

