# harness_model_mapping API Reference

> **Source**: `src/thegent/utils/routing_impl/harness_model_mapping.py`

Provider-harness-model mapping for universal parity across Codex, LiteLLM, and CLIProxy.

Ensures consistent model resolution and metadata when requests flow through:
- Codex harness (dex) -> CLIProxy adapter -> CLIProxyAPIPlus
- LiteLLM Router -> CLIProxyAPIPlus
- Direct CLIProxy API

When clode harness pairs with minimax/kilo + MiniMax-M2.5, see Minimax clode guidance:
https://platform.minimax.io/docs/coding-plan/claude-code

---

## get_ollama_models

Return list of all registered Ollama model aliases.

---

## get_openrouter_models

Return list of all OpenRouter model IDs we can route to.

---

## is_openrouter_model_id

```python
is_openrouter_model_id(model: str)
```

Return True if model string is in OpenRouter provider/model format (contains '/').

---

## resolve_model_for_backend

```python
resolve_model_for_backend(model: str)
```

Map Codex/provider-specific model ID to CLIProxy backend model ID.

---

## resolve_ollama_model_alias

```python
resolve_ollama_model_alias(model: str)
```

Map a thegent short model name to the canonical Ollama model name.

Strips an ``ollama/`` prefix first, then looks up in ``OLLAMA_MODEL_ALIASES``.
Falls back to the raw (stripped) name if no alias is registered.

**Parameters**:

- `model`: Short alias (e.g. ``"llama3.3"``) or prefixed form
(e.g. ``"ollama/llama3.3"``).

**Returns**: Canonical Ollama model name (e.g. ``"llama3.3"``).

---

## resolve_openrouter_model

```python
resolve_openrouter_model(model: str)
```

Map any thegent model alias to OpenRouter provider/model format.

Tries CANONICAL_TO_OPENROUTER first. If not found and model contains '/',
returns as-is (already in provider/model format). Otherwise returns model unchanged.

---

