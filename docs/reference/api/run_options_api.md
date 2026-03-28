# run_options API Reference

> **Source**: `src/thegent/agents/run_options.py`

RunOptions — extended run-time options for agent execution.

# @trace WL-112

---

## RunOptions

Extended run options for agent execution.

# @trace WL-112

**Inherits from**: `BaseModel`

---

## translate_reasoning_to_anthropic_budget

```python
translate_reasoning_to_anthropic_budget(effort: str)
```

Translate a reasoning_effort value to Anthropic thinking.budget_tokens.

Raises KeyError if the effort value is not a recognised level.

# @trace WL-112

---

## translate_reasoning_to_codex_config

```python
translate_reasoning_to_codex_config(effort: str)
```

Translate a reasoning_effort value to a Codex --config dict.

Returns a dict suitable for merging into CodexProxyRunner.config_overrides
or passing to _build_config_flags().

# @trace WL-112

---

## translate_reasoning_to_openai_effort

```python
translate_reasoning_to_openai_effort(effort: str)
```

Translate a reasoning_effort value to OpenAI o-series reasoning.effort string.

Maps xhigh -> high (OpenAI only supports low/medium/high).

# @trace WL-112

---

