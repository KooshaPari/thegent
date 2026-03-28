# key_rotation API Reference

> **Source**: `src/thegent/governance/key_rotation.py`

WL-051: API key rotation monitoring and webhook notification.

Implements:
  - ApiKeyRecord: key metadata with expiry tracking
  - KeyRotationMonitor: warns when keys expire within 7 days
  - KeyRotationWebhook: posts rotation events to a configurable URL (httpx)

---

## ApiKeyRecord

Persistent metadata for an API key (WL-051).

**Inherits from**: `BaseModel`

### Methods

#### ApiKeyRecord.days_until_expiry

```python
days_until_expiry(self: Any)
```

Return days remaining until expiry (negative = already expired).

---

#### ApiKeyRecord.expires_at_dt

```python
expires_at_dt(self: Any)
```

---

#### ApiKeyRecord.is_expired

```python
is_expired(self: Any)
```

---

#### ApiKeyRecord.is_expiring_soon

```python
is_expiring_soon(self: Any, warn_days: int)
```

Return True if the key expires within `warn_days` days.

---

---

## KeyRegistry

Persists ApiKeyRecord entries in a JSONL file (WL-051).

### Methods

#### KeyRegistry.__init__

```python
__init__(self: Any, registry_path: Any)
```

---

#### KeyRegistry.add

```python
add(self: Any, record: ApiKeyRecord)
```

Append a key record. Raises ValueError if key_id already exists.

---

#### KeyRegistry.get

```python
get(self: Any, key_id: str)
```

---

#### KeyRegistry.list_all

```python
list_all(self: Any)
```

---

#### KeyRegistry.update

```python
update(self: Any, updated: ApiKeyRecord)
```

Replace the record with the same key_id. Raises KeyError if not found.

---

---

## KeyRotationMonitor

Monitors API keys and emits warnings for keys expiring within the threshold (WL-051).

Usage::

    monitor = KeyRotationMonitor(registry)
    warnings = monitor.check_all()
    for w in warnings:
        print(w.to_dict())

### Methods

#### KeyRotationMonitor.__init__

```python
__init__(self: Any, registry: KeyRegistry, warn_days: int)
```

---

#### KeyRotationMonitor.check_all

```python
check_all(self: Any)
```

Return warnings for all keys expiring within warn_days (or already expired).

---

#### KeyRotationMonitor.check_provider

```python
check_provider(self: Any, provider: str)
```

Return warnings for keys of a specific provider.

---

---

## KeyRotationWarning

Structured warning emitted by KeyRotationMonitor.

### Methods

#### KeyRotationWarning.__init__

```python
__init__(self: Any, record: ApiKeyRecord, warn_days: int)
```

---

#### KeyRotationWarning.to_dict

```python
to_dict(self: Any)
```

---

---

## KeyRotationWebhook

Posts key rotation events to a configurable URL via httpx (WL-051).

The webhook payload format::

    {
        "event": "key_rotation",
        "key_id": "...",
        "provider": "...",
        "rotated_at": "...",
        "prev_expires_at": "...",
        "new_expires_at": "...",
    }

### Methods

#### KeyRotationWebhook.__init__

```python
__init__(self: Any, webhook_url: str, registry: KeyRegistry, timeout_seconds: float)
```

---

#### KeyRotationWebhook.build_rotation_payload

```python
build_rotation_payload(self: Any, key_id: str, new_expires_at: str)
```

Build the webhook payload without executing the rotation (for inspection/testing).

---

#### KeyRotationWebhook.rotate

```python
rotate(self: Any)
```

Record a key rotation and notify the webhook.

Updates the key registry with new_expires_at, then POSTs a rotation
event to webhook_url.  Raises httpx.HTTPError on non-2xx response.

Returns the webhook response payload (or empty dict if dry-run with
no URL set).

---

---

## add

```python
add(self: Any, record: ApiKeyRecord)
```

Append a key record. Raises ValueError if key_id already exists.

---

## build_rotation_payload

```python
build_rotation_payload(self: Any, key_id: str, new_expires_at: str)
```

Build the webhook payload without executing the rotation (for inspection/testing).

---

## check_all

```python
check_all(self: Any)
```

Return warnings for all keys expiring within warn_days (or already expired).

---

## check_provider

```python
check_provider(self: Any, provider: str)
```

Return warnings for keys of a specific provider.

---

## days_until_expiry

```python
days_until_expiry(self: Any)
```

Return days remaining until expiry (negative = already expired).

---

## expires_at_dt

```python
expires_at_dt(self: Any) -> datetime
```

---

## get

```python
get(self: Any, key_id: str) -> ApiKeyRecord
```

---

## is_expired

```python
is_expired(self: Any) -> bool
```

---

## is_expiring_soon

```python
is_expiring_soon(self: Any, warn_days: int)
```

Return True if the key expires within `warn_days` days.

---

## list_all

```python
list_all(self: Any) -> list[ApiKeyRecord]
```

---

## make_expiry_utc

```python
make_expiry_utc(days_from_now: int)
```

Return an ISO-8601 UTC datetime string for N days from now.

---

## rotate

```python
rotate(self: Any)
```

Record a key rotation and notify the webhook.

Updates the key registry with new_expires_at, then POSTs a rotation
event to webhook_url.  Raises httpx.HTTPError on non-2xx response.

Returns the webhook response payload (or empty dict if dry-run with
no URL set).

---

## to_dict

```python
to_dict(self: Any) -> dict[(str, Any)]
```

---

## update

```python
update(self: Any, updated: ApiKeyRecord)
```

Replace the record with the same key_id. Raises KeyError if not found.

---

