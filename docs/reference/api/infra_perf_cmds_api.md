# infra_perf_cmds API Reference

> **Source**: `src/thegent/cli/commands/infra_perf_cmds.py`

Thegent CLI performance & operations commands (benchmark, modes, release, forensics, monitor) - extracted from infra_cmds.py.

---

## benchmark_cmd

Report orchestration performance metrics (WP-6001).

---

## forensics_snapshot_cmd

```python
forensics_snapshot_cmd(run_id: Any, phase: Any)
```

Backward-compatible wrapper for extracted recovery command group.

---

## modes_cmd

```python
modes_cmd(format: Any, mode: Any)
```

List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop).

---

## monitor_cmd

```python
monitor_cmd(interval: float)
```

Monitor sessions and plan progress in real-time (WP-8001).

---

## operations_cmd

```python
operations_cmd(format: Any, operation: Any)
```

Backward-compatible wrapper for extracted operations command group.

---

## recover_status_cmd

Backward-compatible wrapper for extracted recovery command group.

---

## release_pack_cmd

```python
release_pack_cmd(version: str)
```

Automated release documentation packaging (WP-12009).

---

