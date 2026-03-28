# team_cmds API Reference

> **Source**: `src/thegent/cli/commands/team/team_cmds.py`

Thegent CLI team/handoff commands - re-export facade (extracted from cli.py).

This module is a thin re-export facade for command groups extracted to focused modules:
- team_snapshot_cmds: Session snapshot management
- team_dump_cmds: Conversation dump management
- team_analysis_cmds: Run explanation and fallback analysis
- team_handoff_cmds: Shift handoff and continuity
- team_monitoring_cmds: Watchdog, DLQ, traffic, roadmap, self-heal
- team_summary_cmds: Summary and teammates commands

---

## project_list_cmd

```python
project_list_cmd(format: Any)
```

Backward-compatible wrapper for extracted project command group.

---

## project_register_cmd

```python
project_register_cmd(path: Any, name: Any)
```

Backward-compatible wrapper for extracted project command group.

---

## queue_list_cmd

```python
queue_list_cmd(watch: bool)
```

WP-7002: List pending prompts in the queue.

---

## recover_status_cmd

Backward-compatible wrapper for extracted recovery command group.

---

## team_create_cmd

```python
team_create_cmd(name: str, leader: Any, teammates: Any)
```

Backward-compatible wrapper for extracted team command group.

---

## team_task_add_cmd

```python
team_task_add_cmd(team_id: str, title: str, description: str)
```

Backward-compatible wrapper for extracted team command group.

---

## team_task_list_cmd

```python
team_task_list_cmd(team_id: str)
```

Backward-compatible wrapper for extracted team command group.

---

