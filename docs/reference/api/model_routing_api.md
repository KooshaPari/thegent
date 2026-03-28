# model_routing API Reference

> **Source**: `src/thegent/ports/driven/model_routing.py`

ModelRoutingPort: Interface for model selection and routing.

---

## ModelRoutingPort

Port interface for model discovery and routing operations.

**Inherits from**: `Protocol`

### Methods

#### ModelRoutingPort.add_common_alias

```python
add_common_alias(self: Any, alias: str)
```

Add a common model alias that works across providers.

**Parameters**:

- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

#### ModelRoutingPort.add_model_alias

```python
add_model_alias(self: Any, provider: str, model: str, alias: str)
```

Add a model alias for a provider.

**Parameters**:

- `provider`: Provider name.
- `model`: Base model name.
- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

#### ModelRoutingPort.discover_models

```python
discover_models(self: Any, provider: Any)
```

Discover available models from provider APIs.

**Parameters**:

- `provider`: Optional provider name to filter models.
- `include_status`: If True, includes discovery status/error information.

**Returns**: List of model dicts, or dict with models and status if include_status=True.

---

#### ModelRoutingPort.list_models

```python
list_models(self: Any, provider: Any)
```

List all models, optionally filtered by provider.

**Parameters**:

- `provider`: Optional provider name to filter by.

**Returns**: List of model configurations.

---

#### ModelRoutingPort.remove_common_alias

```python
remove_common_alias(self: Any, alias: str)
```

Remove a common model alias.

**Parameters**:

- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

#### ModelRoutingPort.remove_model_alias

```python
remove_model_alias(self: Any, provider: str, alias: str)
```

Remove a model alias from a provider.

**Parameters**:

- `provider`: Provider name.
- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

#### ModelRoutingPort.validate_provider

```python
validate_provider(self: Any, name: str)
```

Validate a provider by testing connectivity.

**Parameters**:

- `name`: Provider name.

**Returns**: Tuple of (is_valid: bool, message: str, details: dict).

---

---

## add_common_alias

```python
add_common_alias(self: Any, alias: str)
```

Add a common model alias that works across providers.

**Parameters**:

- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

## add_model_alias

```python
add_model_alias(self: Any, provider: str, model: str, alias: str)
```

Add a model alias for a provider.

**Parameters**:

- `provider`: Provider name.
- `model`: Base model name.
- `alias`: The alias to add.

**Returns**: Tuple of (success: bool, message: str).

---

## discover_models

```python
discover_models(self: Any, provider: Any)
```

Discover available models from provider APIs.

**Parameters**:

- `provider`: Optional provider name to filter models.
- `include_status`: If True, includes discovery status/error information.

**Returns**: List of model dicts, or dict with models and status if include_status=True.

---

## list_models

```python
list_models(self: Any, provider: Any)
```

List all models, optionally filtered by provider.

**Parameters**:

- `provider`: Optional provider name to filter by.

**Returns**: List of model configurations.

---

## remove_common_alias

```python
remove_common_alias(self: Any, alias: str)
```

Remove a common model alias.

**Parameters**:

- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

## remove_model_alias

```python
remove_model_alias(self: Any, provider: str, alias: str)
```

Remove a model alias from a provider.

**Parameters**:

- `provider`: Provider name.
- `alias`: The alias to remove.

**Returns**: Tuple of (success: bool, message: str).

---

## validate_provider

```python
validate_provider(self: Any, name: str)
```

Validate a provider by testing connectivity.

**Parameters**:

- `name`: Provider name.

**Returns**: Tuple of (is_valid: bool, message: str, details: dict).

---

