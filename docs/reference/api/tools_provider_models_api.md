# tools_provider_models API Reference

> **Source**: `src/thegent/mcp/server/tools_provider_models.py`

Provider/model management tool registrations for MCP server.

---

## add_api_key

```python
add_api_key(provider: str, api_key: str)
```

Add or update API key for a provider.

---

## add_model_alias

```python
add_model_alias(provider: str, model: str, alias: str)
```

Add a model alias for a provider.

---

## add_provider

```python
add_provider(name: str, base_url: str, model: str, api_key: Any, extra_aliases: Any, login_url: Any)
```

Add a new provider configuration.

---

## delete_provider

```python
delete_provider(name: str, remove_credentials: bool)
```

Delete a provider configuration.

---

## discover_models

```python
discover_models(provider: Any)
```

Discover available models from provider APIs.

---

## get_provider

```python
get_provider(name: str)
```

Get a specific provider configuration.

---

## list_credentials

List all configured credentials (API keys and OAuth).

---

## list_models

```python
list_models(provider: Any)
```

List all models, optionally filtered by provider.

---

## list_providers

```python
list_providers(include_credentials: bool)
```

List all configured providers with their settings.

---

## register_provider_model_tools

---

## remove_api_key

```python
remove_api_key(provider: str)
```

Remove API key for a provider.

---

## remove_model_alias

```python
remove_model_alias(provider: str, alias: str)
```

Remove a model alias from a provider.

---

## update_provider

```python
update_provider(name: str, base_url: Any, model: Any, api_key: Any, extra_aliases: Any)
```

Update an existing provider configuration.

---

## validate_provider

```python
validate_provider(name: str)
```

Validate a provider by testing connectivity and credentials.

---

