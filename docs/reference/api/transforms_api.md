# transforms API Reference

> **Source**: `src/thegent/utils/routing_impl/transforms.py`

GW-41: Request/response transforms including middle-out context compression.

middle-out: Compresses long message histories by summarizing middle messages
while preserving system prompt, first user message, and recent messages.

# @trace FR-REQEXT-041

---

## apply_middle_out

```python
apply_middle_out(messages: list[dict], max_messages: int)
```

Compress messages list using middle-out strategy.

If len(messages) <= max_messages: return unchanged.
Otherwise:
- Keep: system messages (all), first user message, last (max_messages // 2) messages
- Replace middle with a single synthetic assistant message summarizing count
  {"role": "assistant", "content": f"[{n} earlier messages omitted for context window]"}

Returns new list (does not mutate).

---

## apply_transforms

```python
apply_transforms(body: dict, max_messages: int)
```

Apply all transforms listed in body["transforms"].

Supported transforms: "middle-out"
Unknown transforms are silently ignored.
Returns modified copy of body.

---

## extract_transforms

```python
extract_transforms(body: dict)
```

Extract transforms list from request body.

Returns body.get("transforms", []).

---

