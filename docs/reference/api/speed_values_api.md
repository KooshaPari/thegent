# speed_values API Reference

> **Source**: `src/thegent/models/speed_values.py`

Speed index for all model-provider pairs.

Uses CLIProxyAPIPlus GET /v1/metrics/providers (tps_1m, latency_p50_ms, latency_p95_ms, success_rate)
when available; falls back to Route.latency_ms from catalog.

---

## get_model_best_speed_index

```python
get_model_best_speed_index(model_id: str, settings: Any)
```

Get best speed index (0-1) across all providers for a model.

Used when provider is unknown (e.g. ObjectiveSelector).

---

## get_model_provider_speed_index

```python
get_model_provider_speed_index(model_id: str, provider: str, settings: Any)
```

Get speed index (0-1, higher = faster) for a model-provider pair.

Returns 0.5 if unknown (neutral).

---

## get_model_provider_speed_indices

```python
get_model_provider_speed_indices(settings: Any, use_cache: bool)
```

Build speed indices for all model-provider pairs.

Returns: {model_id: {provider: speed_index}}
speed_index is 0-1, higher = faster.
Uses proxy metrics when reachable; falls back to Route.latency_ms.

---

## invalidate_speed_index_cache

Clear speed index cache (e.g. after proxy restart).

---

