# overrides API Reference

> **Source**: `src/thegent/governance/overrides.py`

WP-3003: Override path with TTL and revalidation (FR-011).

---

## OverrideManager

Manages temporary policy overrides.

### Methods

#### OverrideManager.__init__

```python
__init__(self, settings)
```

#### OverrideManager.apply_override

Create a new temporary override.

```python
apply_override(self, policy_id, reason, by, duration_minutes, metadata)
```

#### OverrideManager.cleanup_expired

Remove all expired overrides from disk.

```python
cleanup_expired(self)
```

#### OverrideManager.get_override

Get an active override for a policy.

```python
get_override(self, policy_id)
```

---

## PolicyOverride

An active override for a governance policy.

### Methods

#### PolicyOverride.from_dict

Create from dictionary.

```python
from_dict(cls, data)
```

#### PolicyOverride.is_active

Check if the override is still valid.

```python
is_active(self)
```

#### PolicyOverride.to_dict

Convert to dictionary.

```python
to_dict(self)
```

---

## apply_override

Create a new temporary override.

```python
apply_override(self, policy_id, reason, by, duration_minutes, metadata)
```

---

## cleanup_expired

Remove all expired overrides from disk.

```python
cleanup_expired(self)
```

---

## from_dict

Create from dictionary.

```python
from_dict(cls, data)
```

---

## get_override

Get an active override for a policy.

```python
get_override(self, policy_id)
```

---

## is_active

Check if the override is still valid.

```python
is_active(self)
```

---

## to_dict

Convert to dictionary.

```python
to_dict(self)
```

---

