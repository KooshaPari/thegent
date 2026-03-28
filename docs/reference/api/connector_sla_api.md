# connector_sla API Reference

> **Source**: `src/thegent/integrations/connector_sla.py`

Connector SLA tracking and breach detection.

Tracks connector SLA targets and actual performance, emits alerts on breaches.

FR traceability: WL-233 (Connector SLA Tracking)

---

## ConnectorSLATracker

Tracks connector SLA targets and actual performance.

# @trace WL-233

### Methods

#### ConnectorSLATracker.__init__

```python
__init__(self: Any)
```

Initialize the tracker with empty records.

---

#### ConnectorSLATracker.all_records

```python
all_records(self: Any)
```

Get all SLA records.

**Returns**: List of all SLARecord entries in the tracker.

---

#### ConnectorSLATracker.breached

```python
breached(self: Any)
```

Get all currently breached SLA records.

**Returns**: List of SLARecord entries where actual > target.

---

#### ConnectorSLATracker.is_breached

```python
is_breached(self: Any, connector_id: str)
```

Check if a connector's SLA is currently breached.

**Parameters**:

- `connector_id`: Unique connector identifier.

**Returns**: True if actual > target, False if actual <= target or not recorded yet.

---

#### ConnectorSLATracker.record_actual

```python
record_actual(self: Any, connector_id: str, actual_ms: float)
```

Record actual measured latency for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `actual_ms`: Actual measured latency in milliseconds.

---

#### ConnectorSLATracker.set_target

```python
set_target(self: Any, connector_id: str, target_ms: float)
```

Set or update the SLA target for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `target_ms`: Target latency in milliseconds.

**Returns**: The SLARecord with the target set.

---

---

## SLARecord

Represents a connector SLA record.

# @trace WL-233

---

## all_records

```python
all_records(self: Any)
```

Get all SLA records.

**Returns**: List of all SLARecord entries in the tracker.

---

## breached

```python
breached(self: Any)
```

Get all currently breached SLA records.

**Returns**: List of SLARecord entries where actual > target.

---

## is_breached

```python
is_breached(self: Any, connector_id: str)
```

Check if a connector's SLA is currently breached.

**Parameters**:

- `connector_id`: Unique connector identifier.

**Returns**: True if actual > target, False if actual <= target or not recorded yet.

**Raises**:

- `KeyError`: If connector is not registered.

---

## record_actual

```python
record_actual(self: Any, connector_id: str, actual_ms: float)
```

Record actual measured latency for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `actual_ms`: Actual measured latency in milliseconds.

**Raises**:

- `ValueError`: If connector not registered or actual_ms is negative.
- `KeyError`: If connector has not had a target set yet.

---

## set_target

```python
set_target(self: Any, connector_id: str, target_ms: float)
```

Set or update the SLA target for a connector.

**Parameters**:

- `connector_id`: Unique connector identifier.
- `target_ms`: Target latency in milliseconds.

**Returns**: The SLARecord with the target set.

**Raises**:

- `ValueError`: If target_ms is not positive.

---

