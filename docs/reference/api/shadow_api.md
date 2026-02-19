# shadow API Reference

> **Source**: `src/thegent/orchestration/shadow.py`

## ShadowWorkspace

MTSP-12: Shadow Workspace for isolated planning and testing.
Uses git worktree for a true isolated branch/workspace, or symlink-shadow as fallback.

### Methods

#### ShadowWorkspace.__init__

```python
__init__(self, project_root, shadow_id)
```

#### ShadowWorkspace.create

Create a shadow workspace using git worktree.

```python
create(self, branch)
```

#### ShadowWorkspace.destroy

Destroy the shadow workspace and clean up git references.

```python
destroy(self)
```

#### ShadowWorkspace.run

Run a command within the shadow workspace.

```python
run(self, cmd)
```

---

## create

Create a shadow workspace using git worktree.

```python
create(self, branch)
```

---

## destroy

Destroy the shadow workspace and clean up git references.

```python
destroy(self)
```

---

## run

Run a command within the shadow workspace.

```python
run(self, cmd)
```

---

