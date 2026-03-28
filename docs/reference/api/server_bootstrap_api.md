# server_bootstrap API Reference

> **Source**: `src/thegent/mcp/server_bootstrap.py`

Bootstrap helpers for the MCP server extraction surface (WL-120).

---

## build_elicitation_helpers

Build server-compatible helper callables and cache instance.

---

## build_lifespan

Build the FastMCP lifespan function with injected lifecycle dependencies.

---

## get_default_cwd

```python
get_default_cwd(ctx: Any) -> Any
```

---

## get_default_owner

```python
get_default_owner(ctx: Any) -> Any
```

---

## load_auth

```python
load_auth(load_module: Any)
```

Load the auth helper module from server/auth.py.

---

## load_lifecycle

```python
load_lifecycle(load_module: Any)
```

Load the lifecycle helper module from server/lifecycle.py.

---

