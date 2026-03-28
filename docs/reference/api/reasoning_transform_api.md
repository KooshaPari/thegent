# reasoning_transform API Reference

> **Source**: `src/thegent/utils/routing_impl/reasoning_transform.py`

GW-40: Unified reasoning interface.

Normalizes {effort: "high"/"medium"/"low"} to provider-specific reasoning params:
- Anthropic: extended_thinking with budget_tokens
- OpenAI: reasoning_effort (high/medium/low)
- Google Gemini: thinking_config with thinking_budget

# @trace FR-REQEXT-040

---

## ReasoningEffort

**Inherits from**: `str, Enum`

---

## apply_anthropic_reasoning

```python
apply_anthropic_reasoning(body: dict, effort: ReasoningEffort)
```

Add extended_thinking to Anthropic request body.

Sets body["thinking"] = {"type": "enabled", "budget_tokens": THINKING_BUDGET[effort]}.
Removes "reasoning" key if present.
Returns modified copy of body (does not mutate in place).

---

## apply_gemini_reasoning

```python
apply_gemini_reasoning(body: dict, effort: ReasoningEffort)
```

Add thinking_config to Google Gemini request body.

Sets body["thinking_config"] = {"thinking_budget": THINKING_BUDGET[effort]}.
Removes "reasoning" key if present.
Returns modified copy of body.

---

## apply_openai_reasoning

```python
apply_openai_reasoning(body: dict, effort: ReasoningEffort)
```

Add reasoning_effort to OpenAI request body.

Sets body["reasoning_effort"] = effort.value.
Removes "reasoning" and "variant" keys if present.
Returns modified copy of body.

---

## apply_reasoning_for_provider

```python
apply_reasoning_for_provider(body: dict, provider: str)
```

Apply provider-specific reasoning transform for body["reasoning"]["effort"].

If no reasoning effort in body, returns body unchanged.
Dispatches to apply_anthropic_reasoning / apply_openai_reasoning / apply_gemini_reasoning
based on provider prefix matching ("anthropic", "openai", "google", "gemini").
For "codex" provider, treats as OpenAI-compatible (uses reasoning_effort).
Unknown providers: strips "reasoning" key and returns.

---

## extract_reasoning_effort

```python
extract_reasoning_effort(body: dict)
```

Extract reasoning effort from request body.

Reads body["reasoning"]["effort"], body["reasoning_effort"], or body["variant"].
Returns None if not present or invalid.

---

