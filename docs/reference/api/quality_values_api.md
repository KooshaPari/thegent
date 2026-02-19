# quality_values API Reference

> **Source**: `src/thegent/models/quality_values.py`

Quality index for models.

Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
falls back to Route.accuracy_score from catalog.

---

## get_all_model_quality_indices

Returns: {model_id: quality_index}

```python
get_all_model_quality_indices(settings, benchmarks_path)
```

---

## get_model_provider_quality_index

Get quality index (0-1) for a model-provider pair.

Returns 0.5 if unknown.

```python
get_model_provider_quality_index(model_id, provider, settings)
```

---

## get_model_provider_quality_indices

Returns: {model_id: {provider: quality_index}}
Same model has same quality across providers; structure matches cost/speed.

```python
get_model_provider_quality_indices(settings, benchmarks_path, use_cache)
```

---

## get_model_quality_index

Get quality index (0-1) for a model.

Uses benchmarks.json when available; falls back to Route.accuracy_score.

```python
get_model_quality_index(model_id, settings, benchmarks_path)
```

---

## invalidate_quality_index_cache

Clear quality index cache (e.g. after benchmarks.json update).

---

