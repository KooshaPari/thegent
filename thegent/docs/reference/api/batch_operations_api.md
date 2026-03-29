# batch_operations API Reference

> **Source**: `src/thegent/utils/batch_operations.py`

Batch file operations to reduce tool calls.

---

## batch_file_operations

```python
batch_file_operations(files: list[Path], operation: Callable[(Any, Any)], batch_size: int)
```

Perform batch file operations.

**Parameters**:

- `files`: List of file paths
- `operation`: Operation function to apply to each file
- `batch_size`: Number of files to process per batch

**Returns**: List of operation results

---

## batch_read_files

```python
batch_read_files(files: list[Path], batch_size: int)
```

Batch read multiple files.

**Parameters**:

- `files`: List of file paths
- `batch_size`: Number of files to read per batch

**Returns**: Dictionary mapping paths to file contents

---

## batch_write_files

```python
batch_write_files(file_contents: dict[(Path, str)], batch_size: int)
```

Batch write multiple files.

**Parameters**:

- `file_contents`: Dictionary mapping paths to file contents
- `batch_size`: Number of files to write per batch

---

## read_file

```python
read_file(file_path: Path) -> tuple[(Path, str)]
```

---

## write_file

```python
write_file(item: tuple[(Path, str)]) -> None
```

---
