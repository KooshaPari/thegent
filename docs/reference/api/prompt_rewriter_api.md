# prompt_rewriter API Reference

> **Source**: `src/thegent/utils/routing_impl/prompt_rewriter.py`

GW-69: Auto prompt rewriting per model/provider.

Implements provider-specific and model-specific prompt normalization.
Rules are matched by provider and model prefix, then applied in priority order.

# @trace FR-PROMPT-069

---

## RewriteConfig

Configuration for the prompt rewriter.

---

## RewriteResult

Result of a prompt rewrite operation.

---

## RewriteRule

A prompt rewriting rule matched by provider and/or model.

---

## rewrite_prompt

```python
rewrite_prompt(messages: list[dict])
```

Rewrite messages for provider/model conventions.

Returns a RewriteResult with the (possibly modified) messages.
When config.enabled=False or no rules match, returns original messages unchanged.

---

