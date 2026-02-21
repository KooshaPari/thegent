# cli_git API Reference

> **Source**: `src/thegent/cli/commands/cli_git.py`

Overhauled Git CLI for thegent (Phase 6 / WP-16003).

Replaces standard git with multitenancy-aware, parallel-capable commands.
Leverages gix/gitoxide via native binary and private index files.

---

## add

```python
add(files: list[str], agent_id: str, project_root: Path)
```

Add files to the agent's private index (parallel-safe).

---

## callback

```python
callback(ctx: typer.Context)
```

Default handler for unknown commands (pass-through to system git).

---

## commit

```python
commit(message: str, agent_id: str, ref: str, project_root: Path)
```

Create a commit from private index and update ref using atomic CAS.

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

