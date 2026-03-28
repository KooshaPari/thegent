# provider_model_scoring API Reference

> **Source**: `src/thegent/provider_model_scoring.py`

Model scoring, indices, and benchmarking functions.

This module provides functions for:
- Model indices (context limits, cost, speed, benchmarks)
- Composite score calculation
- Fuzzy search
- Modality management

---

## add_custom_benchmark

```python
add_custom_benchmark(provider: str, model: str, benchmark_name: str, score: float)
```

Add custom benchmark score to model.

**Parameters**:

- `provider`: Provider name
- `model`: Model name
- `benchmark_name`: Name of benchmark
- `score`: Score (0-1)

**Returns**: Tuple of (success, message)

---

## add_model_index

```python
add_model_index(provider: str, model: str, context_window: Any, max_output_tokens: Any, cost_per_1m_input: Any, cost_per_1m_output: Any, tokens_per_second: Any, benchmarks: Any, modalities: Any)
```

Add or update model index entry.

**Parameters**:

- `provider`: Provider name
- `model`: Model name
- `context_window`: Context window size
- `max_output_tokens`: Maximum output tokens
- `cost_per_1m_input`: Cost per million input tokens
- `cost_per_1m_output`: Cost per million output tokens
- `tokens_per_second`: Generation speed
- `benchmarks`: Dict of benchmark_name -> score (0-1)
- `modalities`: Dict of modality_name -> enabled

**Returns**: Tuple of (success, message)

---

## add_model_modality

```python
add_model_modality(provider: str, model: str, modality: str, enabled: bool)
```

Add or update modality for model.

**Parameters**:

- `provider`: Provider name
- `model`: Model name
- `modality`: Modality name (e.g., 'vision', 'audio', 'tools')
- `enabled`: Whether modality is enabled

**Returns**: Tuple of (success, message)

---

## calculate_composite_score

```python
calculate_composite_score(benchmarks: dict[(str, float)], weights: Any)
```

Calculate composite performance score from benchmarks.

Uses available benchmarks only - missing benchmarks don't penalize.
Results are normalized to 0-100 scale.

**Parameters**:

- `benchmarks`: Dict of benchmark_name -> score (0-1)
- `weights`: Optional custom weights for benchmarks

**Returns**: Composite score 0-100, or None if no benchmarks available

---

## fuzzy_search_models

```python
fuzzy_search_models(query: str, provider: Any, limit: int)
```

Fuzzy search models by name.

**Parameters**:

- `query`: Search query
- `provider`: Optional provider filter
- `limit`: Maximum results

**Returns**: List of matching models with scores

---

## get_model_indices

```python
get_model_indices(provider: Any, model: Any)
```

Get model indices (context limits, cost, speed, benchmarks).

---

## get_model_modalities

```python
get_model_modalities(provider: Any, model: Any)
```

Get model modalities (text, vision, audio, etc.).

**Parameters**:

- `provider`: Optional provider filter
- `model`: Optional model filter

**Returns**: Dict of model -> modalities

---

## list_available_modalities

List all available modality types.

**Returns**: Dict of modality -> description

---

## list_model_indices

```python
list_model_indices(provider: Any, sort_by: str, limit: Any)
```

List all model indices with optional sorting.

**Parameters**:

- `provider`: Optional provider filter
- `sort_by`: Sort by 'context', 'cost_input', 'cost_output', 'tps', 'score'
- `limit`: Optional limit on results

**Returns**: List of model index entries sorted by specified field

---

## list_models_with_scores

```python
list_models_with_scores(provider: Any, min_score: Any, modality: Any, sort_by: str)
```

List models with composite performance scores.

**Parameters**:

- `provider`: Optional provider filter
- `min_score`: Minimum composite score filter
- `modality`: Only include models with this modality enabled
- `sort_by`: Sort by 'composite_score', 'cost', 'context', 'tps'

**Returns**: List of models with computed composite scores

---

## remove_model_index

```python
remove_model_index(provider: str, model: str)
```

Remove model index entry.

---

## search_by_modalities

```python
search_by_modalities(modalities: list[str], provider: Any, match_all: bool)
```

Search models by enabled modalities.

**Parameters**:

- `modalities`: List of required modalities
- `provider`: Optional provider filter
- `match_all`: If True, require all modalities; if False, require any

**Returns**: List of models with specified modalities

---

## search_models_by_capability

```python
search_models_by_capability(capability: str, provider: Any, min_value: Any)
```

Search models by capability/benchmark score.

**Parameters**:

- `capability`: Capability name (e.g., 'reasoning', 'coding', 'swebench')
- `provider`: Optional provider filter
- `min_value`: Minimum score threshold (0-1)

**Returns**: List of models matching capability

---

## sort_key

```python
sort_key(item: dict) -> Any
```

---

