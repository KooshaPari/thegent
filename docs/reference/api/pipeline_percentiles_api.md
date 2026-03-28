# pipeline_percentiles API Reference

> **Source**: `src/thegent/integrations/pipeline_percentiles.py`

Pipeline stage percentile tracking for observability.

Tracks execution duration of pipeline stages and computes percentiles (p50, p95, p99)
for performance analysis.

FR traceability: WL-303 (Pipeline Stage Percentiles)

---

## PipelinePercentileTracker

Tracks and computes percentiles of pipeline stage durations.

### Methods

#### PipelinePercentileTracker.__init__

```python
__init__(self: Any)
```

Initialize the tracker with empty recording list.

---

#### PipelinePercentileTracker.all_stages

```python
all_stages(self: Any)
```

Get sorted list of all unique stages recorded.

**Returns**: Sorted list of unique stage names.

---

#### PipelinePercentileTracker.percentile

```python
percentile(self: Any, stage: str, p: float)
```

Get the p-th percentile of durations for a stage.

**Parameters**:

- `stage`: Name of the pipeline stage.
- `p`: Percentile value (0-100).

**Returns**: The p-th percentile in milliseconds, or None if no data exists for the stage.

---

#### PipelinePercentileTracker.record

```python
record(self: Any, stage: str, duration_ms: float, cycle_id: str)
```

Record a pipeline stage execution.

**Parameters**:

- `stage`: Name of the pipeline stage.
- `duration_ms`: Execution duration in milliseconds.
- `cycle_id`: Associated cycle identifier.

---

#### PipelinePercentileTracker.summary

```python
summary(self: Any, stage: str)
```

Get summary statistics for a stage.

**Parameters**:

- `stage`: Name of the pipeline stage.

**Returns**: Dictionary with keys: stage, count, p50, p95, p99.
p50, p95, p99 are None if no data exists.

---

---

## StageTimer

Record of a single pipeline stage execution.

---

## all_stages

```python
all_stages(self: Any)
```

Get sorted list of all unique stages recorded.

**Returns**: Sorted list of unique stage names.

---

## percentile

```python
percentile(self: Any, stage: str, p: float)
```

Get the p-th percentile of durations for a stage.

**Parameters**:

- `stage`: Name of the pipeline stage.
- `p`: Percentile value (0-100).

**Returns**: The p-th percentile in milliseconds, or None if no data exists for the stage.

**Raises**:

- `ValueError`: If p is not in range [0, 100].

---

## record

```python
record(self: Any, stage: str, duration_ms: float, cycle_id: str)
```

Record a pipeline stage execution.

**Parameters**:

- `stage`: Name of the pipeline stage.
- `duration_ms`: Execution duration in milliseconds.
- `cycle_id`: Associated cycle identifier.

**Raises**:

- `ValueError`: If duration_ms is negative.

---

## summary

```python
summary(self: Any, stage: str)
```

Get summary statistics for a stage.

**Parameters**:

- `stage`: Name of the pipeline stage.

**Returns**: Dictionary with keys: stage, count, p50, p95, p99.
p50, p95, p99 are None if no data exists.

---

