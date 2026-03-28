# work_chunking API Reference

> **Source**: `src/thegent/orchestration/execution/work_chunking.py`

Work chunking and parallelization for resource-aware task distribution.

Breaks large tasks into parallelizable chunks with resource-aware sizing.

---

## ChunkConfig

Configuration for work chunking.

---

## chunk_work_items

```python
chunk_work_items(items: list[Any], chunk_size: int)
```

Split work items into chunks.

---

## compute_optimal_chunk_size

```python
compute_optimal_chunk_size(total_items: int, available_resources: dict[(str, Any)], config: Any)
```

Compute optimal chunk size and parallelism.

Returns (chunk_size, num_chunks).

---

