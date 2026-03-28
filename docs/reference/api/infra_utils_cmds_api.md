# infra_utils_cmds API Reference

> **Source**: `src/thegent/cli/commands/infra_utils_cmds.py`

Thegent CLI utility commands (archive, purge, context, scratchpad, explorer) - extracted from infra_cmds.py.

---

## archive_cmd

```python
archive_cmd(days: Any, domain: Any, tier: Any)
```

Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr).

---

## config_check_cmd

```python
config_check_cmd(format: Any)
```

Validate config and report issues (DX-010, ROB-013).

---

## context_history_cmd

```python
context_history_cmd(query: Any, task_id: Any, cwd: Any, limit: int)
```

Search and display context-aware shell history.

---

## explorer_cmd

Launch the terminal explorer TUI.

---

## interruption_list_cmd

```python
interruption_list_cmd(limit: int, format: Any)
```

List recent interruptions (WP-4004).

---

## interruption_snooze_cmd

```python
interruption_snooze_cmd(alert_id: str, minutes: int, itype: str)
```

Snooze an alert; expires → auto-escalation (WP-4004).

---

## purge_cmd

```python
purge_cmd(dry_run: bool)
```

WP-3006: Tiered retention purge (G-GP-07).

---

## scratchpad_cmd

```python
scratchpad_cmd(action: str, content: Any)
```

Manage the AI command drafting scratchpad.

---

