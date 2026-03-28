# connector_capability_discovery API Reference

> **Source**: `src/thegent/integrations/connector_capability_discovery.py`

Connector capability discovery and probing system.

Manages connector capabilities and feature flags for runtime behavior gates.

FR traceability: WL-228 (Connector Capability Discovery)

---

## ConnectorCapability

Represents a connector and its capabilities.

# @trace WL-228

---

## ConnectorCapabilityRegistry

Registry for managing connector capabilities and feature flags.

# @trace WL-228

### Methods

#### ConnectorCapabilityRegistry.__init__

```python
__init__(self: Any)
```

Initialize the registry with empty state.

---

#### ConnectorCapabilityRegistry.connectors_with

```python
connectors_with(self: Any, capability: str)
```

Get all connectors that have a specific capability.

**Parameters**:

- `capability`: Capability to search for.

**Returns**: List of connector IDs that have the capability.

---

#### ConnectorCapabilityRegistry.get

```python
get(self: Any, connector_id: str)
```

Get capabilities for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.

**Returns**: ConnectorCapability with the connector's details.

---

#### ConnectorCapabilityRegistry.has_capability

```python
has_capability(self: Any, connector_id: str, capability: str)
```

Check if a connector has a specific capability.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `capability`: Capability to check for.

**Returns**: True if connector has the capability, False otherwise.

---

#### ConnectorCapabilityRegistry.register

```python
register(self: Any, connector_id: str, capabilities: list[str])
```

Register a connector with its capabilities.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `capabilities`: List of capability strings.

**Returns**: ConnectorCapability with the registered details.

---

---

## connectors_with

```python
connectors_with(self: Any, capability: str)
```

Get all connectors that have a specific capability.

**Parameters**:

- `capability`: Capability to search for.

**Returns**: List of connector IDs that have the capability.

---

## get

```python
get(self: Any, connector_id: str)
```

Get capabilities for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.

**Returns**: ConnectorCapability with the connector's details.

**Raises**:

- `KeyError`: If connector is not registered.

---

## has_capability

```python
has_capability(self: Any, connector_id: str, capability: str)
```

Check if a connector has a specific capability.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `capability`: Capability to check for.

**Returns**: True if connector has the capability, False otherwise.

---

## register

```python
register(self: Any, connector_id: str, capabilities: list[str])
```

Register a connector with its capabilities.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `capabilities`: List of capability strings.

**Returns**: ConnectorCapability with the registered details.

**Raises**:

- `ValueError`: If connector is already registered.

---

