# mgmt_manage API Reference

> **Source**: `src/thegent/mgmt_manage.py`

Management commands for agent self-service: ensure proxy, verify Codex+CLIProxy.

---

## ensure_proxy

Ensure MCP + proxy are running. Starts via process-compose if needed.

Returns (success, message).

```python
ensure_proxy(timeout_sec)
```

---

## verify_codex_cliproxy

Verify Codex works with CLIProxy adapter.

1. Ensures proxy is up (mcp up if needed)
2. Runs `codex exec` against proxy
3. Returns (success, message)

Requires: codex CLI installed (npm i -g @openai/codex).

```python
verify_codex_cliproxy(model, prompt, timeout_sec)
```

---

