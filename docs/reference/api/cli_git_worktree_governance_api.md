# cli_git_worktree_governance API Reference

> **Source**: `src/thegent/cli/governance/cli_git_worktree_governance.py`

Structured worktree governance CLI passthrough.

---

## register_worktree_governance_commands

```python
register_worktree_governance_commands(parent_app: typer.Typer)
```

Register the structured worktree governance namespace.

---

## run_worktree_governance_script

```python
run_worktree_governance_script(project_root: Path)
```

Run the canonical worktree governance script and return the completed process.

---

## worktree_governance_check

```python
worktree_governance_check(root: Any)
```

Validate the structured worktree inventory.

---

## worktree_governance_list

```python
worktree_governance_list(root: Any)
```

List structured worktrees.

---

## worktree_governance_migrate_legacy

```python
worktree_governance_migrate_legacy(legacy_path: Path, domain: str, scale: str, change_anchor: str, state: str, root: Any)
```

Migrate a legacy worktree into the canonical structured root.

---

## worktree_governance_new

```python
worktree_governance_new(domain: str, scale: str, change_anchor: str, start_point: str, root: Any)
```

Create a structured worktree.

---

## worktree_governance_path

```python
worktree_governance_path(domain: str, scale: str, change_anchor: str, state: str, root: Any)
```

Print the canonical structured path for a worktree.

---

## worktree_governance_prune

```python
worktree_governance_prune(dry_run: bool, root: Any)
```

Prune done or broken worktrees.

---

## worktree_governance_refresh

```python
worktree_governance_refresh(change_anchor: str, remote: str, upstream_ref: Any, strategy: Literal[(rebase, merge)], root: Any)
```

Fetch and refresh a structured worktree against an upstream branch.

---

## worktree_governance_state

```python
worktree_governance_state(change_anchor: str, new_state: str, root: Any)
```

Move a worktree between lifecycle states.

---

