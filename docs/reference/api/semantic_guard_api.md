# semantic_guard API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/semantic_guard.py`

## SemanticGuardConfig

---

## SemanticGuardResult

---

## check_semantic_guard

```python
check_semantic_guard(text: str, config: SemanticGuardConfig, provider: Any)
```

Check text similarity against reference prompts.

If provider is None, uses NumpyEmbeddingProvider (deterministic seeded).
Returns blocked=False if config.reference_prompts is empty.

---

