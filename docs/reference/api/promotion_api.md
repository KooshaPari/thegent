# promotion API Reference

> **Source**: `src/thegent/learning/promotion.py`

WP-14002: Autonomous learning and model promotion.

---

## ModelPromoter

Manages autonomous model promotion based on performance metrics.

### Methods

#### ModelPromoter.__init__

```python
__init__(self, settings)
```

#### ModelPromoter.evaluate_promotion

Evaluate if a model should be promoted to a higher tier (e.g. from experimental to production).

```python
evaluate_promotion(self, model_id, success_rate, cost_efficiency)
```

---

## evaluate_promotion

Evaluate if a model should be promoted to a higher tier (e.g. from experimental to production).

```python
evaluate_promotion(self, model_id, success_rate, cost_efficiency)
```

---

