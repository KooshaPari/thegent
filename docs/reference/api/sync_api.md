# sync API Reference

> **Source**: `src/thegent/cli/apps/sync.py`

Logical stream: System State Synchronization.

# @trace WL-037

---

## sync_all

```python
sync_all(components: Any, force: bool, dry_run: bool, format: str)
```

---

## sync_audit

```python
sync_audit(format: str, project: Any, policy_path: Any)
```

``thegent sync audit`` — validate runtime behavior against sync-policy contract.

Prints current sync policies (enabled connectors, quota budgets, policy modes)
as JSON or formatted table.

# @trace WL-261

---

## sync_autopilot

```python
sync_autopilot(subcommand: str, once: bool, interval: int, dry_run: bool, area: Any, status: Any, priority: Any, wl_range: Any, remote_missing_item_policy: Any, output_format: str, bootstrap_required: list[str], bootstrap_map: list[str], bootstrap_connector: str, simulation_mode: bool, offline: bool, snapshot_retention_count: Any, artifact_encryption: bool, artifact_encryption_key: str)
```

``thegent sync autopilot`` — run automatic workstream reflection.

Continuously reflects local WORK_STREAM.md status to GitHub Projects and Linear,
and pulls remote status updates back to local markdown. Enable by setting:
    - THGENT_WORKSTREAM_AUTOSYNC_ENABLED=true
    - THGENT_GITHUB_ENABLED=true + THGENT_GITHUB_OWNER + THGENT_GITHUB_PROJECT_NUMBER
    - OR THGENT_LINEAR_ENABLED=true + THGENT_LINEAR_API_KEY + THGENT_LINEAR_TEAM_KEY

# @trace WL-160

---

## sync_autopilot_status

```python
sync_autopilot_status(format: str)
```

``thegent sync autopilot-status`` — query autopilot status.

Reads from autosync_status.json if it exists and displays health summary.

# @trace WL-171

---

## sync_board

```python
sync_board(board_id: Any, source: Any, dry_run: bool, shadow_mode: bool, wl_start: Any, wl_end: Any, write_batch_size: int, project: Any)
```

``thegent sync board`` — synchronize cross-repo board state.

Operationalize repeatable board update/import flow using native tooling.
Syncs local WORK_STREAM.md status with GitHub Projects or Linear issues.

# @trace WL-159

---

## sync_board_migrate

```python
sync_board_migrate(legacy_ids: list[str], dry_run: bool, project: Any)
```

---

## sync_bootstrap_github

```python
sync_bootstrap_github(owner: str, repo: str, project_title: str, dry_run: bool)
```

Run `scripts/bootstrap_sync_workflow_project.py` via an in-process module load.

---

## sync_catalog

```python
sync_catalog(force: bool)
```

---

## sync_conflicts

```python
sync_conflicts(queue_file: Path)
```

---

## sync_dag

```python
sync_dag(force: bool)
```

---

## sync_dead_letter_queue

```python
sync_dead_letter_queue(source: Any, board_id: Any, limit: int, output_format: str, project: Any)
```

``thegent sync dead-letter-queue`` — inspect replay queue candidates.

Read-only command that reports pending queue records and due replay candidates.

# @trace WL-331

---

## sync_dead_letter_replay

```python
sync_dead_letter_replay(source: Any, board_id: Any, limit: int, dry_run: bool, project: Any)
```

``thegent sync dead-letter-replay`` — replay pending remote-write dead letters.

# @trace WL-214

---

## sync_freeze

```python
sync_freeze(reason: str, actor: str, state_file: Path)
```

---

## sync_ga_readiness

```python
sync_ga_readiness(format: str)
```

---

## sync_health

```python
sync_health(entry: list[str])
```

---

## sync_local_orphans

```python
sync_local_orphans(mapping_cache: Path, project: Any)
```

---

## sync_pull

```python
sync_pull(source: Any, project: Any)
```

``thegent sync pull`` — pull remote state to local.

# @trace FR-SYNC-040

---

## sync_push

```python
sync_push(target: Any, project: Any)
```

``thegent sync push`` — push local state to remote.

# @trace FR-SYNC-039

---

## sync_remote_orphans

```python
sync_remote_orphans(remote_ids: list[str], project: Any)
```

---

## sync_research

```python
sync_research(dry_run: bool, project: Any)
```

``thegent sync research`` — incorporate research fragments into WORK_STREAM.md.

# @trace WL-037

---

## sync_reset

```python
sync_reset(yes: bool, project: Any)
```

``thegent sync reset`` — reset local sync state.

# @trace FR-SYNC-040

---

## sync_rollback

```python
sync_rollback(list_snapshots: bool, snapshot_id: Any, latest: bool, create_snapshot: bool, cycle_id: str, work_stream: Any)
```

``thegent sync rollback`` — manage work stream snapshots.

Use --list to show available snapshots, --create to create one, or
--snapshot/--latest to restore.

# @trace WL-185

---

## sync_rules

```python
sync_rules(dry_run: bool, platform: Any, project: Any)
```

``thegent sync rules`` — delegate to RulesSyncManager.

# @trace WL-037

---

## sync_status

```python
sync_status(project: Any, output_format: str)
```

``thegent sync status`` — report drift and sync state.

# @trace FR-SYNC-039

---

## sync_unfreeze

```python
sync_unfreeze(actor: str, state_file: Path)
```

---

## sync_update

```python
sync_update(components: Any, dry_run: bool, force: bool)
```

---

## sync_work

```python
sync_work(force: bool)
```

---

## sync_work_stream_full

```python
sync_work_stream_full(dry_run: bool, project: Any)
```

``thegent sync work-stream`` — full work stream integration.

# @trace WL-037

---

