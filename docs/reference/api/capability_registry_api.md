# capability_registry API Reference

> **Source**: `src/thegent/contracts/capability_registry.py`

WP-10002: Capability registry service.

Authoritative source for available capabilities, versions, and trust levels.

---

## Capability

A registered system capability.

---

## CapabilityRegistry

Central registry for managing and querying system capabilities.

### Methods

#### CapabilityRegistry.__init__

```python
__init__(self)
```

#### CapabilityRegistry.get_capability

Return capability metadata if found.

```python
get_capability(self, cap_id)
```

#### CapabilityRegistry.is_supported

Check if a capability and version are supported.

```python
is_supported(self, cap_id, version)
```

#### CapabilityRegistry.list_capabilities

List all registered capabilities.

```python
list_capabilities(self)
```

#### CapabilityRegistry.register

Register a new capability.

```python
register(self, cap)
```

---

## get_capability

Return capability metadata if found.

```python
get_capability(self, cap_id)
```

---

## is_supported

Check if a capability and version are supported.

```python
is_supported(self, cap_id, version)
```

---

## list_capabilities

List all registered capabilities.

```python
list_capabilities(self)
```

---

## register

Register a new capability.

```python
register(self, cap)
```

---

