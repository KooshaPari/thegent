# manage API Reference

> **Source**: `src/thegent/mcp/manage.py`

MCP configuration and service management for thegent.

---

## install_to_claude_code

```python
install_to_claude_code(url: str)
```

Add thegent to Claude Code config (~/.claude.json).

---

## install_to_claude_desktop

```python
install_to_claude_desktop(url: str)
```

Add thegent to Claude Desktop config (macOS).

---

## install_to_client

```python
install_to_client(client: str, url: str, workspace: Any, replace_all: bool, force_http: bool)
```

Install thegent to given MCP client. Returns (success, message).

---

## install_to_codex

```python
install_to_codex(url: str)
```

Add thegent to Codex MCP config.

---

## install_to_cursor

```python
install_to_cursor(url: str, workspace: Any)
```

Add thegent to Cursor MCP config. Prefers workspace .cursor/mcp.json if present.

---

## install_to_droid

```python
install_to_droid(url: str, workspace: Any)
```

Add thegent to .factory/mcp.json (project-level, for droids/scripts).

---

## mcp_down

Stop MCP + proxy via process-compose. Returns (success, message).

---

## mcp_restart

Restart MCP + proxy via process-compose. Returns (success, message).

---

## mcp_up

```python
mcp_up(reload: bool)
```

Start MCP + proxy via process-compose. Returns (success, message).

---

## migrate_to_unimount

```python
migrate_to_unimount(client: str, mcp_url: str, workspace: Any)
```

Replace ALL MCP server entries with a single thegent entry at mcp_url. Returns (success, message).

---

## prune_periodic_install

Install a periodic prune daemon. Returns (success, message).

---

## prune_periodic_start

Start the periodic prune daemon. Returns (success, message).

---

## prune_periodic_status

Return status of the periodic prune daemon. Returns (success, message).

---

## prune_periodic_stop

Stop the periodic prune daemon. Returns (success, message).

---

## prune_periodic_uninstall

Remove the periodic prune daemon. Returns (success, message).

---

## remove_playwright_from_client

```python
remove_playwright_from_client(client: str, workspace: Any)
```

Shorthand to remove playwright from a single client.

---

## remove_servers_from_client

```python
remove_servers_from_client(client: str, server_names: list[str], workspace: Any)
```

Remove named MCP servers from a client's config. Returns (success, message).

---

## serve_delegate_or_run

```python
serve_delegate_or_run(settings: Any)
```

Check if MCP server should be delegated to a service (launchd/Homebrew) or run directly.

**Returns**: (run_foreground, message) - If run_foreground=True, run in foreground;
otherwise, message indicates delegation success.

---

## service_install

Install thegent MCP as launchd service (macOS).

---

## service_start

Start thegent MCP service.

---

## service_status

```python
service_status(settings: Any)
```

Check if thegent MCP service is running (launchd loaded + HTTP reachable).

---

## service_stop

Stop thegent MCP service.

---

## service_uninstall

Remove launchd service.

---

