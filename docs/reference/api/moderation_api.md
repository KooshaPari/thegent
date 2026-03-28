# moderation API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/moderation.py`

## ModerationCategory

---

## ModerationConfig

---

## ModerationResult

---

## check_moderation

```python
check_moderation(text: str, config: Any)
```

Check text against moderation rules. Uses DEFAULT_CATEGORIES if config is None.

---

## should_block

```python
should_block(result: ModerationResult, config: Any)
```

Return True if the moderation result warrants blocking the request.

---

