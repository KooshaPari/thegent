# universal_adapter API Reference

> **Source**: `src/thegent/tools/universal_adapter.py`

WP-9005: Universal tool adapter layer.

Maps direct tool calls to unified operation envelopes with validation.

---

## UniversalToolAdapter

Adapts disparate tools to the unified operation surface.

### Methods

#### UniversalToolAdapter.__init__

```python
__init__(self)
```

#### UniversalToolAdapter.call_tool

Call a tool through its operation-mapped adapter.

```python
call_tool(self, command)
```

#### UniversalToolAdapter.register_adapter

Register an adapter for a specific CLI command.

```python
register_adapter(self, command, adapter_fn)
```

---

## call_tool

Call a tool through its operation-mapped adapter.

```python
call_tool(self, command)
```

---

## register_adapter

Register an adapter for a specific CLI command.

```python
register_adapter(self, command, adapter_fn)
```

---

## validate_tool_schema

WP-9005: Validate tool call payload against operation-specific schema.

```python
validate_tool_schema(operation, payload)
```

---

