# tools_harness API Reference

> **Source**: `src/thegent/mcp/server/tools_harness.py`

Harness interaction tool handlers for MCP server.

---

## harness_get_command_impl

Get the command template for a harness-action pair.

**Parameters**:

- `harness`: Harness type
- `action`: Abstract action

**Returns**: JSON string with command template or error

---

## harness_interact_impl

Execute a harness action via HarnessTUIMapper.

**Parameters**:

- `harness`: Harness type (cursor, codex, claude, ante, droid)
- `action`: Abstract action (send_message, attach_terminal, view_history, etc.)
- `host_id`: Optional remote host identifier
- `prompt`: Prompt/message for send_message action
- `session_id`: Session ID for session-related actions

**Returns**: JSON string with success status, output, and any errors

---

## harness_list_actions_impl

List all available harness actions.

**Returns**: JSON string with list of available actions

---

## harness_register_host_impl

Register a new host device with custom command mappings.

**Parameters**:

- `host_id`: Unique identifier for the host
- `harness`: The harness type this host uses
- `command_prefix`: Prefix for all commands (e.g., "ssh user@host")
- `custom_actions`: Override commands for specific actions

**Returns**: JSON string with registration status

---

## register_harness_tools

```python
register_harness_tools(mcp: Any, server_tools_harness: Any)
```

Register harness interaction tools with the MCP server.

**Returns**: Tuple of (thegent_harness_interact, thegent_harness_list_actions,
thegent_harness_get_command, thegent_harness_register_host)

---

