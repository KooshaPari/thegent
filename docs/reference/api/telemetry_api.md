# telemetry API Reference

> **Source**: `src/thegent/ports/driven/telemetry.py`

TelemetryPort: Interface for logging and metrics.

---

## TelemetryPort

Port interface for logging and metrics collection.

**Inherits from**: `Protocol`

### Methods

#### TelemetryPort.log_debug

```python
log_debug(self: Any, event: str)
```

Log a debug event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

#### TelemetryPort.log_error

```python
log_error(self: Any, event: str)
```

Log an error event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

#### TelemetryPort.log_info

```python
log_info(self: Any, event: str)
```

Log an informational event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

#### TelemetryPort.log_warning

```python
log_warning(self: Any, event: str)
```

Log a warning event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

#### TelemetryPort.record_metric

```python
record_metric(self: Any, metric_name: str, value: float)
```

Record a numerical metric.

**Parameters**:

- `metric_name`: Name of the metric.
- `value`: Metric value.
- `**kwargs`: Additional tags/labels.

---

---

## log_debug

```python
log_debug(self: Any, event: str)
```

Log a debug event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

## log_error

```python
log_error(self: Any, event: str)
```

Log an error event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

## log_info

```python
log_info(self: Any, event: str)
```

Log an informational event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

## log_warning

```python
log_warning(self: Any, event: str)
```

Log a warning event.

**Parameters**:

- `event`: Event name or message.
- `**kwargs`: Additional context data.

---

## record_metric

```python
record_metric(self: Any, metric_name: str, value: float)
```

Record a numerical metric.

**Parameters**:

- `metric_name`: Name of the metric.
- `value`: Metric value.
- `**kwargs`: Additional tags/labels.

---

