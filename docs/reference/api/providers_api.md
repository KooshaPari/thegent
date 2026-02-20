# providers API Reference

> **Source**: `src/thegent/governance/providers.py`

Provider registry for economic governance (WP-5003).

Centralized registry of provider configurations with fallback chains
and cost/reliability metadata for routing decisions.

See: docs/changes/research-economic-governance/design.md § 2.1

---

## ProviderConfig

Provider configuration.

---

## ProviderRegistry

Centralized provider configuration and lookup.

Manages provider definitions, routing metadata, and fallback chains.
Implements singleton pattern with class-level registry.

### Methods

#### ProviderRegistry.clear

```python
clear(cls: Any)
```

Clear all registered providers (for testing).

WARNING: This should only be called during tests.

---

#### ProviderRegistry.count

```python
count(cls: Any)
```

Get number of registered providers.

**Returns**: Provider count

---

#### ProviderRegistry.get

```python
get(cls: Any, provider_id: str)
```

Get provider configuration by ID.

**Parameters**:

- `provider_id`: Provider identifier

**Returns**: Provider config or None if not found

---

#### ProviderRegistry.get_fallback_order

```python
get_fallback_order(cls: Any, provider_id: str)
```

Get fallback chain for a provider.

**Parameters**:

- `provider_id`: Provider identifier

**Returns**: Ordered list of fallback provider IDs

---

#### ProviderRegistry.list_providers

```python
list_providers(cls: Any)
```

List all registered providers.

**Returns**: List of provider configurations

---

#### ProviderRegistry.register

```python
register(cls: Any, config: ProviderConfig)
```

Register a provider configuration.

**Parameters**:

- `config`: Provider configuration

---

#### ProviderRegistry.unregister

```python
unregister(cls: Any, provider_id: str)
```

Unregister a provider (for testing).

**Parameters**:

- `provider_id`: Provider identifier to remove

---

---

## ProviderType

Provider deployment type.

**Inherits from**: `Enum`

---

## clear

```python
clear(cls: Any)
```

Clear all registered providers (for testing).

WARNING: This should only be called during tests.

---

## count

```python
count(cls: Any)
```

Get number of registered providers.

**Returns**: Provider count

---

## get

```python
get(cls: Any, provider_id: str)
```

Get provider configuration by ID.

**Parameters**:

- `provider_id`: Provider identifier

**Returns**: Provider config or None if not found

---

## get_fallback_order

```python
get_fallback_order(cls: Any, provider_id: str)
```

Get fallback chain for a provider.

**Parameters**:

- `provider_id`: Provider identifier

**Returns**: Ordered list of fallback provider IDs

---

## list_providers

```python
list_providers(cls: Any)
```

List all registered providers.

**Returns**: List of provider configurations

---

## register

```python
register(cls: Any, config: ProviderConfig)
```

Register a provider configuration.

**Parameters**:

- `config`: Provider configuration

---

## unregister

```python
unregister(cls: Any, provider_id: str)
```

Unregister a provider (for testing).

**Parameters**:

- `provider_id`: Provider identifier to remove

---

