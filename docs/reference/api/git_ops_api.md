# git_ops API Reference

> **Source**: `src/thegent/phench/git_ops.py`

## detect_head_branch

```python
detect_head_branch(checkout_path: Path) -> Any
```

---

## list_timeline

```python
list_timeline(repo_path: Path, limit: int, branch: Any) -> dict[(str, Any)]
```

---

## materialize_repo_checkout

```python
materialize_repo_checkout(source_repo: Path, checkout_path: Path, resolved_sha: str) -> None
```

---

## resolve_ref_to_sha

```python
resolve_ref_to_sha(repo_path: Path, ref: str) -> str
```

---

## run_git

```python
run_git(repo_path: Path, args: list[str]) -> str
```

---

## sanitize_repo_id

```python
sanitize_repo_id(value: str) -> str
```

---

