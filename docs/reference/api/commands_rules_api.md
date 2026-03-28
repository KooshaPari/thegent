# commands_rules API Reference

> **Source**: `src/thegent/cli/commands/models/commands_rules.py`

Thegent CLI model listing and rules sync - extracted from model_cmds_config.py.

Lists available models across providers (Claude, Codex, Cursor, Copilot, Gemini, etc.).
Provides cliproxy login delegation and model contract schema inspection.

---

## cliproxy_login_cmd

```python
cliproxy_login_cmd(provider: str, force: bool)
```

Run provider login by delegating to cliproxyctl machine JSON surface.

---

## list_model_contract_schema_cmd

Print the route contract schema metadata used by contract views.

---

