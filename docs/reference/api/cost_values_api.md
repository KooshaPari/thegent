# cost_values API Reference

> **Source**: `src/thegent/models/cost_values.py`

Cost values for all model-provider pairs.

Uses CLIProxyAPIPlus GET /v1/metrics/providers when available; falls back to
static catalog cost_weight, planning/models_meta, and governance defaults.

---

## get_cost_for_model_provider

Get (input_per_1k_usd, output_per_1k_usd) for a model-provider pair.

Returns (0.001, 0.002) if unknown.

```python
get_cost_for_model_provider(model_id, provider, settings)
```

---

## get_model_provider_costs

Build cost values for all model-provider pairs.

Returns: {model_id: {provider: (input_per_1k_usd, output_per_1k_usd)}}
Uses proxy metrics when reachable; falls back to static values.

```python
get_model_provider_costs(settings)
```

---

