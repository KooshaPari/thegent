# slo_trend API Reference

> **Source**: `src/thegent/governance/slo_trend.py`

SLO trend serialization for WL-135 B90-W2-F4.

Provides SloTrend, load_trend, and serialize_trend for reading and
serializing windowed SLO metric history from the .quality/slo-metrics.jsonl file.

Fail-fast: all functions raise loudly if the file is missing or malformed.
No fallbacks, no silent errors, no legacy compatibility shims.

# @trace WL-135 B90-W2-F4

---

## SloTrend

Windowed collection of SLO metric snapshots.

---

## load_trend

```python
load_trend(path: Any, window_days: int)
```

Read JSONL from path, filter to last window_days days, return SloTrend.

**Raises**:

- `FileNotFoundError`: if the JSONL file does not exist.
- `ValueError`: if any line is malformed or missing required fields.

---

## serialize_trend

```python
serialize_trend(trend: SloTrend)
```

Return a JSON string representation of the SloTrend.

The output is a single JSON object with:
  - window_days: int
  - generated_at: str
  - metrics: list of metric dicts

**Raises**:

- `TypeError`: if trend contains un-serializable fields (fail-fast).

---

