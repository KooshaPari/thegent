# provider_model_manager_cliproxy API Reference

> **Source**: `src/thegent/provider_model_manager_cliproxy.py`

CLIProxy config helpers for provider/model manager.

---

## get_api_key_from_compat

```python
get_api_key_from_compat(compat: list[dict[(str, Any)]], name: str)
```

Get first API key from provider compat entry.

---

## remove_openai_compat_entry

```python
remove_openai_compat_entry(compat: list[dict[(str, Any)]], name: str)
```

Return compat entries excluding the requested provider name.

---

## upsert_openai_compat_entry

```python
upsert_openai_compat_entry(compat: list[dict[(str, Any)]])
```

Add or update an openai-compatibility entry in-place.

---

