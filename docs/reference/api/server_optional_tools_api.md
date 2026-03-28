# server_optional_tools API Reference

> **Source**: `src/thegent/mcp/server_optional_tools.py`

Optional MCP tool registrations extracted from server.py.

---

## AgentConfig

**Inherits from**: `BaseModel`

---

## register_optional_tools

Register optional tool/resource blocks with debug-on-failure semantics.

---

## register_storage_event_tools

Register storage/event tool wrappers and return exported callables.

---

## thegent_events_emit

```python
thegent_events_emit(event_type: str, payload: str) -> ToolResult
```

---

## thegent_events_replay

```python
thegent_events_replay(since_id: Any) -> ToolResult
```

---

## thegent_storage_get

```python
thegent_storage_get(key: str) -> ToolResult
```

---

## thegent_storage_set

```python
thegent_storage_set(key: str, value: str, ttl_seconds: Any) -> ToolResult
```

---

