# learning API Reference

> **Source**: `src/thegent/planning/learning.py`

WP-14002: Learning model registry and promotion with canary scoring.

---

## CanaryMetrics

### Methods

#### CanaryMetrics.avg_latency

```python
avg_latency(self)
```

#### CanaryMetrics.success_rate

```python
success_rate(self)
```

---

## LearningModel

---

## LearningRegistry

Registry for managing the lifecycle of candidate models (WP-14002).

### Methods

#### LearningRegistry.__init__

```python
__init__(self, storage_path)
```

#### LearningRegistry.add_canary

Register a new model for canary testing.

```python
add_canary(self, model_id)
```

#### LearningRegistry.finalize_promotion

WP-14003: Finalize promotion after human approval.

```python
finalize_promotion(self, model_id, approver)
```

#### LearningRegistry.list_models

```python
list_models(self)
```

#### LearningRegistry.promote_to_candidate

Promote a canary to a promotion candidate based on metrics.

```python
promote_to_candidate(self, model_id)
```

#### LearningRegistry.record_outcome

Record the outcome of a canary run.

```python
record_outcome(self, model_id, success, latency_ms, cost_usd)
```

---

## add_canary

Register a new model for canary testing.

```python
add_canary(self, model_id)
```

---

## avg_latency

```python
avg_latency(self)
```

---

## finalize_promotion

WP-14003: Finalize promotion after human approval.

```python
finalize_promotion(self, model_id, approver)
```

---

## list_models

```python
list_models(self)
```

---

## promote_to_candidate

Promote a canary to a promotion candidate based on metrics.

```python
promote_to_candidate(self, model_id)
```

---

## record_outcome

Record the outcome of a canary run.

```python
record_outcome(self, model_id, success, latency_ms, cost_usd)
```

---

## success_rate

```python
success_rate(self)
```

---

