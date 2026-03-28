# metrics_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/metrics_adapter.py`

Metrics and reporting adapter for workstream autosync.

Handles Prometheus metrics export, cycle metrics, and change digest.

---

## MetricsAdapter

Adapter for metrics and reporting operations.

### Methods

#### MetricsAdapter.__init__

```python
__init__(self: Any, config: Any)
```

---

#### MetricsAdapter.append_cycle_metrics

```python
append_cycle_metrics(self: Any, cycle_data: dict[(str, Any)])
```

Append cycle metrics to JSONL file.

---

#### MetricsAdapter.flush_prometheus_metrics

```python
flush_prometheus_metrics(self: Any)
```

Export Prometheus metrics to file.

---

#### MetricsAdapter.get_change_digest_path

```python
get_change_digest_path(self: Any)
```

---

#### MetricsAdapter.record_connector_latency

```python
record_connector_latency(self: Any, connector: str, duration_seconds: float)
```

Record connector latency metric.

---

#### MetricsAdapter.refresh_change_digest

```python
refresh_change_digest(self: Any, current_digest: dict[(str, Any)])
```

Refresh hourly change digest.

---

---

## append_cycle_metrics

```python
append_cycle_metrics(self: Any, cycle_data: dict[(str, Any)])
```

Append cycle metrics to JSONL file.

---

## flush_prometheus_metrics

```python
flush_prometheus_metrics(self: Any)
```

Export Prometheus metrics to file.

---

## get_change_digest_path

```python
get_change_digest_path(self: Any) -> Path
```

---

## record_connector_latency

```python
record_connector_latency(self: Any, connector: str, duration_seconds: float)
```

Record connector latency metric.

---

## refresh_change_digest

```python
refresh_change_digest(self: Any, current_digest: dict[(str, Any)])
```

Refresh hourly change digest.

---

