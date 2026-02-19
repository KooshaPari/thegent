# cost API Reference

> **Source**: `src/thegent/governance/cost.py`

Cost governance scaffolding (G-GP-06).

CostEstimator and CostAggregator for per-run cost tracking.
See docs/governance/COST_GOVERNANCE_DESIGN.md.

---

## CostAggregator

Daily cost rollup by owner. G-GP-06 Phase 4.

### Methods

#### CostAggregator.daily_total

Sum cost_usd for owner's runs today. Returns 0.0 if no cost tracking.

```python
daily_total(self, owner)
```

#### CostAggregator.get_all_categories_mtd

Get MTD cost totals for all categories.

Returns:
    Dictionary mapping category names to MTD costs

```python
get_all_categories_mtd(self)
```

#### CostAggregator.get_category_mtd_total

Sum cost_usd for a specific category this month.

Args:
    category: Task category (fast/normal/complex/high_complex)

Returns:
    Total cost in USD for the category this month

```python
get_category_mtd_total(self, category)
```

#### CostAggregator.get_mtd_total

Sum cost_usd for all runs this month. G-GP-06 Phase 4.

```python
get_mtd_total(self)
```

---

## CostEstimator

Estimate run cost from metadata. WP-5003: Cost-aware routing integration.

### Methods

#### CostEstimator.estimate

Estimate cost in USD. Uses pricing table or heuristic fallback.

```python
estimate(self, model, tokens_total, prompt_length)
```

---

## daily_total

Sum cost_usd for owner's runs today. Returns 0.0 if no cost tracking.

```python
daily_total(self, owner)
```

---

## estimate

Estimate cost in USD. Uses pricing table or heuristic fallback.

```python
estimate(self, model, tokens_total, prompt_length)
```

---

## get_all_categories_mtd

Get MTD cost totals for all categories.

Returns:
    Dictionary mapping category names to MTD costs

```python
get_all_categories_mtd(self)
```

---

## get_category_mtd_total

Sum cost_usd for a specific category this month.

Args:
    category: Task category (fast/normal/complex/high_complex)

Returns:
    Total cost in USD for the category this month

```python
get_category_mtd_total(self, category)
```

---

## get_mtd_total

Sum cost_usd for all runs this month. G-GP-06 Phase 4.

```python
get_mtd_total(self)
```

---

