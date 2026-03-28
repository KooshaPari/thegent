# manage_models API Reference

> **Source**: `src/thegent/use_cases/manage_models.py`

Model CRUD operations (add, remove, update, list models, routing).

---

## add_common_alias

```python
add_common_alias(alias: str)
```

Add a common model alias that works across providers.

**Parameters**:

- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

## add_model_alias

```python
add_model_alias(provider: str, model: str, alias: str)
```

Add a model alias for a provider.

**Parameters**:

- `provider`: Provider name.
- `model`: Base model name (for reference, not directly used in storage).
- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

## list_models

```python
list_models(provider: Any)
```

List all models, optionally filtered by provider.

**Parameters**:

- `provider`: Optional provider name to filter by.

**Returns**: List of model configurations across providers and common aliases.

---

## remove_common_alias

```python
remove_common_alias(alias: str)
```

Remove a common model alias.

**Parameters**:

- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

## remove_model_alias

```python
remove_model_alias(provider: str, alias: str)
```

Remove a model alias from a provider.

**Parameters**:

- `provider`: Provider name.
- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

