# unified API Reference

> **Source**: `src/thegent/sdk/unified.py`

Unified SDK Facade

Provides a single entry point for all agent/SDK operations.

---

## UnifiedSDK

Unified SDK facade for all agent operations.

### Methods

#### UnifiedSDK.__init__

```python
__init__(self: Any)
```

---

#### UnifiedSDK.call

```python
call(self: Any, adapter_name: str)
```

Call adapter by name

---

#### UnifiedSDK.get_adapter

```python
get_adapter(self: Any, name: str)
```

Get adapter by name

---

#### UnifiedSDK.list_adapters

```python
list_adapters(self: Any)
```

List all registered adapters

---

#### UnifiedSDK.register

```python
register(self: Any, name: str, adapter: AdapterPort)
```

Register a new adapter

---

---

## call

```python
call(self: Any, adapter_name: str)
```

Call adapter by name

---

## call_adapter

```python
call_adapter(name: str)
```

Call adapter by name

---

## get_adapter

```python
get_adapter(self: Any, name: str)
```

Get adapter by name

---

## get_sdk

Get global UnifiedSDK instance

---

## list_adapters

```python
list_adapters(self: Any)
```

List all registered adapters

---

## register

```python
register(self: Any, name: str, adapter: AdapterPort)
```

Register a new adapter

---

