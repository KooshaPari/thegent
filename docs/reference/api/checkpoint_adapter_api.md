# checkpoint_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/checkpoint_adapter.py`

Checkpoint and failure queue adapter for workstream autosync.

Handles checkpoint persistence and failure queue management.

---

## CheckpointAdapter

Adapter for checkpoint and failure queue operations.

### Methods

#### CheckpointAdapter.__init__

```python
__init__(self: Any, config: Any, failure_queue: SyncFailureQueue)
```

---

#### CheckpointAdapter.clear_checkpoint

```python
clear_checkpoint(self: Any)
```

Clear checkpoint file.

---

#### CheckpointAdapter.get_checkpoint_path

```python
get_checkpoint_path(self: Any)
```

---

#### CheckpointAdapter.get_failure_queue_path

```python
get_failure_queue_path(self: Any)
```

---

#### CheckpointAdapter.load_checkpoint

```python
load_checkpoint(self: Any)
```

Load checkpoint from disk.

---

#### CheckpointAdapter.load_failure_queue

```python
load_failure_queue(self: Any)
```

Load failure queue from disk.

---

#### CheckpointAdapter.save_checkpoint

```python
save_checkpoint(self: Any, checkpoint: SyncCheckpoint)
```

Save checkpoint to disk.

---

#### CheckpointAdapter.save_failure_queue

```python
save_failure_queue(self: Any)
```

Save failure queue to disk.

---

---

## clear_checkpoint

```python
clear_checkpoint(self: Any)
```

Clear checkpoint file.

---

## get_checkpoint_path

```python
get_checkpoint_path(self: Any) -> Path
```

---

## get_failure_queue_path

```python
get_failure_queue_path(self: Any) -> Path
```

---

## load_checkpoint

```python
load_checkpoint(self: Any)
```

Load checkpoint from disk.

---

## load_failure_queue

```python
load_failure_queue(self: Any)
```

Load failure queue from disk.

---

## save_checkpoint

```python
save_checkpoint(self: Any, checkpoint: SyncCheckpoint)
```

Save checkpoint to disk.

---

## save_failure_queue

```python
save_failure_queue(self: Any)
```

Save failure queue to disk.

---

