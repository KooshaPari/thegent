# latency_tracker API Reference

> **Source**: `src/thegent/utils/routing_impl/latency_tracker.py`

GW-60: EWMA latency tracking for fastest-provider routing.

Exponential Weighted Moving Average latency per provider/model.

# @trace FR-AROUTE-060

---

## EWMAConfig

Configuration for the EWMA latency tracker.

---

## EWMALatencyTracker

Thread-safe EWMA latency tracker keyed by (provider, model).

Records latency samples and maintains an exponential weighted moving
average per provider+model combination. Used for fastest-provider routing.

### Methods

#### EWMALatencyTracker.__init__

```python
__init__(self: Any, config: Any)
```

---

#### EWMALatencyTracker.get_latency

```python
get_latency(self: Any, provider: str, model: str)
```

Return the current EWMA latency for a provider+model pair.

Returns initial_latency_ms if no data has been recorded.

**Parameters**:

- `provider`: Provider identifier.
- `model`: Model identifier.

**Returns**: EWMA latency in milliseconds.

---

#### EWMALatencyTracker.rank_by_latency

```python
rank_by_latency(self: Any, candidates: list[tuple[(str, str)]])
```

Rank candidates ascending by EWMA latency (fastest first).

**Parameters**:

- `candidates`: List of (provider, model) tuples to rank.

**Returns**: New list sorted with lowest EWMA latency first.

---

#### EWMALatencyTracker.record

```python
record(self: Any, provider: str, model: str, latency_ms: float)
```

Record a latency sample and update the EWMA.

EWMA update: new = alpha * sample + (1 - alpha) * old_ewma

**Parameters**:

- `provider`: Provider identifier (e.g. "openai").
- `model`: Model identifier (e.g. "gpt-4o").
- `latency_ms`: Observed latency in milliseconds.

---

---

## LatencyRecord

EWMA latency record for a single provider+model pair.

---

## get_latency

```python
get_latency(self: Any, provider: str, model: str)
```

Return the current EWMA latency for a provider+model pair.

Returns initial_latency_ms if no data has been recorded.

**Parameters**:

- `provider`: Provider identifier.
- `model`: Model identifier.

**Returns**: EWMA latency in milliseconds.

---

## get_latency_tracker

Return the process-global EWMALatencyTracker singleton.

---

## rank_by_latency

```python
rank_by_latency(self: Any, candidates: list[tuple[(str, str)]])
```

Rank candidates ascending by EWMA latency (fastest first).

**Parameters**:

- `candidates`: List of (provider, model) tuples to rank.

**Returns**: New list sorted with lowest EWMA latency first.

---

## record

```python
record(self: Any, provider: str, model: str, latency_ms: float)
```

Record a latency sample and update the EWMA.

EWMA update: new = alpha * sample + (1 - alpha) * old_ewma

**Parameters**:

- `provider`: Provider identifier (e.g. "openai").
- `model`: Model identifier (e.g. "gpt-4o").
- `latency_ms`: Observed latency in milliseconds.

---

## reset_latency_tracker

Reset the singleton (for testing only).

---

