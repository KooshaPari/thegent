# conflict_ttl API Reference

> **Source**: `src/thegent/integrations/conflict_ttl.py`

## ConflictRecord

Record of a tracked conflict with TTL and escalation state.

---

## ConflictTTLManager

Manages conflict TTLs with automatic escalation.

# @trace WL-250

### Methods

#### ConflictTTLManager.__init__

```python
__init__(self: Any, ttl_seconds: float, escalation_seconds: float)
```

Initialize the conflict TTL manager.

**Parameters**:

- `ttl_seconds`: Time in seconds before conflict expires (default: 24 hours)
- `escalation_seconds`: Time in seconds before escalation needed (default: 1 hour)

---

#### ConflictTTLManager.escalate

```python
escalate(self: Any, conflict_id: str)
```

Mark a conflict as escalated.

**Parameters**:

- `conflict_id`: The conflict ID to escalate

---

#### ConflictTTLManager.expired_ids

```python
expired_ids(self: Any)
```

Get all IDs of expired conflicts.

**Returns**: List of conflict IDs with age > ttl_seconds

---

#### ConflictTTLManager.is_expired

```python
is_expired(self: Any, conflict_id: str)
```

Check if a conflict has exceeded its TTL.

**Parameters**:

- `conflict_id`: The conflict ID to check

**Returns**: True if the conflict has expired, False otherwise

---

#### ConflictTTLManager.needs_escalation

```python
needs_escalation(self: Any, conflict_id: str)
```

Check if a conflict needs escalation (age > escalation_seconds but not expired).

**Parameters**:

- `conflict_id`: The conflict ID to check

**Returns**: True if escalation is needed and conflict not yet expired, False otherwise

---

#### ConflictTTLManager.register

```python
register(self: Any, conflict_id: str)
```

Register a new conflict.

**Parameters**:

- `conflict_id`: Unique identifier for the conflict

**Returns**: The created ConflictRecord

---

---

## escalate

```python
escalate(self: Any, conflict_id: str)
```

Mark a conflict as escalated.

**Parameters**:

- `conflict_id`: The conflict ID to escalate

**Raises**:

- `KeyError`: If the conflict_id is not registered

---

## expired_ids

```python
expired_ids(self: Any)
```

Get all IDs of expired conflicts.

**Returns**: List of conflict IDs with age > ttl_seconds

---

## is_expired

```python
is_expired(self: Any, conflict_id: str)
```

Check if a conflict has exceeded its TTL.

**Parameters**:

- `conflict_id`: The conflict ID to check

**Returns**: True if the conflict has expired, False otherwise

**Raises**:

- `KeyError`: If the conflict_id is not registered

---

## needs_escalation

```python
needs_escalation(self: Any, conflict_id: str)
```

Check if a conflict needs escalation (age > escalation_seconds but not expired).

**Parameters**:

- `conflict_id`: The conflict ID to check

**Returns**: True if escalation is needed and conflict not yet expired, False otherwise

**Raises**:

- `KeyError`: If the conflict_id is not registered

---

## register

```python
register(self: Any, conflict_id: str)
```

Register a new conflict.

**Parameters**:

- `conflict_id`: Unique identifier for the conflict

**Returns**: The created ConflictRecord

---

