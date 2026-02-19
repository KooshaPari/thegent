# selector API Reference

> **Source**: `src/thegent/planning/selector.py`

WP-14001: Cost-aware objective selector for multi-objective optimization.

---

## ObjectiveSelector

Optimizes model selection across multiple objectives (WP-14001).

### Methods

#### ObjectiveSelector.__init__

```python
__init__(self, weights)
```

#### ObjectiveSelector.select_best_model

Score and select the best model from the candidates.

```python
select_best_model(self, candidate_ids)
```

---

## ObjectiveWeights

### Methods

#### ObjectiveWeights.validate

```python
validate(self)
```

---

## get_objective_profile

Return a predefined objective profile.

```python
get_objective_profile(profile_name)
```

---

## select_best_model

Score and select the best model from the candidates.

```python
select_best_model(self, candidate_ids)
```

---

## validate

```python
validate(self)
```

---

