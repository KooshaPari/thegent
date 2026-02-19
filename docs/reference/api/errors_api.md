# errors API Reference

> **Source**: `src/thegent/errors.py`

Production error handling framework for thegent.

---

## ConfigError

Raised when there is a configuration-related failure.

**Inherits from**: `ThegentError`

### Methods

#### ConfigError.__init__

```python
__init__(self, message, remediation_hint)
```

---

## MCPError

Raised when an MCP-related failure occurs.

**Inherits from**: `ThegentError`

### Methods

#### MCPError.__init__

```python
__init__(self, message, remediation_hint)
```

---

## ProviderError

Raised when an AI provider (Anthropic, Google, etc.) returns an error.

**Inherits from**: `ThegentError`

### Methods

#### ProviderError.__init__

```python
__init__(self, message, remediation_hint)
```

---

## ThegentError

Base class for all errors in thegent.

Attributes:
    message: The error message.
    remediation_hint: A human-readable hint on how to fix the error.

**Inherits from**: `Exception`

### Methods

#### ThegentError.__init__

```python
__init__(self, message, remediation_hint)
```

---

## get_install_hint

Get platform-specific installation hint for a missing tool.

```python
get_install_hint(tool)
```

---

