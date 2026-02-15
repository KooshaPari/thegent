# FastMCP Middleware

**Source:** gofastmcp.com/servers/middleware  
**Date:** 2026-02-14  
**Purpose:** Extract add_middleware order, ResponseCachingMiddleware, RateLimitingMiddleware, on_call_tool hook for thegent_run.

---

## 1. add_middleware Order

Middleware executes in **order added**. First added = outermost (runs first in, last out).

```python
mcp.add_middleware(ErrorHandlingMiddleware())   # 1st in, last out
mcp.add_middleware(RateLimitingMiddleware())   # 2nd in, 2nd out
mcp.add_middleware(TimingMiddleware())        # 3rd in, first out
mcp.add_middleware(LoggingMiddleware())        # 4th in, first out
```

**Recommended order:** ErrorHandling → RateLimiting → Timing → Logging (first added = outermost).

---

## 2. ResponseCachingMiddleware

```python
from fastmcp.server.middleware.caching import (
    ResponseCachingMiddleware,
    CallToolSettings,
    ListToolsSettings,
    ReadResourceSettings,
)

mcp.add_middleware(ResponseCachingMiddleware(
    list_tools_settings=ListToolsSettings(ttl=30),
    call_tool_settings=CallToolSettings(included_tools=["expensive_tool"]),
    read_resource_settings=ReadResourceSettings(enabled=False)
))
```

### Settings Classes

| Settings Class | Configures |
|----------------|------------|
| ListToolsSettings | on_list_tools caching |
| CallToolSettings | on_call_tool caching |
| ListResourcesSettings | on_list_resources caching |
| ReadResourceSettings | on_read_resource caching |
| ListPromptsSettings | on_list_prompts caching |
| GetPromptSettings | on_get_prompt caching |

### Per-settings options

- `included_*` / `excluded_*` — Whitelist or blacklist
- `ttl` — Time-to-live in seconds
- `enabled` — Enable/disable caching for this operation

### thegent mapping

- `ListToolsSettings(ttl=30)` — cache tools/list
- `CallToolSettings(included_tools=["thegent_ps", "thegent_list_agents", "thegent_list_droids", "thegent_list_models"])` — cache read-heavy tools
- `ReadResourceSettings` — cache thegent://sessions, thegent://session/{id}/meta

### Storage for persistence

```python
from key_value.aio.stores.disk import DiskStore
mcp.add_middleware(ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="cache")
))
```

---

## 3. RateLimitingMiddleware

```python
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

mcp.add_middleware(RateLimitingMiddleware(
    max_requests_per_second=10.0,
    burst_capacity=20
))
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_requests_per_second | float | 10.0 | Sustained request rate |
| burst_capacity | int | 20 | Maximum burst size |
| client_id_func | Callable | None | Custom client identification |

**thegent:** `max_requests_per_second=10`, `burst_capacity=20` to protect thegent_run from abuse.

---

## 4. on_call_tool Hook

```python
async def on_call_tool(self, context: MiddlewareContext, call_next):
    tool_name = context.message.name
    args = context.message.arguments
    result = await call_next(context)
    return result
```

### MiddlewareContext

| Attribute | Type | Description |
|-----------|------|-------------|
| method | str | MCP method (e.g. "tools/call") |
| message.name | str | Tool name |
| message.arguments | dict | Tool arguments |
| fastmcp_context | Context | FastMCP context (if available) |

### thegent_run hook

Use `on_call_tool` to:
- Log `thegent_run` invocations
- Rate-limit or throttle thegent_run specifically
- Enrich ToolResult with metadata

---

## 5. ResponseLimitingMiddleware

```python
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

mcp.add_middleware(ResponseLimitingMiddleware(max_size=500_000))
```

For `thegent_logs` — limit response size to avoid context overflow.

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_size | 1_000_000 | Max response size in bytes |
| tools | None | Limit only these tools (None = all) |

---

## 6. Built-in Middleware Summary

| Middleware | Purpose |
|------------|---------|
| ErrorHandlingMiddleware | Centralized error logging |
| RateLimitingMiddleware | Token bucket rate limit |
| TimingMiddleware | Execution duration |
| LoggingMiddleware | Request/response logging |
| StructuredLoggingMiddleware | JSON logs |
| ResponseCachingMiddleware | Cache tool/resource/prompt calls |
| ResponseLimitingMiddleware | Truncate large responses |
| PingMiddleware | Keep connections alive |

---

## 7. thegent Production Pipeline

```python
mcp.add_middleware(ErrorHandlingMiddleware())
mcp.add_middleware(RateLimitingMiddleware(max_requests_per_second=10, burst_capacity=20))
mcp.add_middleware(TimingMiddleware())
mcp.add_middleware(ResponseCachingMiddleware(
    call_tool_settings=CallToolSettings(
        included_tools=["thegent_ps", "thegent_list_agents", "thegent_list_droids", "thegent_list_models"],
        ttl=30
    )
))
mcp.add_middleware(ResponseLimitingMiddleware(max_size=500_000))
mcp.add_middleware(LoggingMiddleware())
```
