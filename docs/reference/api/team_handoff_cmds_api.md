# team_handoff_cmds API Reference

> **Source**: `src/thegent/cli/commands/team/team_handoff_cmds.py`

Thegent CLI handoff and continuity commands (extracted from team_cmds.py).

---

## handoff_cmd

```python
handoff_cmd(owner: str)
```

Create a continuity snapshot for a shift handoff (WP-4006, WP-3008).

---

## handoff_confirm_cmd

```python
handoff_confirm_cmd(snapshot_id: str, incoming_owner: str, confidence: float)
```

Incoming owner confirms handoff completeness (WP-3008, WP-4006).

---

## handoff_list_cmd

```python
handoff_list_cmd(limit: int, format: Any)
```

List pending handoff snapshots (WP-4006).

---

## handoff_show_cmd

```python
handoff_show_cmd(snapshot_id: str, format: Any)
```

Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006).

---

