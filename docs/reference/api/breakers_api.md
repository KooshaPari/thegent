# breakers API Reference

> **Source**: `src/thegent/governance/breakers.py`

WP-5005: Usage spike circuit breakers.

---

## CircuitBreaker

Breaks the flow when usage spikes are detected.

### Methods

#### CircuitBreaker.__init__

```python
__init__(self, session_dir)
```

#### CircuitBreaker.check_spike

Check if the current cost batch causes a spike.

```python
check_spike(self, current_batch_cost)
```

#### CircuitBreaker.is_tripped

Return True if any active breaker is tripped.

```python
is_tripped(self)
```

#### CircuitBreaker.trip

Trip the circuit breaker.

```python
trip(self, reason, value)
```

---

## check_spike

Check if the current cost batch causes a spike.

```python
check_spike(self, current_batch_cost)
```

---

## is_tripped

Return True if any active breaker is tripped.

```python
is_tripped(self)
```

---

## trip

Trip the circuit breaker.

```python
trip(self, reason, value)
```

---

