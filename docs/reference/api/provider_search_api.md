# provider_search API Reference

> **Source**: `src/thegent/provider_search.py`

Model search and scoring functions.

Extracted from provider_model_manager.py for maintainability.

---

## calculate_composite_score

```python
calculate_composite_score(benchmarks: dict[(str, float)], weights: Any)
```

Calculate composite performance score from benchmarks.

---

## fuzzy_search_models

```python
fuzzy_search_models(query: str, min_score: float)
```

Fuzzy search models by name.

---

## list_model_indices

```python
list_model_indices(sort_by: str, provider: Any, reverse: bool)
```

List all model indices with optional sorting.

---

## search_models_by_capability

```python
search_models_by_capability(capability: str, min_context: Any, max_cost_per_1m: Any)
```

Search models by capability.

---

