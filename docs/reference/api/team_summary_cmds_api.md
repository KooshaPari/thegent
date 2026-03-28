# team_summary_cmds API Reference

> **Source**: `src/thegent/cli/commands/team/team_summary_cmds.py`

Thegent CLI summary and teammates commands (extracted from team_cmds.py).

---

## summary_cmd

```python
summary_cmd(period: str, project: Any, summarize: bool, agent: str, full: bool, format: Any)
```

FR-X09: Unified summary and audit log across runs, chats, and commits.

---

## teammates_delegate_cmd

```python
teammates_delegate_cmd(teammate_id: str, prompt: str, parent_run_id: str)
```

WP-16002: Delegate a sub-task to a specialized teammate.

---

## teammates_list_cmd

WP-16001: List all discovered specialized agents available for delegation.

---

## teammates_status_cmd

```python
teammates_status_cmd(run_id: str)
```

WP-16002: Monitor the status of the teammate swarm.

---

