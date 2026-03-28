# infra_env_helpers API Reference

> **Source**: `src/thegent/cli/commands/infra_env_helpers.py`

Helpers for infra command .env updates.

---

## resolve_env_file

```python
resolve_env_file(cwd: Path, module_file: Path)
```

Resolve .env path from cwd or fallback project root relative to module file.

---

## rewrite_max_concurrency_lines

```python
rewrite_max_concurrency_lines(env_lines: list[str], limit: int)
```

Rewrite/add THGENT_MAX_CONCURRENCY assignment.

---

