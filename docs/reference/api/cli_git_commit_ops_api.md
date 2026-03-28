# cli_git_commit_ops API Reference

> **Source**: `src/thegent/cli/commands/cli_git_commit_ops.py`

Thegent Git: commit, add, merge, and status operations.

Phase 6 / WP-16003: Extracted from cli_git.py for modular management.

---

## add

```python
add(files: list[str], agent_id: str, project_root: Path)
```

Add files to the agent's private index (parallel-safe).

---

## commit

```python
commit(message: str, agent_id: str, actor_profile: Any, ref: str, project_root: Path, lock_timeout: float, stale_after_s: float, allow_stale_cleanup: bool)
```

Create a commit from private index and update ref using atomic CAS.

---

## get_agent_id

Return the current agent ID from settings or default.

---

## lock_status

```python
lock_status(project_root: Path, stale_after_s: float, json_output: bool)
```

Inspect current `.git/index.lock` state.

---

## merge

```python
merge(base: Path, ours: Path, theirs: Path, output: Path)
```

AST-aware merge using Mergiraf (Phase 7).

---

## run_system_git

```python
run_system_git(args: list[str])
```

Fallback: run the actual git binary.

---

## status

```python
status(agent_id: str, project_root: Path, short: bool)
```

Show status: combines private index (staged) and worktree (modified).

---

