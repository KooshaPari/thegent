# manage_providers API Reference

> **Source**: `src/thegent/use_cases/manage_providers.py`

Provider CRUD operations (add, remove, update, list providers).

---

## add_provider

```python
add_provider(name: str, base_url: str, model: str, login_url: Any, login_instructions: Any, display_name: Any, extra_aliases: Any, api_key: Any, base_url_env: Any)
```

Add a new provider.

**Parameters**:

- `name`: Provider name.
- `base_url`: Base URL for the provider API.
- `model`: Default model name.
- `login_url`: Optional login/authentication URL.
- `login_instructions`: Optional list of login instruction steps.
- `display_name`: Display name for login UI.
- `extra_aliases`: Additional model aliases.
- `api_key`: API key to store in CLIProxy config.
- `base_url_env`: Environment variable name for base_url.

**Returns**: Tuple of (success: bool, message: str).

---

## delete_provider

```python
delete_provider(name: str, remove_credentials: bool)
```

Delete a provider.

**Parameters**:

- `name`: Provider name.
- `remove_credentials`: If True, also removes credentials from CLIProxy config.

**Returns**: Tuple of (success: bool, message: str).

---

## get_provider

```python
get_provider(name: str)
```

Get a specific provider by name.

**Parameters**:

- `name`: Provider name (case-insensitive).

**Returns**: Provider configuration dict, or None if not found.

---

## list_providers

```python
list_providers(include_credentials: bool)
```

List all configured providers.

**Parameters**:

- `include_credentials`: If False, strips sensitive API keys and credentials.

**Returns**: List of provider configurations.

---

## update_provider

```python
update_provider(name: str, base_url: Any, model: Any, login_url: Any, login_instructions: Any, display_name: Any, extra_aliases: Any, api_key: Any, base_url_env: Any)
```

Update an existing provider.

**Parameters**:

- `name`: Provider name.
- `base_url`: New base URL (optional).
- `model`: New default model (optional).
- `login_url`: New login URL (optional).
- `login_instructions`: New login instructions (optional).
- `display_name`: New display name (optional).
- `extra_aliases`: New aliases (optional).
- `api_key`: New API key (optional).
- `base_url_env`: New env var name (optional).

**Returns**: Tuple of (success: bool, message: str).

---

