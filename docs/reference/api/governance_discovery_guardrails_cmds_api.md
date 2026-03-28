# governance_discovery_guardrails_cmds API Reference

> **Source**: `src/thegent/cli/governance/governance_discovery_guardrails_cmds.py`

Governance discovery and guardrails commands (WL-124).

This module handles guardrails enforcement and discovery of external agents
and governance-relevant code patterns.

---

## discovery_parse_cmd

```python
discovery_parse_cmd(text: str, register: bool, ppid: int)
```

Parse CLI output for session information and register them.

---

## discovery_register_cmd

```python
discovery_register_cmd(agent: str, pid: int, ppid: int, cwd: str, command: Any, args: Any, session_id: Any, token_usage_json: Any, mcp_errors: Any)
```

Register or update a discovered external agent (WP-4008).

---

## discovery_scan_cmd

```python
discovery_scan_cmd(format: Any)
```

Scan process tree for agent CLI sessions and auto-register them.

Detects running cursor-agent, Claude Code, and Codex processes,
extracts session IDs from --resume= when present, and registers them
for introspection via thegent ps, terminal takeover, and inbox.

---

## guardrails_check_cmd

```python
guardrails_check_cmd(prompt: str, agent: Any, model: Any)
```

Check a prompt against active guardrails (FR-GOV-003..006).

---

## guardrails_show_cmd

Show active guardrail configuration (FR-GOV-007).

---

