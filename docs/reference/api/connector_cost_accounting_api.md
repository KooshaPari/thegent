# connector_cost_accounting API Reference

> **Source**: `src/thegent/integrations/connector_cost_accounting.py`

Per-connector cost accounting for sync budgeting.

# @trace WL-297

---

## ConnectorCostLedger

In-memory ledger of per-connector usage/cost metrics.

### Methods

#### ConnectorCostLedger.__init__

```python
__init__(self: Any)
```

---

#### ConnectorCostLedger.record

```python
record(self: Any)
```

---

#### ConnectorCostLedger.summary_by_connector

```python
summary_by_connector(self: Any)
```

---

#### ConnectorCostLedger.total_cost

```python
total_cost(self: Any)
```

---

---

## ConnectorCostSummary

Aggregated connector cost/usage summary.

---

## ConnectorUsageEvent

Single connector usage event.

---

## record

```python
record(self: Any) -> ConnectorUsageEvent
```

---

## summary_by_connector

```python
summary_by_connector(self: Any) -> list[ConnectorCostSummary]
```

---

## total_cost

```python
total_cost(self: Any) -> float
```

---

