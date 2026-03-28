# shared_mcp_manager API Reference

> **Source**: `src/thegent/shared_mcp_manager.py`

Shared MCP Server Manager (System-Wide First)

Manages system-wide shared MCP servers, scoping down to per-project only when needed.

---

## check_mcp_health

```python
check_mcp_health(project_root: Any)
```

Check health of shared MCP server.

Returns: (is_healthy, status_message)

---

## ensure_shared_mcp_server

```python
ensure_shared_mcp_server(project_root: Any)
```

Ensure shared MCP server is running (system-wide by default).

Returns: (is_new_server, server_url_or_error)

---

## get_server_scope

```python
get_server_scope(project_root: Any)
```

Determine server scope (system-wide or project-scoped).

Default: system-wide. Scope down only if project requires isolation.

**Returns**: (scope_type, lockfile_path)

---

## get_shared_mcp_url

```python
get_shared_mcp_url(project_root: Any)
```

Get URL for shared MCP server (system-wide by default).

Starts server if not running.

---

