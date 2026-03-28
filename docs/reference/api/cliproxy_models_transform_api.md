# cliproxy_models_transform API Reference

> **Source**: `src/thegent/cliproxy_models_transform.py`

## get_transform_models_diagnostics

Return diagnostics for transform_models_response failures.

---

## reset_transform_models_diagnostics

Reset transform diagnostics (test helper).

---

## transform_models_response

```python
transform_models_response(content: Any)
```

Transform CLIProxy models response to Codex-compatible format.

Codex 0.104.0 requires:
- Top-level "models" key (Codex API format, NOT OpenAI "data" key)
- Each model object with 20+ required fields (slug, shell_type, supported_reasoning_levels, etc.)
- x-models-etag response header (SHA256 of sorted model IDs)

OR-15: When inject_openrouter=True, known OpenRouter proxy models are merged into the
list before enrichment so Codex sees them even if the CLIProxy backend omits them.

Without the full schema, Codex shows "Model metadata for X not found" and won't connect.

Returns (transformed_body, etag) or None on parse failure.

---

