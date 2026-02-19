# prune_utils API Reference

> **Source**: `src/thegent/prune_utils.py`

Orphan detection for prune (orphan-by-ppid).

---

## is_agent_in_cmd

True if command indicates Cursor/Claude/Codex (agent parent).

```python
is_agent_in_cmd(cmd)
```

---

## is_orphan_by_ppid

True if process has no Cursor/Claude/Codex in parent chain (true orphan).

```python
is_orphan_by_ppid(pid, parent_map, cmd_map)
```

---

