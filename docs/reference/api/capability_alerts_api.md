# capability_alerts API Reference

> **Source**: `src/thegent/integrations/capability_alerts.py`

Capability mismatch detection for connectors.

Detects when a connector lacks required capabilities for sync operations
and generates alerts.

FR traceability: WL-305 (Capability Mismatch Alerts)

---

## CapabilityMismatchDetector

Detects capability mismatches between connectors and sync requirements.

### Methods

#### CapabilityMismatchDetector.__init__

```python
__init__(self: Any, required_capabilities: list[str])
```

Initialize the detector.

**Parameters**:

- `required_capabilities`: Capabilities required by the sync.

---

#### CapabilityMismatchDetector.check_connector

```python
check_connector(self: Any, connector_name: str, available_capabilities: list[str])
```

Check a connector for missing capabilities.

**Parameters**:

- `connector_name`: Name of the connector.
- `available_capabilities`: Capabilities the connector has.

**Returns**: List of missing capability names (empty if all present).

---

#### CapabilityMismatchDetector.generate_alert

```python
generate_alert(self: Any, connector_name: str, missing: list[str])
```

Generate an alert for capability mismatch.

**Parameters**:

- `connector_name`: Name of the connector.
- `missing`: List of missing capabilities.

**Returns**: Alert dict with keys: connector, missing, severity, timestamp.

---

#### CapabilityMismatchDetector.is_compatible

```python
is_compatible(self: Any, connector_name: str, available_capabilities: list[str])
```

Check if a connector has all required capabilities.

**Parameters**:

- `connector_name`: Name of the connector.
- `available_capabilities`: Capabilities the connector has.

**Returns**: True if all required capabilities are present.

---

---

## ConnectorCapabilityDiscovery

Runtime connector capability discovery with explicit cache refresh control.

### Methods

#### ConnectorCapabilityDiscovery.__init__

```python
__init__(self: Any, probe: Callable[(Any, list[str])])
```

---

#### ConnectorCapabilityDiscovery.discover

```python
discover(self: Any, connector: str)
```

Return discovered capabilities for the connector.

---

---

## ConnectorSLAEvaluator

Evaluate connector latency/error budget compliance against SLA thresholds.

### Methods

#### ConnectorSLAEvaluator.evaluate

```python
evaluate(self: Any)
```

Return SLA compliance payload and explicit breach reasons.

---

---

## ConnectorSLAThresholds

SLA thresholds for a connector.

---

## check_connector

```python
check_connector(self: Any, connector_name: str, available_capabilities: list[str])
```

Check a connector for missing capabilities.

**Parameters**:

- `connector_name`: Name of the connector.
- `available_capabilities`: Capabilities the connector has.

**Returns**: List of missing capability names (empty if all present).

**Raises**:

- `ValueError`: If inputs are invalid.

---

## discover

```python
discover(self: Any, connector: str)
```

Return discovered capabilities for the connector.

---

## evaluate

```python
evaluate(self: Any)
```

Return SLA compliance payload and explicit breach reasons.

---

## generate_alert

```python
generate_alert(self: Any, connector_name: str, missing: list[str])
```

Generate an alert for capability mismatch.

**Parameters**:

- `connector_name`: Name of the connector.
- `missing`: List of missing capabilities.

**Returns**: Alert dict with keys: connector, missing, severity, timestamp.

**Raises**:

- `ValueError`: If inputs are invalid.

---

## is_compatible

```python
is_compatible(self: Any, connector_name: str, available_capabilities: list[str])
```

Check if a connector has all required capabilities.

**Parameters**:

- `connector_name`: Name of the connector.
- `available_capabilities`: Capabilities the connector has.

**Returns**: True if all required capabilities are present.

**Raises**:

- `ValueError`: If inputs are invalid.

---

