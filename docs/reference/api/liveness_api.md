# liveness API Reference

> **Source**: `src/thegent/verification/liveness.py`

WP-25001: Liveness Proofs for Autonomous Agent Loops.
Ensures that an agent loop will eventually terminate or make progress.
Uses formal-inspired invariant checking on loop state history.

---

## LivenessChecker

Verifies liveness properties of autonomous execution loops.

### Methods

#### LivenessChecker.__init__

```python
__init__(self, run_id, max_retries, progress_timeout_s)
```

#### LivenessChecker.check_invariants

Check for liveness violations in the execution history.

```python
check_invariants(self)
```

#### LivenessChecker.record_step

Record a step in the agent loop for liveness analysis.

```python
record_step(self, step_type, state)
```

---

## LivenessViolation

Details of a detected liveness violation.

**Inherits from**: `BaseModel`

---

## check_invariants

Check for liveness violations in the execution history.

```python
check_invariants(self)
```

---

## record_step

Record a step in the agent loop for liveness analysis.

```python
record_step(self, step_type, state)
```

---

