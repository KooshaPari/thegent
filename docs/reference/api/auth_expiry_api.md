# auth_expiry API Reference

> **Source**: `src/thegent/integrations/auth_expiry.py`

Auth token expiry detection for connectors.

# @trace WL-241

---

## AuthExpiryDetector

Detects and monitors auth token expiry.

### Methods

#### AuthExpiryDetector.__init__

```python
__init__(self: Any, expiring_soon_threshold_hours: float)
```

Initialize the auth expiry detector.

**Parameters**:

- `expiring_soon_threshold_hours`: Hours before expiry to consider "expiring soon".

---

#### AuthExpiryDetector.detect_expiry

```python
detect_expiry(self: Any, token_info: dict[(str, Any)])
```

Detect the expiry status of a token.

**Parameters**:

- `token_info`: Token information dictionary. May contain:
- expires_at (datetime): When the token expires
- expiry_timestamp (int): Unix timestamp of expiry
- ttl (int): Time to live in seconds
- expires_in (int): Seconds until expiry

**Returns**: AuthExpiryInfo with status and metadata.

---

#### AuthExpiryDetector.is_expired

```python
is_expired(self: Any, token_info: dict[(str, Any)])
```

Quick check if token is expired.

**Parameters**:

- `token_info`: Token information dictionary.

**Returns**: True if token is expired, False otherwise.

---

#### AuthExpiryDetector.is_expiring_soon

```python
is_expiring_soon(self: Any, token_info: dict[(str, Any)])
```

Quick check if token is expiring soon.

**Parameters**:

- `token_info`: Token information dictionary.

**Returns**: True if token is expiring within threshold, False otherwise.

---

---

## AuthExpiryInfo

Information about token expiry.

---

## ExpiryStatus

Status of token expiry.

**Inherits from**: `str, Enum`

---

## detect_expiry

```python
detect_expiry(self: Any, token_info: dict[(str, Any)])
```

Detect the expiry status of a token.

**Parameters**:

- `token_info`: Token information dictionary. May contain:
- expires_at (datetime): When the token expires
- expiry_timestamp (int): Unix timestamp of expiry
- ttl (int): Time to live in seconds
- expires_in (int): Seconds until expiry

**Returns**: AuthExpiryInfo with status and metadata.

**Raises**:

- `ValueError`: If token_info has no expiry information.

---

## is_expired

```python
is_expired(self: Any, token_info: dict[(str, Any)])
```

Quick check if token is expired.

**Parameters**:

- `token_info`: Token information dictionary.

**Returns**: True if token is expired, False otherwise.

---

## is_expiring_soon

```python
is_expiring_soon(self: Any, token_info: dict[(str, Any)])
```

Quick check if token is expiring soon.

**Parameters**:

- `token_info`: Token information dictionary.

**Returns**: True if token is expiring within threshold, False otherwise.

---

