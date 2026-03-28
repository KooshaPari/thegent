# connector_circuit_breaker API Reference

> **Source**: `src/thegent/integrations/connector_circuit_breaker.py`

Connector circuit breakers.

Implements circuit breaker pattern for connector health management, allowing
graceful degradation when a connector experiences repeated failures.

# @trace WL-194

---

## CircuitState

Circuit breaker state enum.

**Inherits from**: `Enum`

---

## ConnectorCircuitBreaker

Circuit breaker for connector failures.

Tracks failure count and transitions between states (CLOSED -> OPEN -> HALF_OPEN -> CLOSED).
Prevents cascading failures by blocking requests when the circuit is open.

### Methods

#### ConnectorCircuitBreaker.__init__

```python
__init__(self: Any, failure_threshold: int, recovery_timeout_seconds: float)
```

Initialize the circuit breaker.

**Parameters**:

- `failure_threshold`: Number of failures required to open the circuit.
- `recovery_timeout_seconds`: Time (in seconds) before attempting recovery.

---

#### ConnectorCircuitBreaker.failure_count

```python
failure_count(self: Any)
```

Get the current failure count.

**Returns**: Number of consecutive failures recorded.

---

#### ConnectorCircuitBreaker.is_open

```python
is_open(self: Any)
```

Check if the circuit is currently open (blocking requests).

**Returns**: True if the circuit is OPEN or HALF_OPEN, False if CLOSED.

---

#### ConnectorCircuitBreaker.record_failure

```python
record_failure(self: Any)
```

Record a failure and update circuit state.

If failure count reaches threshold, opens the circuit.
If circuit is HALF_OPEN, any failure returns to OPEN.

---

#### ConnectorCircuitBreaker.record_success

```python
record_success(self: Any)
```

Record a successful request and reset failures.

If circuit is HALF_OPEN, transitions to CLOSED.
If circuit is CLOSED, resets failure counter.

---

#### ConnectorCircuitBreaker.state

```python
state(self: Any)
```

Get the current circuit state.

**Returns**: Current CircuitState (CLOSED, OPEN, or HALF_OPEN).

---

---

## failure_count

```python
failure_count(self: Any)
```

Get the current failure count.

**Returns**: Number of consecutive failures recorded.

---

## is_open

```python
is_open(self: Any)
```

Check if the circuit is currently open (blocking requests).

**Returns**: True if the circuit is OPEN or HALF_OPEN, False if CLOSED.

---

## record_failure

```python
record_failure(self: Any)
```

Record a failure and update circuit state.

If failure count reaches threshold, opens the circuit.
If circuit is HALF_OPEN, any failure returns to OPEN.

---

## record_success

```python
record_success(self: Any)
```

Record a successful request and reset failures.

If circuit is HALF_OPEN, transitions to CLOSED.
If circuit is CLOSED, resets failure counter.

---

## state

```python
state(self: Any)
```

Get the current circuit state.

**Returns**: Current CircuitState (CLOSED, OPEN, or HALF_OPEN).

---

