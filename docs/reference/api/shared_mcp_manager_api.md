# shared_mcp_manager API Reference

> **Source**: `src/thegent/shared_mcp_manager.py`

Shared MCP Server Manager (System-Wide First)

Manages system-wide shared MCP servers, scoping down to per-project only when needed.

---

## check_mcp_health

Check health of shared MCP server.
Returns: (is_healthy, status_message)

```python
check_mcp_health(project_root)
```

---

## ensure_shared_mcp_server

Ensure shared MCP server is running (system-wide by default).
Returns: (is_new_server, server_url_or_error)

```python
ensure_shared_mcp_server(project_root)
```

---

## get_server_scope

Determine server scope (system-wide or project-scoped).
Default: system-wide. Scope down only if project requires isolation.

Returns:
    (scope_type, lockfile_path)

```python
get_server_scope(project_root)
```

---

## get_shared_mcp_url

Get URL for shared MCP server (system-wide by default).
Starts server if not running.

```python
get_shared_mcp_url(project_root)
```

---

