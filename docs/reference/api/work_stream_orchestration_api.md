# work_stream_orchestration API Reference

> **Source**: `src/thegent/cli/services/work_stream_orchestration.py`

Shared work-stream orchestration service for CLI command wrappers.

---

## continuity_snapshot_impl

```python
continuity_snapshot_impl(owner: str, run_ids: list[str], state_summary: Any, next_steps: Any)
```

Create a continuity snapshot for shift handoff (WP-1009).

---

## do_next_impl

```python
do_next_impl(cd: Any, limit: int)
```

Find next actionable work items from work-stream and queue sources.

---

## incorporate_impl

```python
incorporate_impl(cd: Any, dry_run: bool)
```

Merge fragments into WORK_STREAM.md and sync with task files.

---

## spawn_next_impl

```python
spawn_next_impl(cd: Any, limit: int, agent: str, timeout: Any, lane: str, override_reason: str, claim: bool)
```

Spawn next items as background runs.

---

## wait_next_impl

```python
wait_next_impl(cd: Any, poll_interval: float, timeout: float, sources: tuple[(str, Ellipsis)])
```

Poll do-next until an actionable item exists or timeout is reached.

---

## work_stream_claim_impl

```python
work_stream_claim_impl(item_id: str, agent_id: str, cd: Any)
```

Claim a work item (move from BACKLOG to CLAIMED in WORK_STREAM.md).

---

## work_stream_complete_impl

```python
work_stream_complete_impl(item_id: str, agent_id: str, cd: Any)
```

Complete a work item (move from CLAIMED to COMPLETED in WORK_STREAM.md).

---

