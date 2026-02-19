# mcp_manage API Reference

> **Source**: `src/thegent/mcp_manage.py`

MCP configuration and service management for thegent.

---

## install_to_claude_code

Add thegent to Claude Code config (~/.claude.json).

```python
install_to_claude_code(url)
```

---

## install_to_claude_desktop

Add thegent to Claude Desktop config (macOS).

```python
install_to_claude_desktop(url)
```

---

## install_to_client

Install thegent to given MCP client. Returns (success, message).

```python
install_to_client(client, url, workspace)
```

---

## install_to_codex

Add thegent to Codex MCP config.

```python
install_to_codex(url)
```

---

## install_to_cursor

Add thegent to Cursor MCP config. Prefers workspace .cursor/mcp.json if present.

```python
install_to_cursor(url, workspace)
```

---

## install_to_droid

Add thegent to .factory/mcp.json (project-level, for droids/scripts).

```python
install_to_droid(url, workspace)
```

---

## mcp_down

Stop MCP + proxy via process-compose. Returns (success, message).

---

## mcp_up

Start MCP + proxy via process-compose. Returns (success, message).

---

## service_install

Install thegent MCP as launchd service (macOS).

---

## service_start

Start thegent MCP service.

---

## service_status

Check if thegent MCP service is running (launchd loaded + HTTP reachable).

```python
service_status(settings)
```

---

## service_stop

Stop thegent MCP service.

---

## service_uninstall

Remove launchd service.

---

