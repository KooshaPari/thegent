# connector_sandbox API Reference

> **Source**: `src/thegent/integrations/connector_sandbox.py`

Connector sandbox project mode tracking and promotion.

Manages connectors in sandbox mode for testing before production promotion.

FR traceability: WL-274 (Connector Sandbox Project Mode)
# @trace WL-274

---

## ConnectorSandboxRegistry

Manages sandbox connectors and promotion to production.

### Methods

#### ConnectorSandboxRegistry.__init__

```python
__init__(self: Any)
```

Initialize the connector sandbox registry.

---

#### ConnectorSandboxRegistry.all_sandbox

```python
all_sandbox(self: Any)
```

Get all connectors currently in sandbox mode.

**Returns**: List of SandboxConnector objects in sandbox mode.

---

#### ConnectorSandboxRegistry.is_sandbox

```python
is_sandbox(self: Any, connector_id: str)
```

Check if a connector is in sandbox mode.

**Parameters**:

- `connector_id`: Connector identifier.

**Returns**: True if registered and in sandbox mode, False otherwise.

---

#### ConnectorSandboxRegistry.promote

```python
promote(self: Any, connector_id: str)
```

Promote a connector from sandbox to production mode.

**Parameters**:

- `connector_id`: Connector identifier.

---

#### ConnectorSandboxRegistry.register

```python
register(self: Any, connector_id: str, project_id: str, sandbox: bool)
```

Register a connector with sandbox mode status.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `project_id`: Associated project identifier.
- `sandbox`: Whether connector is in sandbox mode (default: True).

**Returns**: The registered SandboxConnector.

---

---

## SandboxConnector

A connector registered with sandbox mode status.

---

## all_sandbox

```python
all_sandbox(self: Any)
```

Get all connectors currently in sandbox mode.

**Returns**: List of SandboxConnector objects in sandbox mode.

---

## is_sandbox

```python
is_sandbox(self: Any, connector_id: str)
```

Check if a connector is in sandbox mode.

**Parameters**:

- `connector_id`: Connector identifier.

**Returns**: True if registered and in sandbox mode, False otherwise.

---

## promote

```python
promote(self: Any, connector_id: str)
```

Promote a connector from sandbox to production mode.

**Parameters**:

- `connector_id`: Connector identifier.

**Raises**:

- `ValueError`: If connector is not registered.

---

## register

```python
register(self: Any, connector_id: str, project_id: str, sandbox: bool)
```

Register a connector with sandbox mode status.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `project_id`: Associated project identifier.
- `sandbox`: Whether connector is in sandbox mode (default: True).

**Returns**: The registered SandboxConnector.

---

