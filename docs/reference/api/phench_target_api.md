# phench_target API Reference

> **Source**: `src/thegent/cli/apps/phench_target.py`

Phench target lifecycle commands.

---

## register_target_commands

```python
register_target_commands(target_app: typer.Typer) -> None
```

---

## target_add_repo_cmd

```python
target_add_repo_cmd(name: str, family: Any, repo: str, ref: str, preferred_ref: Any, preferred_runner: Any, preferred_command: Any, repo_id: Any, worktree: Any) -> None
```

---

## target_bootstrap_cmd

```python
target_bootstrap_cmd(name: str, family: Any, mode: str, source_root: Any, ref: str, preferred_runner: Any, preferred_command: Any, preferred_ref: Any, include: list[str], exclude: list[str], repo_ids: list[str], auto_lock: bool) -> None
```

---

## target_import_repos_cmd

```python
target_import_repos_cmd(name: str, family: Any, source_root: Any, ref: str, preferred_runner: Any, preferred_command: Any, preferred_ref: Any, include: list[str], exclude: list[str], repo_ids: list[str], auto_lock: bool) -> None
```

---

## target_init_cmd

```python
target_init_cmd(name: str, family: Any, mode: str) -> None
```

---

## target_lock_cmd

```python
target_lock_cmd(name: str, family: Any) -> None
```

---

## target_materialize_cmd

```python
target_materialize_cmd(name: str, family: Any) -> None
```

---

## target_set_ref_cmd

```python
target_set_ref_cmd(name: str, family: Any, repo_id: str, ref: str) -> None
```

---

