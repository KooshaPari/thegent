# dynamic_tools API Reference

> **Source**: `src/thegent/mcp/dynamic_tools.py`

WL-105 dynamic per-session tool registry primitives.

---

## DynamicToolCallResult

Client-provided output for a prior dynamic tool call.

---

## DynamicToolRegistry

Per-session dynamic tool registration and call lifecycle state.

### Methods

#### DynamicToolRegistry.__init__

```python
__init__(self: Any)
```

---

#### DynamicToolRegistry.clear_session

```python
clear_session(self: Any, session_id: str)
```

---

#### DynamicToolRegistry.create_tool_call

```python
create_tool_call(self: Any, session_id: str, name: str, arguments: dict[(str, Any)], timeout_seconds: Any)
```

---

#### DynamicToolRegistry.get_pending_call

```python
get_pending_call(self: Any, call_id: str)
```

---

#### DynamicToolRegistry.list_dynamic_tools

```python
list_dynamic_tools(self: Any, session_id: str)
```

---

#### DynamicToolRegistry.pending_calls_for_session

```python
pending_calls_for_session(self: Any, session_id: str)
```

---

#### DynamicToolRegistry.register_dynamic_tool

```python
register_dynamic_tool(self: Any, session_id: str, tool_spec: DynamicToolSpec)
```

---

#### DynamicToolRegistry.resolve_tool_call

```python
resolve_tool_call(self: Any, call_id: str, output: Any, success: bool, error: Any)
```

---

#### DynamicToolRegistry.resolve_tool_call_for_session

```python
resolve_tool_call_for_session(self: Any, session_id: str, call_id: str, output: Any, success: bool, error: Any)
```

---

#### DynamicToolRegistry.tool_call_completed_event

```python
tool_call_completed_event(result: DynamicToolCallResult)
```

---

#### DynamicToolRegistry.tool_call_requested_event

```python
tool_call_requested_event(call: PendingDynamicToolCall)
```

---

---

## DynamicToolSpec

Client-registered tool definition bound to a session.

---

## PendingDynamicToolCall

In-flight dynamic tool call awaiting client response.

---

## clear_session

```python
clear_session(self: Any, session_id: str) -> None
```

---

## create_tool_call

```python
create_tool_call(self: Any, session_id: str, name: str, arguments: dict[(str, Any)], timeout_seconds: Any) -> PendingDynamicToolCall
```

---

## get_pending_call

```python
get_pending_call(self: Any, call_id: str) -> PendingDynamicToolCall
```

---

## list_dynamic_tools

```python
list_dynamic_tools(self: Any, session_id: str) -> list[DynamicToolSpec]
```

---

## pending_calls_for_session

```python
pending_calls_for_session(self: Any, session_id: str) -> list[PendingDynamicToolCall]
```

---

## register_dynamic_tool

```python
register_dynamic_tool(self: Any, session_id: str, tool_spec: DynamicToolSpec) -> DynamicToolSpec
```

---

## resolve_tool_call

```python
resolve_tool_call(self: Any, call_id: str, output: Any, success: bool, error: Any) -> DynamicToolCallResult
```

---

## resolve_tool_call_for_session

```python
resolve_tool_call_for_session(self: Any, session_id: str, call_id: str, output: Any, success: bool, error: Any) -> DynamicToolCallResult
```

---

## tool_call_completed_event

```python
tool_call_completed_event(result: DynamicToolCallResult) -> dict[(str, Any)]
```

---

## tool_call_requested_event

```python
tool_call_requested_event(call: PendingDynamicToolCall) -> dict[(str, Any)]
```

---

