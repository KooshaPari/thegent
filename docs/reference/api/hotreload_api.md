# hotreload API Reference

> **Source**: `src/thegent/mcp/hotreload.py`

Production hot-reload supervisor for MCP + proxy.

Watches project source/config files and triggers a process-compose restart
when relevant files change.

---

## run_prod_hotreload

```python
run_prod_hotreload(project_root: Any, debounce_s: float)
```

Run a blocking watch loop and restart MCP stack on relevant changes.

---

