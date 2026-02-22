# otel_instrumentation API Reference

> **Source**: `src/thegent/observability/otel_instrumentation.py`

## instrument_genai_call

```python
instrument_genai_call(agent_name: str, model: str, run_id: Any, chunk_id: Any, system: Any)
```

Wrap an agent call with OTel spans using GenAI semantic conventions.

---

## record_usage

```python
record_usage(span: trace.Span, input_tokens: int, output_tokens: int)
```

Record token usage on an active span.

---
