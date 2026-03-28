# context_validator API Reference

> **Source**: `src/thegent/utils/routing_impl/context_validator.py`

GW-62: Pre-call context window validation.

Checks if the request's token count fits within the model's context window.
Triggers context_window_fallbacks if the check fails.

# @trace FR-AROUTE-062

---

## ContextWindowCheckResult

Result of a context window validation check.

---

## check_context_window

```python
check_context_window(model: str, messages: list[dict])
```

Check whether the request fits within the model's context window.

Unknown models are allowed through (fits=True) to avoid blocking
requests to models not yet in the registry.

**Parameters**:

- `model`: Model identifier string (e.g. "gpt-4o").
- `messages`: List of message dicts whose tokens to estimate.

**Returns**: ContextWindowCheckResult with fit status, estimated tokens, and overflow.

---

## estimate_token_count

```python
estimate_token_count(messages: list[dict])
```

Estimate the token count for a list of messages.

Rough heuristic: 1 token ≈ 4 characters of text.

**Parameters**:

- `messages`: List of message dicts (e.g., OpenAI chat format).

**Returns**: Integer token estimate.

---

## select_fallback_model

```python
select_fallback_model(model: str, fallbacks: list[str], messages: list[dict])
```

Select the first fallback model whose context window fits the messages.

Iterates through fallbacks in order and returns the first that fits.
If none fit, returns the last fallback (better to attempt than to block).
If fallbacks is empty, returns the original model unchanged.

**Parameters**:

- `model`: The original model that failed the context window check.
- `fallbacks`: Ordered list of fallback model identifiers to try.
- `messages`: The message list to check against each fallback's limit.

**Returns**: A model identifier string — the first fitting fallback, or last if none fit.

---

