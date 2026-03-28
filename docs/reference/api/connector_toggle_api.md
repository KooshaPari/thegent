# connector_toggle API Reference

> **Source**: `src/thegent/integrations/connector_toggle.py`

Runtime connector enable/disable toggle controls.

Manages a registry of connectors with enable/disable state for runtime control
of connector activation.

FR traceability: WL-306 (Runtime Connector Toggle Controls)

---

## ConnectorToggleRegistry

Registry for managing connector enabled/disabled states at runtime.

### Methods

#### ConnectorToggleRegistry.__init__

```python
__init__(self: Any)
```

Initialize the registry with empty state.

---

#### ConnectorToggleRegistry.disable

```python
disable(self: Any, connector: str)
```

Disable a connector.

**Parameters**:

- `connector`: Name of the connector.

---

#### ConnectorToggleRegistry.enable

```python
enable(self: Any, connector: str)
```

Enable a connector.

**Parameters**:

- `connector`: Name of the connector.

---

#### ConnectorToggleRegistry.is_enabled

```python
is_enabled(self: Any, connector: str)
```

Check if a connector is enabled.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: True if connector is registered and enabled, False otherwise.

---

#### ConnectorToggleRegistry.list_all

```python
list_all(self: Any)
```

Get a copy of the entire registry.

**Returns**: Dictionary mapping connector names to enabled state.

---

#### ConnectorToggleRegistry.register

```python
register(self: Any, connector: str, enabled: bool)
```

Register a connector with initial enabled state.

**Parameters**:

- `connector`: Name of the connector.
- `enabled`: Whether the connector starts enabled (default: True).

---

#### ConnectorToggleRegistry.toggle

```python
toggle(self: Any, connector: str)
```

Toggle the state of a connector.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: The new state (True if now enabled, False if now disabled).

---

---

## disable

```python
disable(self: Any, connector: str)
```

Disable a connector.

**Parameters**:

- `connector`: Name of the connector.

**Raises**:

- `ValueError`: If connector is not registered.

---

## enable

```python
enable(self: Any, connector: str)
```

Enable a connector.

**Parameters**:

- `connector`: Name of the connector.

**Raises**:

- `ValueError`: If connector is not registered.

---

## is_enabled

```python
is_enabled(self: Any, connector: str)
```

Check if a connector is enabled.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: True if connector is registered and enabled, False otherwise.

---

## list_all

```python
list_all(self: Any)
```

Get a copy of the entire registry.

**Returns**: Dictionary mapping connector names to enabled state.

---

## register

```python
register(self: Any, connector: str, enabled: bool)
```

Register a connector with initial enabled state.

**Parameters**:

- `connector`: Name of the connector.
- `enabled`: Whether the connector starts enabled (default: True).

**Raises**:

- `ValueError`: If connector is already registered.

---

## toggle

```python
toggle(self: Any, connector: str)
```

Toggle the state of a connector.

**Parameters**:

- `connector`: Name of the connector.

**Returns**: The new state (True if now enabled, False if now disabled).

**Raises**:

- `ValueError`: If connector is not registered.

---

