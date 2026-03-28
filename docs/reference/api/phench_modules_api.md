# phench_modules API Reference

> **Source**: `src/thegent/cli/apps/phench_modules.py`

Phench module governance commands.

---

## audit_modules_cmd

```python
audit_modules_cmd(source_root: Any, include_repos: Any, exclude_repos: Any, skip_repos: Any, min_repo_count: int, include_modules: Any, exclude_modules: Any, include_repo_modules_root: bool) -> None
```

---

## register_modules_commands

```python
register_modules_commands(modules_app: typer.Typer)
```

Register module-level orchestration commands for phench.

---

## sync_modules_cmd

```python
sync_modules_cmd(source_root: Any, destination_root: Any, include_repos: Any, exclude_repos: Any, include_modules: Any, exclude_modules: Any, overwrite: bool, dry_run: bool) -> None
```

---

