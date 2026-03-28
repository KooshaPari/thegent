# pii API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/pii.py`

## PiiEntity

---

## PiiMaskResult

---

## mask_messages

```python
mask_messages(messages: list[dict], entity_types: Any)
```

Mask PII in a messages list (OpenAI format). Returns (masked_messages, token_map).

---

## mask_pii

```python
mask_pii(text: str, entity_types: Any)
```

Detect and mask PII entities. entity_types=None masks all known types.

---

## unmask_content

```python
unmask_content(content: str, token_map: dict[(str, str)])
```

Unmask LLM response content using stored token_map.

---

## unmask_pii

```python
unmask_pii(text: str, token_map: dict[(str, str)])
```

Re-insert original values using the token_map from mask_pii().

---

