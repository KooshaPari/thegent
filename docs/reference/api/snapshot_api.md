# snapshot API Reference

> **Source**: `src/thegent/forensics/snapshot.py`

WP-12001: Forensic snapshotting for deep debugging and audit.

---

## ForensicSnapshotter

Captures detailed system and project state snapshots.

### Methods

#### ForensicSnapshotter.__init__

```python
__init__(self, session_dir)
```

#### ForensicSnapshotter.capture_post_run

Capture state after a run, including git diff.

```python
capture_post_run(self, run_id, project_root, exit_code)
```

#### ForensicSnapshotter.capture_pre_run

Capture state before a run.

```python
capture_pre_run(self, run_id, project_root)
```

---

## capture_post_run

Capture state after a run, including git diff.

```python
capture_post_run(self, run_id, project_root, exit_code)
```

---

## capture_pre_run

Capture state before a run.

```python
capture_pre_run(self, run_id, project_root)
```

---

