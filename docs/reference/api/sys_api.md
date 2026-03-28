# sys API Reference

> **Source**: `src/thegent/cli/apps/sys.py`

Logical stream: System and Lifecycle Operations.

---

## setup_app_callback

```python
setup_app_callback(ctx: typer.Context)
```

Interactive system setup when no subcommand is given.

---

## sys_config

```python
sys_config(action: str, key: Any, value: Any)
```

---

## sys_cp

```python
sys_cp(action: str)
```

---

## sys_lsp

```python
sys_lsp(action: str, language: Any)
```

---

## sys_mcp

```python
sys_mcp(action: str, server: Any, command: Any, force: bool, dry_run: bool, parent_pid: Any, shadow_age_hours: int, log_age_days: int)
```

---

## sys_session

```python
sys_session(action: str, session_id: Any)
```

---

## sys_shadow

```python
sys_shadow(action: str, path: str)
```

Manage git shadow worktrees.

Shadows use git worktrees (NOT file copying) for efficient isolation.
- Active worktrees share .git objects (no disk duplication)
- Orphaned directories are cleaned up on demand

Actions:
    status  - Show current shadow worktree status
    cleanup - Remove orphaned shadow directories
    stats   - Detailed statistics about shadows

---

## sys_terminal

```python
sys_terminal(action: str, name: Any)
```

---

