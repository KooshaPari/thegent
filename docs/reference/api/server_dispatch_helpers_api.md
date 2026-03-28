# server_dispatch_helpers API Reference

> **Source**: `src/thegent/mcp/server_dispatch_helpers.py`

Helper utilities extracted from MCP server dispatch paths.

---

## build_route_request_payload

```python
build_route_request_payload(include_contract: bool, requested_model: Any, requested_provider_hint: Any, policy: Any, resolved_model_alias: Any, resolved_agent: Any)
```

Build route request payload included in background dispatch output.

---

## format_acp_response

Render normalized ACP invoke response payload.

---

## normalize_bg_routing

```python
normalize_bg_routing(routing: Any, default_routing: Any, failover: bool)
```

Normalize requested policy and derive lookup/child routing semantics.

---

## parse_acp_payload

```python
parse_acp_payload(payload: str)
```

Parse ACP payload JSON into context dict.

---

## write_session_control_file

```python
write_session_control_file(session_root: Path, session_id: str, filename: str, content: str)
```

Create a session control file (e.g. takeover/STOP) under session dir.

---

