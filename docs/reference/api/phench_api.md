# phench API Reference

> **Source**: `src/thegent/cli/apps/phench.py`

Phench: stable project-state runtime control plane for Phenotype/projects.

---

## audit_shared_cmd

```python
audit_shared_cmd(name: str) -> None
```

---

## materialize_module_manifest_cmd

```python
materialize_module_manifest_cmd(module: str, repos_root: Any, repos_root_mode: str, repos: list[str], min_count: int, output_dir: Any, dry_run: bool, print_snippets: bool) -> None
```

---

## scan_shared_repos_cmd

```python
scan_shared_repos_cmd(repos_root: Any, repos_root_mode: str, exclude: list[str], min_repo_count: int, candidate_name_regex: Any, candidates: bool, omit_candidates: bool) -> None
```

---

## status_cmd

```python
status_cmd(name: str) -> None
```

---

## sync_cmd

```python
sync_cmd(name: str, prefer: Any) -> None
```

---

## target_add_module_cmd

```python
target_add_module_cmd(name: str, module: str, selected_ref: Any, exclude: list[str]) -> None
```

---

## target_add_repo_cmd

```python
target_add_repo_cmd(name: str, repo: Path, ref: str, repo_id: Any, worktree: Any) -> None
```

---

## target_init_cmd

```python
target_init_cmd(name: str, mode: str) -> None
```

---

## target_lock_cmd

```python
target_lock_cmd(name: str) -> None
```

---

## target_materialize_cmd

```python
target_materialize_cmd(name: str) -> None
```

---

## tui_cmd

---

