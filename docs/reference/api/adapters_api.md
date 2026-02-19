# adapters API Reference

> **Source**: `src/thegent/contracts/adapters.py`

Output adapter protocol and scaffolding for provider-specific normalization.

Adapters convert copilot/gemini/codex/claude (and other) outputs into
CanonicalStructuredMessage for orchestration pipelines.

---

## AdapterResult

Result of adapter normalization.

---

## GenericOutputAdapter

Default adapter using output_parser.extract_condensed for all providers.

### Methods

#### GenericOutputAdapter.__init__

```python
__init__(self, provider)
```

#### GenericOutputAdapter.normalize

```python
normalize(self, raw, context)
```

#### GenericOutputAdapter.provider

```python
provider(self)
```

---

## OutputAdapter

Protocol for provider output adapters.

Each provider (copilot, gemini, codex, claude, etc.) should implement
an adapter that normalizes raw output into CanonicalStructuredMessage.

**Inherits from**: `Protocol`

### Methods

#### OutputAdapter.normalize

Normalize raw provider output to CSM.

Args:
    raw: Raw stdout string or parsed dict from provider.
    context: Optional context (run_id, chunk_id, etc.).

Returns:
    AdapterResult with CSM and confidence.

```python
normalize(self, raw, context)
```

#### OutputAdapter.provider

Provider identifier (e.g. copilot, gemini, codex, claude).

```python
provider(self)
```

---

## XMLOutputAdapter

Base adapter for XML-structured agent outputs.

### Methods

#### XMLOutputAdapter.__init__

```python
__init__(self, provider_name)
```

#### XMLOutputAdapter.normalize

```python
normalize(self, raw, context)
```

#### XMLOutputAdapter.provider

```python
provider(self)
```

---

## get_adapter

Get adapter for provider, or None if not registered.

```python
get_adapter(provider)
```

---

## get_tag

---

## normalize

```python
normalize(self, raw, context)
```

---

## normalize_output

Normalize provider output via registered adapter, or fallback to plain extraction.

If no adapter is registered or if adapter fails and allow_fallback is True,
returns a best-effort CSM.

```python
normalize_output(provider, raw, context, allow_fallback)
```

---

## provider

```python
provider(self)
```

---

## register_adapter

Register an output adapter for a provider.

```python
register_adapter(provider, adapter)
```

---

