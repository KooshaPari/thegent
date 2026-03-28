# rest_to_mcp API Reference

> **Source**: `src/thegent/mcp/rest_to_mcp.py`

GW-66: REST-to-MCP adapter — wrap REST endpoints as MCP tools.

Allows any REST API to be exposed as an MCP tool, enabling LLMs to call
arbitrary HTTP endpoints through the MCP tool calling interface.

# @trace FR-MCP-066

---

## McpAdapter

MCP adapter wrapper for registry

### Methods

#### McpAdapter.__init__

```python
__init__(self: Any)
```

---

#### McpAdapter.call

```python
call(self: Any)
```

---

---

## RestToMcpAdapter

Registry of REST endpoints exposed as MCP tools.

### Methods

#### RestToMcpAdapter.__init__

```python
__init__(self: Any)
```

---

#### RestToMcpAdapter.call

```python
call(self: Any, name: str, arguments: dict)
```

Execute the named REST tool with the given arguments.

Substitutes {param} placeholders in URL, sends HTTP request.
Uses httpx for HTTP. Returns RestToolResult with error set on failure.

---

#### RestToMcpAdapter.get_tool

```python
get_tool(self: Any, name: str)
```

Return the RestToolDef for the given name, or None if not registered.

---

#### RestToMcpAdapter.list_tools

```python
list_tools(self: Any)
```

Return all registered tool definitions.

---

#### RestToMcpAdapter.register

```python
register(self: Any, tool: RestToolDef)
```

Register a REST endpoint as an MCP tool.

---

#### RestToMcpAdapter.to_openai_tools

```python
to_openai_tools(self: Any)
```

Convert registered tools to OpenAI tools format for LLM consumption.

---

#### RestToMcpAdapter.unregister

```python
unregister(self: Any, name: str)
```

Remove a tool. Raises KeyError if not found.

---

---

## RestToolDef

Definition of a REST endpoint exposed as an MCP tool.

---

## RestToolResult

---

## build_openai_tool_def

```python
build_openai_tool_def(tool: RestToolDef)
```

Convert a RestToolDef to OpenAI function calling format.

---

## call

```python
call(self: Any) -> dict
```

---

## get_tool

```python
get_tool(self: Any, name: str)
```

Return the RestToolDef for the given name, or None if not registered.

---

## list_tools

```python
list_tools(self: Any)
```

Return all registered tool definitions.

---

## register

```python
register(self: Any, tool: RestToolDef)
```

Register a REST endpoint as an MCP tool.

---

## to_openai_tools

```python
to_openai_tools(self: Any)
```

Convert registered tools to OpenAI tools format for LLM consumption.

---

## unregister

```python
unregister(self: Any, name: str)
```

Remove a tool. Raises KeyError if not found.

---

