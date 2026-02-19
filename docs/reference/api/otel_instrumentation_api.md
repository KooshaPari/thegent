# otel_instrumentation API Reference

> **Source**: `src/thegent/observability/otel_instrumentation.py`

## instrument_genai_call

Wrap an agent call with OTel spans using GenAI semantic conventions.

```python
instrument_genai_call(agent_name, model, run_id, chunk_id, system)
```

---

## record_usage

Record token usage on an active span.

```python
record_usage(span, input_tokens, output_tokens)
```

---

