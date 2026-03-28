# provider_names API Reference

> **Source**: `src/thegent/utils/provider_names.py`

Provider name normalization and type utilities.

This module is intentionally decoupled from routing_impl to avoid circular imports
with models.catalog.

---

## normalize_provider_name

```python
normalize_provider_name(provider: str)
```

Normalize provider aliases into canonical routing names.

---

