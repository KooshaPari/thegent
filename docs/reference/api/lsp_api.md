# lsp API Reference

> **Source**: `src/thegent/cli/apps/lsp.py`

LSP and JetBrains MCP tools management.

---

## jetbrains_mcp_tools

```python
jetbrains_mcp_tools(list_tools: bool, status: bool, test: bool)
```

List available JetBrains MCP tools and their status.

---

## lsp_list

List all available LSP servers.

---

## lsp_prune

Stop all LSP server processes.

---

## lsp_restart

```python
lsp_restart(language: str)
```

Restart an LSP server.

---

