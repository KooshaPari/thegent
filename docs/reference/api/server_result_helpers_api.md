# server_result_helpers API Reference

> **Source**: `src/thegent/mcp/server_result_helpers.py`

Shared result helpers for MCP server tool/resource responses (WL-126).

---

## error_result

```python
error_result(error: str, remediation: str, exit_code: int, extra: Any)
```

Return ToolResult with error, remediation, and structured_content (MCP-OPT §5).

---

## stable_json

```python
stable_json(payload: Any)
```

Serialize dict/list payloads with stable key order for deterministic MCP transport.

---

