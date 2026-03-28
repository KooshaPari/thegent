# sla_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/sla_adapter.py`

SLA and error budget adapter for workstream autosync.

Handles SLA evaluation, error budget tracking, and connector health monitoring.

---

## SLAAdapter

Adapter for SLA evaluation and error budget operations.

### Methods

#### SLAAdapter.__init__

```python
__init__(self: Any, config: Any, error_budget: ErrorBudgetTracker)
```

---

#### SLAAdapter.evaluate_slo_state

```python
evaluate_slo_state(self: Any, snapshot_age_seconds: Any)
```

Evaluate current SLO state and return alerts.

---

#### SLAAdapter.get_connector_error_budget

```python
get_connector_error_budget(self: Any, connector: str)
```

Get or create error budget for connector.

---

#### SLAAdapter.record_connector_latency

```python
record_connector_latency(self: Any, connector: str, duration_seconds: float)
```

Record connector latency metric.

---

---

## evaluate_slo_state

```python
evaluate_slo_state(self: Any, snapshot_age_seconds: Any)
```

Evaluate current SLO state and return alerts.

---

## get_connector_error_budget

```python
get_connector_error_budget(self: Any, connector: str)
```

Get or create error budget for connector.

---

## record_connector_latency

```python
record_connector_latency(self: Any, connector: str, duration_seconds: float)
```

Record connector latency metric.

---

