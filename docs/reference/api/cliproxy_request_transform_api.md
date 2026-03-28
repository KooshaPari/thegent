# cliproxy_request_transform API Reference

> **Source**: `src/thegent/cliproxy_request_transform.py`

## build_openrouter_passthrough_body

```python
build_openrouter_passthrough_body(body: dict)
```

Build a dict of OpenRouter passthrough fields present in body.

Returns a new dict containing only the OR passthrough fields from _OR_PASSTHROUGH_FIELDS
that are present in body. Used for documentation and testing purposes.

# @trace FR-REQEXT-042

---

