# ollama_provider API Reference

> **Source**: `src/thegent/utils/routing_impl/ollama_provider.py`

Ollama local model provider for zero-cost execution.

Ollama exposes an OpenAI-compatible REST API at http://localhost:11434/v1.
This module provides availability detection and model discovery; actual
inference routing goes through LiteLLM with the ``ollama`` provider prefix.

WL-118: Ollama as a local model provider.

---

## OllamaUnavailableError

Raised when Ollama provider is explicitly requested but unreachable.

**Inherits from**: `RuntimeError`

---

## assert_ollama_available

Raise OllamaUnavailableError if Ollama daemon is not reachable.

Use this at the start of any code path where ``--provider ollama`` was
explicitly requested so we fail loudly rather than silently falling back.

**Raises**:

- `OllamaUnavailableError`: If the daemon is not reachable.

---

## build_litellm_entry

```python
build_litellm_entry(model: str)
```

Build a LiteLLM model_list entry for a local Ollama model.

**Parameters**:

- `model`: Ollama model name (e.g. ``"llama3.3"``).

**Returns**: LiteLLM model_list entry dict with ``model_name`` and
``litellm_params`` (including ``api_base`` and ``api_key``).

---

## get_available_models

Return list of locally available Ollama model names.

Calls GET /api/tags and extracts the ``name`` field from each entry in the
``models`` array.  Raises ``OllamaUnavailableError`` if the daemon is not
reachable so routing code can fail loudly when Ollama was explicitly
requested.

**Returns**: Sorted list of model name strings (e.g. ``["llama3.3", "mistral"]``).

**Raises**:

- `OllamaUnavailableError`: If daemon is not reachable or returns non-200.

---

## is_ollama_available

Check if Ollama daemon is running at localhost:11434.

Performs a GET /api/tags probe with a short timeout.  Returns False for
any network or HTTP error so callers can treat Ollama as unavailable
without crashing.

**Returns**: True if the daemon responded with HTTP 200, False otherwise.

---

## resolve_ollama_model

```python
resolve_ollama_model(model: str)
```

Resolve a thegent model alias to a canonical Ollama model name.

Strips an ``ollama/`` prefix if present, then looks up the alias in
``OLLAMA_MODEL_ALIASES``.  Falls back to the raw name if no alias exists.

**Parameters**:

- `model`: Model identifier (e.g. ``"llama3.3"``, ``"ollama/mistral"``).

**Returns**: Canonical Ollama model name (e.g. ``"llama3.3"``).

---

