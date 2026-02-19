# formal_loop API Reference

> **Source**: `src/thegent/verification/formal_loop.py`

WP-18004: Automated Formal Verification Loop.
Continously runs symbolic execution and logical verification on the active plan.

---

## FormalVerificationLoop

Automated loop that periodically verifies the agent's plan for logical consistency.

### Methods

#### FormalVerificationLoop.__init__

```python
__init__(self, plan_dag)
```

#### FormalVerificationLoop.get_history

Return history of verification passes.

```python
get_history(self)
```

#### FormalVerificationLoop.run

Execute a formal verification pass.

```python
run(self, start_task)
```

---

## get_history

Return history of verification passes.

```python
get_history(self)
```

---

## run

Execute a formal verification pass.

```python
run(self, start_task)
```

---

