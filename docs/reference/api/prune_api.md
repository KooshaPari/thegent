# prune API Reference

> **Source**: `src/thegent/orchestration/pruning/prune.py`

Pruning and resource management logic.

---

## kill_process

```python
kill_process(pid: int)
```

Kill process with SIGTERM then SIGKILL if needed.

---

## mcp_prune

```python
mcp_prune(force: bool, dry_run: bool, parent_pid: Any, interactive: bool, caller_info: Any)
```

Kill redundant agent-related Node.js processes (LSPs, MCP servers).

**Parameters**:

- `force`: If True, skip interactive prompts (but still protects terminal-attached processes)
- `dry_run`: If True, only show what would be pruned without killing
- `parent_pid`: If set, only prune direct children of this PID
- `interactive`: If True, prompt for terminal-attached processes
- `caller_info`: Optional string identifying what triggered this prune (for logging)

---

## prompt_tty_kill

```python
prompt_tty_kill(pid: int, cmd: str, tty: str)
```

Prompt user on a raw TTY if possible.

---

## show_interactive_prune_menu

```python
show_interactive_prune_menu(pid: int, cmd: str, tty: str, pane: Any)
```

Show a tmux menu for interactive pruning with context.

---

