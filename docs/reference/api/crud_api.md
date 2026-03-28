# crud API Reference

> **Source**: `src/thegent/provider/crud.py`

Provider management - CRUD operations.

Domain: Provider
Functions:
- list_providers, get_provider, add_provider, update_provider, delete_provider

---

## add_provider

```python
add_provider(name: str, config: dict[(str, Any)])
```

Add a new provider.

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

Get a specific provider by name.

---

## list_providers

```python
list_providers(include_credentials: bool)
```

List all configured providers.

---

## update_provider

```python
update_provider(name: str, config: dict[(str, Any)])
```

Update an existing provider.

---

## validate_provider

```python
validate_provider(name: str)
```

Validate provider configuration.

---

