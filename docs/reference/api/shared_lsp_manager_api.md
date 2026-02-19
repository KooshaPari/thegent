# shared_lsp_manager API Reference

> **Source**: `src/thegent/shared_lsp_manager.py`

Shared LSP Server Manager (System-Wide First)

Manages system-wide shared LSP servers, scoping down to per-project only when needed.

---

## ensure_shared_lsp_server

Ensure shared LSP server is running (system-wide by default).
Returns: stdio pipe path or socket path or None

```python
ensure_shared_lsp_server(project_root, language)
```

---

## get_lsp_server_scope

Determine LSP server scope (system-wide or project-scoped).
Default: system-wide. Scope down only if project requires isolation.

Returns:
    (scope_type, lockfile_path)

```python
get_lsp_server_scope(project_root, language)
```

---

