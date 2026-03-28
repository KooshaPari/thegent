# provider_crud API Reference

> **Source**: `src/thegent/provider_crud.py`

Provider CRUD operations.

Extracted from provider_model_manager.py for maintainability.

---

## add_api_key

```python
add_api_key(provider: str, api_key: str)
```

Add an API key for a provider.

---

## add_provider

```python
add_provider(name: str, base_url: str, model: str, login_url: Any, login_instructions: Any, display_name: Any, extra_aliases: Any, api_key: Any, base_url_env: Any)
```

Add a new provider.

**Parameters**:

- `name`: Provider name
- `base_url`: API base URL
- `model`: Default model ID
- `login_url`: Optional login URL
- `login_instructions`: Optional login instructions
- `display_name`: Optional display name
- `extra_aliases`: Optional extra model aliases
- `api_key`: Optional API key
- `base_url_env`: Optional env var for base URL

**Returns**: Tuple of (success, message)

---

## delete_provider

```python
delete_provider(name: str, remove_credentials: bool)
```

Delete a provider.

---

## get_provider

```python
get_provider(name: str)
```

Get a specific provider.

**Parameters**:

- `name`: Provider name

**Returns**: Provider config or None if not found

---

## list_credentials

List all credentials.

---

## list_providers

```python
list_providers(include_credentials: bool)
```

List all configured providers.

**Parameters**:

- `include_credentials`: If True, include API keys

**Returns**: List of provider dicts

---

## remove_api_key

```python
remove_api_key(provider: str)
```

Remove an API key for a provider.

---

## update_provider

```python
update_provider(name: str, base_url: Any, model: Any, login_url: Any, login_instructions: Any, display_name: Any, extra_aliases: Any, api_key: Any, base_url_env: Any)
```

Update an existing provider.

---

## validate_provider

```python
validate_provider(name: str)
```

Validate a provider configuration.

---

