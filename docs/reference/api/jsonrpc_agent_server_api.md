# jsonrpc_agent_server API Reference

> **Source**: `src/thegent/protocols/jsonrpc_agent_server.py`

In-memory JSON-RPC 2.0 agent server over stdio.

---

## InMemoryJsonRpcState

### Methods

#### InMemoryJsonRpcState.next_approval_id

```python
next_approval_id(self: Any)
```

---

#### InMemoryJsonRpcState.next_session_id

```python
next_session_id(self: Any)
```

---

#### InMemoryJsonRpcState.next_tool_call_id

```python
next_tool_call_id(self: Any)
```

---

#### InMemoryJsonRpcState.next_turn_id

```python
next_turn_id(self: Any)
```

---

---

## JsonRpcError

**Inherits from**: `SerializableMixin`

### Methods

#### JsonRpcError.to_dict

```python
to_dict(self: Any)
```

Override to conditionally include data field.

---

---

## main

---

## next_approval_id

```python
next_approval_id(self: Any) -> str
```

---

## next_session_id

```python
next_session_id(self: Any) -> str
```

---

## next_tool_call_id

```python
next_tool_call_id(self: Any) -> str
```

---

## next_turn_id

```python
next_turn_id(self: Any) -> str
```

---

## process_jsonrpc_line

```python
process_jsonrpc_line(raw_line: str)
```

Parse a single JSONL request and return response payload.

---

## process_jsonrpc_line_full

```python
process_jsonrpc_line_full(raw_line: str)
```

Parse and fully process a single JSONL request, including notifications.

---

## serve_stdio

```python
serve_stdio(in_stream: Any, out_stream: Any)
```

Run the daemon in newline-delimited JSON-RPC mode over stdio.

---

## to_dict

```python
to_dict(self: Any)
```

Override to conditionally include data field.

---

