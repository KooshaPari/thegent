# cliproxy_provider API Reference

> **Source**: `src/thegent/adapters/driven/cliproxy_provider.py`

CLIProxy compatibility layer adapter.

This module adapts provider operations to CLIProxy's openai-compatibility configuration format.
It delegates to provider_model_manager_cliproxy for core CLIProxy logic.

---

## CliproxyCompatAdapter

Adapter for CLIProxy openai-compatibility configuration.

### Methods

#### CliproxyCompatAdapter.get_api_key

```python
get_api_key(compat: list[dict[(str, Any)]], name: str)
```

Get API key from a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list.
- `name`: Provider name.

**Returns**: API key string, or None if not found.

---

#### CliproxyCompatAdapter.remove_entry

```python
remove_entry(compat: list[dict[(str, Any)]], name: str)
```

Remove a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list.
- `name`: Provider name to remove.

**Returns**: Filtered list excluding the provider.

---

#### CliproxyCompatAdapter.upsert_entry

```python
upsert_entry(compat: list[dict[(str, Any)]])
```

Add or update a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list to modify in-place.
- `name`: Provider name.
- `base_url`: Provider base URL.
- `model`: Default model name.
- `api_key`: API key for authentication.

---

---

## get_api_key

```python
get_api_key(compat: list[dict[(str, Any)]], name: str)
```

Get API key from a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list.
- `name`: Provider name.

**Returns**: API key string, or None if not found.

---

## remove_entry

```python
remove_entry(compat: list[dict[(str, Any)]], name: str)
```

Remove a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list.
- `name`: Provider name to remove.

**Returns**: Filtered list excluding the provider.

---

## upsert_entry

```python
upsert_entry(compat: list[dict[(str, Any)]])
```

Add or update a CLIProxy openai-compatibility entry.

**Parameters**:

- `compat`: The openai-compatibility list to modify in-place.
- `name`: Provider name.
- `base_url`: Provider base URL.
- `model`: Default model name.
- `api_key`: API key for authentication.

---

