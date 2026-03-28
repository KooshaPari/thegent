# sync_adapter API Reference

> **Source**: `src/thegent/integrations/adapters/sync_adapter.py`

Sync adapter for workstream autosync.

Handles GitHub and Linear sync operations.

---

## SyncAdapter

Adapter for sync operations.

### Methods

#### SyncAdapter.__init__

```python
__init__(self: Any, config: Any)
```

---

#### SyncAdapter.build_mutation_id

```python
build_mutation_id(self: Any, platform: str, item: WorkstreamItem)
```

Build a deterministic mutation identifier for one item write.

---

#### SyncAdapter.build_operation_id

```python
build_operation_id(self: Any, platform: str, direction: str, items: list[WorkstreamItem])
```

Build replay-safe deterministic operation IDs for sync batches.

---

#### SyncAdapter.compute_cycle_fingerprint

```python
compute_cycle_fingerprint(self: Any, items: list[WorkstreamItem])
```

Compute a fingerprint for the current cycle.

---

#### SyncAdapter.normalize_for_checksum

```python
normalize_for_checksum(self: Any, payload: list[dict[(str, Any)]])
```

Return a deterministic remote payload representation for checksum verification.

---

---

## SyncAdapterWrapper

Sync adapter wrapper for registry

### Methods

#### SyncAdapterWrapper.__init__

```python
__init__(self: Any)
```

---

#### SyncAdapterWrapper.call

```python
call(self: Any)
```

---

---

## build_mutation_id

```python
build_mutation_id(self: Any, platform: str, item: WorkstreamItem)
```

Build a deterministic mutation identifier for one item write.

---

## build_operation_id

```python
build_operation_id(self: Any, platform: str, direction: str, items: list[WorkstreamItem])
```

Build replay-safe deterministic operation IDs for sync batches.

---

## call

```python
call(self: Any) -> dict
```

---

## compute_cycle_fingerprint

```python
compute_cycle_fingerprint(self: Any, items: list[WorkstreamItem])
```

Compute a fingerprint for the current cycle.

---

## normalize_for_checksum

```python
normalize_for_checksum(self: Any, payload: list[dict[(str, Any)]])
```

Return a deterministic remote payload representation for checksum verification.

---

