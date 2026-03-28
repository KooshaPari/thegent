# virtual_keys API Reference

> **Source**: `src/thegent/utils/routing_impl/virtual_keys.py`

GW-28: Virtual key system — per-key budget, rate, and model restrictions.

Each virtual key maps to a set of allowed models, rate limits, and a budget.
Keys are resolved from the Authorization header (Bearer sk-tg-...).

# @trace FR-KEYS-028

---

## VirtualKeyConfig

Configuration for a single virtual key.

---

## VirtualKeyStore

Thread-safe store for VirtualKeyConfig objects, keyed by key_id.

### Methods

#### VirtualKeyStore.__init__

```python
__init__(self: Any)
```

---

#### VirtualKeyStore.delete

```python
delete(self: Any, key_id: str)
```

Remove the key with key_id. Returns True if it existed, False otherwise.

---

#### VirtualKeyStore.get

```python
get(self: Any, key_id: str)
```

Return the VirtualKeyConfig for key_id, or None if not found.

---

#### VirtualKeyStore.list_keys

```python
list_keys(self: Any, owner_id: Any)
```

Return all registered keys, optionally filtered by owner_id.

---

#### VirtualKeyStore.register

```python
register(self: Any, config: VirtualKeyConfig)
```

Register or replace a virtual key configuration.

---

---

## VirtualKeyValidationResult

Result of validating a virtual key against a request.

---

## VirtualKeyValidator

Validates virtual keys against a request's model and store state.

### Methods

#### VirtualKeyValidator.validate_key

```python
validate_key(self: Any, key_id: str, model: str, store: Any)
```

Validate key_id for the requested model.

Checks:
1. Key exists in the store.
2. If allowed_models is non-empty, model must be in the list.

**Parameters**:

- `key_id`: The virtual key identifier (e.g. "sk-tg-abc123").
- `model`: The model being requested (e.g. "gpt-4o").
- `store`: The VirtualKeyStore to look up the key in. Defaults to the
global singleton.

**Returns**: VirtualKeyValidationResult with allowed, reason, and key_config.

---

---

## delete

```python
delete(self: Any, key_id: str)
```

Remove the key with key_id. Returns True if it existed, False otherwise.

---

## extract_virtual_key_id

```python
extract_virtual_key_id(authorization: Any)
```

Extract key_id from 'Bearer sk-tg-...' Authorization header.

Returns None if not a virtual key (doesn't start with 'sk-tg-').

**Parameters**:

- `authorization`: The raw Authorization header value, e.g.
``"Bearer sk-tg-abc123"``.

**Returns**: The token string (e.g. ``"sk-tg-abc123"``) when it is a virtual key,
or ``None`` otherwise.

---

## get

```python
get(self: Any, key_id: str)
```

Return the VirtualKeyConfig for key_id, or None if not found.

---

## get_key_store

Return the process-global VirtualKeyStore singleton.

---

## list_keys

```python
list_keys(self: Any, owner_id: Any)
```

Return all registered keys, optionally filtered by owner_id.

---

## register

```python
register(self: Any, config: VirtualKeyConfig)
```

Register or replace a virtual key configuration.

---

## reset_key_store

Reset the singleton (for testing only).

---

## validate_key

```python
validate_key(self: Any, key_id: str, model: str, store: Any)
```

Validate key_id for the requested model.

Checks:
1. Key exists in the store.
2. If allowed_models is non-empty, model must be in the list.

**Parameters**:

- `key_id`: The virtual key identifier (e.g. "sk-tg-abc123").
- `model`: The model being requested (e.g. "gpt-4o").
- `store`: The VirtualKeyStore to look up the key in. Defaults to the
global singleton.

**Returns**: VirtualKeyValidationResult with allowed, reason, and key_config.

---

