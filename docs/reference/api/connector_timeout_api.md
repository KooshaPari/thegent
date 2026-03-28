# connector_timeout API Reference

> **Source**: `src/thegent/integrations/connector_timeout.py`

Per-connector timeout controls.

Manages per-connector timeout configurations for reliable request handling.

# @trace WL-193

---

## ConnectorTimeoutConfig

Configuration for connector timeout.

---

## ConnectorTimeoutRegistry

Registry for per-connector timeout configurations.

### Methods

#### ConnectorTimeoutRegistry.__init__

```python
__init__(self: Any, default_timeout: float)
```

Initialize the timeout registry.

**Parameters**:

- `default_timeout`: Default timeout in seconds for all connectors.

---

#### ConnectorTimeoutRegistry.all_configs

```python
all_configs(self: Any)
```

Get all configured timeouts.

**Returns**: List of ConnectorTimeoutConfig for all connectors with custom timeouts.

---

#### ConnectorTimeoutRegistry.get_timeout

```python
get_timeout(self: Any, connector_id: str)
```

Get the timeout for a connector.

**Parameters**:

- `connector_id`: The connector identifier.

**Returns**: Timeout in seconds. Returns default if not explicitly configured.

---

#### ConnectorTimeoutRegistry.remove

```python
remove(self: Any, connector_id: str)
```

Remove custom timeout configuration for a connector.

After removal, the connector will use the default timeout.

**Parameters**:

- `connector_id`: The connector identifier.

---

#### ConnectorTimeoutRegistry.set_timeout

```python
set_timeout(self: Any, connector_id: str, timeout_seconds: float)
```

Set the timeout for a specific connector.

**Parameters**:

- `connector_id`: The connector identifier.
- `timeout_seconds`: Timeout in seconds.

---

---

## all_configs

```python
all_configs(self: Any)
```

Get all configured timeouts.

**Returns**: List of ConnectorTimeoutConfig for all connectors with custom timeouts.

---

## get_timeout

```python
get_timeout(self: Any, connector_id: str)
```

Get the timeout for a connector.

**Parameters**:

- `connector_id`: The connector identifier.

**Returns**: Timeout in seconds. Returns default if not explicitly configured.

---

## remove

```python
remove(self: Any, connector_id: str)
```

Remove custom timeout configuration for a connector.

After removal, the connector will use the default timeout.

**Parameters**:

- `connector_id`: The connector identifier.

---

## set_timeout

```python
set_timeout(self: Any, connector_id: str, timeout_seconds: float)
```

Set the timeout for a specific connector.

**Parameters**:

- `connector_id`: The connector identifier.
- `timeout_seconds`: Timeout in seconds.

**Raises**:

- `ValueError`: If timeout_seconds <= 0.

---

