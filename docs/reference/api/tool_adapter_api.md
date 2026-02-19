# tool_adapter API Reference

> **Source**: `src/thegent/agents/tool_adapter.py`

WP-24002: Recursive Tool Discovery & Adaptation.
Enables agents to discover, wrap, and use new tools dynamically at runtime.
Includes automatic interface adaptation for foreign tool protocols.

---

## ToolAdapter

Adapts foreign tool interfaces to thegent's canonical tool protocol.

### Methods

#### ToolAdapter.__init__

```python
__init__(self, agent_id)
```

#### ToolAdapter.discover_tools

Scan a path or endpoint for new tools.

```python
discover_tools(self, target_path)
```

#### ToolAdapter.generate_binding

Generate a Python/JSON binding for the tool to be used in prompts.

```python
generate_binding(self, tool_id)
```

#### ToolAdapter.wrap_tool

Wrap a discovered tool into a standard execution function.

```python
wrap_tool(self, tool_id)
```

---

## ToolDefinition

Metadata for a dynamically discovered tool.

**Inherits from**: `BaseModel`

---

## discover_tools

Scan a path or endpoint for new tools.

```python
discover_tools(self, target_path)
```

---

## generate_binding

Generate a Python/JSON binding for the tool to be used in prompts.

```python
generate_binding(self, tool_id)
```

---

## wrap_tool

Wrap a discovered tool into a standard execution function.

```python
wrap_tool(self, tool_id)
```

---

