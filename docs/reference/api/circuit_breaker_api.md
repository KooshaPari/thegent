# circuit_breaker API Reference

> **Source**: `src/thegent/orchestration/circuit_breaker.py`

Circuit breaker service per subsystem (WP-2003, FR-007).

Delegates to execution.CircuitBreakerRegistry. Provides trip, recover, half-open semantics.

---

## is_open

True if circuit is open (blocked). False if closed or half-open (trial allowed).

```python
is_open(session_dir, target, category)
```

---

## should_allow

True if requests to target should be allowed (circuit closed or half-open).

```python
should_allow(session_dir, target, category)
```

---

## trip

Record a failure; may open the circuit.

```python
trip(session_dir, target, category)
```

---

