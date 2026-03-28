# auth API Reference

> **Source**: `src/thegent/mcp/server/auth.py`

Authentication helpers for the MCP server.

---

## BearerAuthMiddleware

G-FM-01: Bearer token authentication for MCP HTTP endpoints.

**Inherits from**: `BaseHTTPMiddleware`

### Methods

#### BearerAuthMiddleware.reload_settings

```python
reload_settings(cls: Any)
```

Reset the cached settings so the next request rebuilds them.

---

---

## get_settings

Return the process-wide ThegentSettings singleton.

---

## reload_settings

```python
reload_settings(cls: Any)
```

Reset the cached settings so the next request rebuilds them.

---

