# git API Reference

> **Source**: `src/thegent/mesh/git.py`

Compatibility wrapper for Git parallelism ops domain module.

---

## GitParallelismManager

Manages parallel git operations using per-agent index files and plumbing (SCLI-P4.1–P4.2).

### Methods

#### GitParallelismManager.__init__

```python
__init__(self: Any, project_root: Path, agent_id: str, mesh_root: Path)
```

---

#### GitParallelismManager.changed_files_between

```python
changed_files_between(self: Any, older: str, newer: str)
```

Return files changed between two refs/hashes.

---

#### GitParallelismManager.create_commit_from_index

```python
create_commit_from_index(self: Any, message: str, parent_ref: str)
```

Build commit from private index with plumbing commands.

---

#### GitParallelismManager.ensure_index

```python
ensure_index(self: Any)
```

Create or refresh the per-agent index file.

---

#### GitParallelismManager.get_agent_status

```python
get_agent_status(self: Any)
```

Show per-agent staged changes.

---

#### GitParallelismManager.index_lock_status

```python
index_lock_status(self: Any, stale_after_s: float)
```

Return index lock state summary.

---

#### GitParallelismManager.queue_commit_conflict

```python
queue_commit_conflict(self: Any, ref: str, reason: str, ours: list[str], theirs: list[str], overlap: list[str], old_hash: Any, new_hash: Any)
```

Append a conflict record to per-project git conflict queue.

---

#### GitParallelismManager.related_overlap

```python
related_overlap(self: Any, ours: list[str], theirs: list[str])
```

Return sorted overlap between two file lists.

---

#### GitParallelismManager.stage_files

```python
stage_files(self: Any, files: list[str])
```

Stage specific files using the agent's index.

---

#### GitParallelismManager.staged_files

```python
staged_files(self: Any)
```

Return staged files from this agent's private index.

---

#### GitParallelismManager.try_auto_merge_commit

```python
try_auto_merge_commit(self: Any, ours_commit: str, theirs_commit: str, message: str)
```

Attempt to create a synthetic 3-way merge commit.

---

#### GitParallelismManager.update_ref_cas

```python
update_ref_cas(self: Any, ref: str, new_hash: str, old_hash: str)
```

Compare-And-Swap ref update with exponential backoff + jitter.

---

#### GitParallelismManager.wait_for_index_lock

```python
wait_for_index_lock(self: Any, timeout_s: float, poll_s: float)
```

Wait briefly for index.lock to clear, optionally cleaning stale locks.

---

---

## changed_files_between

```python
changed_files_between(self: Any, older: str, newer: str)
```

Return files changed between two refs/hashes.

---

## create_commit_from_index

```python
create_commit_from_index(self: Any, message: str, parent_ref: str)
```

Build commit from private index with plumbing commands.

---

## ensure_index

```python
ensure_index(self: Any)
```

Create or refresh the per-agent index file.

---

## get_agent_status

```python
get_agent_status(self: Any)
```

Show per-agent staged changes.

---

## harness_git_status_view

```python
harness_git_status_view(agent_id: str)
```

Display git status for a specific agent.

---

## index_lock_status

```python
index_lock_status(self: Any, stale_after_s: float)
```

Return index lock state summary.

---

## queue_commit_conflict

```python
queue_commit_conflict(self: Any, ref: str, reason: str, ours: list[str], theirs: list[str], overlap: list[str], old_hash: Any, new_hash: Any)
```

Append a conflict record to per-project git conflict queue.

---

## related_overlap

```python
related_overlap(self: Any, ours: list[str], theirs: list[str])
```

Return sorted overlap between two file lists.

---

## stage_files

```python
stage_files(self: Any, files: list[str])
```

Stage specific files using the agent's index.

---

## staged_files

```python
staged_files(self: Any)
```

Return staged files from this agent's private index.

---

## try_auto_merge_commit

```python
try_auto_merge_commit(self: Any, ours_commit: str, theirs_commit: str, message: str)
```

Attempt to create a synthetic 3-way merge commit.

---

## update_ref_cas

```python
update_ref_cas(self: Any, ref: str, new_hash: str, old_hash: str)
```

Compare-And-Swap ref update with exponential backoff + jitter.

---

## wait_for_index_lock

```python
wait_for_index_lock(self: Any, timeout_s: float, poll_s: float)
```

Wait briefly for index.lock to clear, optionally cleaning stale locks.

---

