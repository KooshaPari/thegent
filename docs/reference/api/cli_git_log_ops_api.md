# cli_git_log_ops API Reference

> **Source**: `src/thegent/cli/commands/cli_git_log_ops.py`

Thegent Git: log, diff, worktree, and lock-cleanup operations.

Phase 6 / WP-16003: Extracted from cli_git.py for modular management.

---

## diff

```python
diff(project_root: Path, agent_id: str, use_delta: bool)
```

Show changes: compares worktree against private index (or HEAD).

---

## get_agent_id

Return the current agent ID from settings or default.

---

## lock_cleanup_main

```python
lock_cleanup_main(ctx: typer.Context, path: list[Path], max_age: int, dry_run: bool)
```

Remove stale .git/index.lock files.

---

## lock_cleanup_service

```python
lock_cleanup_service(action: str)
```

Install or manage lock-cleanup daemon.

---

## log

```python
log(project_root: Path, limit: int)
```

Show commit log.

---

## register_lock_cleanup_commands

```python
register_lock_cleanup_commands(parent_app: typer.Typer)
```

Register lock-cleanup subcommands to parent app.

---

## register_worktree_commands

```python
register_worktree_commands(parent_app: typer.Typer)
```

Register worktree subcommands to parent app.

---

## worktree_acquire

```python
worktree_acquire(agent_id: str, project_root: Path, target_branch: str, pool_root: Any, json_output: bool)
```

Acquire a pooled worktree for an agent.

---

## worktree_claim

```python
worktree_claim(agent_id: str, project_root: Path, target_branch: str, pool_root: Any, json_output: bool)
```

Alias for acquire, matching coordination-focused terminology.

---

## worktree_cleanup_stale

```python
worktree_cleanup_stale(project_root: Path, target_branch: str, pool_root: Any)
```

Remove stale entries from the worktree pool state.

---

## worktree_list

```python
worktree_list(project_root: Path, target_branch: str, pool_root: Any, json_output: bool)
```

List active worktree agents and their dedicated branch names.

---

## worktree_release

```python
worktree_release(agent_id: str, project_root: Path, target_branch: str, pool_root: Any)
```

Release a pooled worktree and merge changes back to target branch.

---

## worktree_status

```python
worktree_status(project_root: Path, target_branch: str, pool_root: Any, json_output: bool)
```

Show active worktree leases in the pool.

---

