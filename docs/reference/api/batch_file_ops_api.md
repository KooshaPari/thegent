# batch_file_ops API Reference

> **Source**: `src/thegent/utils/batch_file_ops.py`

Batch file operations for thegent.

This module provides grouping for file reads and writes using native Rust (thegent-fs).
It includes transaction-like semantics for atomic batches and progress callbacks.

---

## BatchFileOperations

Class for grouped file reads and writes with atomic semantics.

### Methods

#### BatchFileOperations.__init__

```python
__init__(self: Any, create_backups: bool)
```

---

#### BatchFileOperations.batch_read

```python
batch_read(self: Any, paths: list[Any], on_progress: Any)
```

Read multiple files and return a mapping of path to content.

---

#### BatchFileOperations.batch_write

```python
batch_write(self: Any, operations: list[tuple[(Any, str)]], atomic: bool, on_progress: Any)
```

Write multiple files from a list of (path, content) pairs.

---

---

## BatchOperation

Represents a single file operation in a batch.

---

## BatchResult

Result of a batch operation.

---

## batch_read

```python
batch_read(self: Any, paths: list[Any], on_progress: Any)
```

Read multiple files and return a mapping of path to content.

---

## batch_write

```python
batch_write(self: Any, operations: list[tuple[(Any, str)]], atomic: bool, on_progress: Any)
```

Write multiple files from a list of (path, content) pairs.

---

