# helpers API Reference

> **Source**: `src/thegent/utils/helpers.py`

Reusable helper functions for common patterns.

---

## batch_file_operations

```python
batch_file_operations(operations: list[tuple[(str, Any)]], batch_size: int)
```

Batch file operations to reduce tool calls.

**Parameters**:

- `operations`: List of (operation_type, params) tuples
- `batch_size`: Number of operations per batch

**Returns**: List of results from operations

---

## normalize_path

```python
normalize_path(path: Any)
```

Normalize a path to a Path object, handling both absolute and relative paths.

**Parameters**:

- `path`: Path string or Path object

**Returns**: Normalized Path object

---

## read_file_chunk

```python
read_file_chunk(path: Any, offset: int, limit: Any, encoding: str)
```

Read a chunk of a file with offset and limit.

**Parameters**:

- `path`: Path to file
- `offset`: Byte offset to start reading from
- `limit`: Maximum number of bytes to read (None for all)
- `encoding`: File encoding

**Returns**: File chunk contents or None if error

---

## read_file_lines

```python
read_file_lines(path: Any, start_line: int, num_lines: Any, encoding: str)
```

Read specific lines from a file efficiently without loading the whole file into memory.

**Parameters**:

- `path`: Path to file
- `start_line`: Line number to start from (0-indexed)
- `num_lines`: Number of lines to read (None for all remaining)
- `encoding`: File encoding

**Returns**: List of lines or None if error

---

## read_file_optimized

```python
read_file_optimized(path: Any, offset: int, limit: Any, max_lines: Any, max_size_mb: int, encoding: str)
```

Read a file with optimization and safety limits for large files.

If no limit or max_lines is provided and the file exceeds max_size_mb,
it will be truncated to avoid excessive memory usage.

**Parameters**:

- `path`: Path to file
- `offset`: Byte offset to start reading from
- `limit`: Maximum number of bytes to read
- `max_lines`: Maximum number of lines to read (applied after offset)
- `max_size_mb`: Maximum size in MB to read if no limit is specified
- `encoding`: File encoding

**Returns**: File contents or None if error

---

## safe_read_file

```python
safe_read_file(path: Any, encoding: str)
```

Safely read a file with error handling.

**Parameters**:

- `path`: Path to file
- `encoding`: File encoding

**Returns**: File contents or None if error

---

## safe_read_file_with_version

```python
safe_read_file_with_version(path: Any, encoding: str)
```

Safely read a file and return its content and OCC version (hash).

**Parameters**:

- `path`: Path to file
- `encoding`: File encoding

**Returns**: Tuple of (content, version). Version is "none" if file doesn't exist.

---

## safe_write_file

```python
safe_write_file(path: Any, content: str, expected_version: Any, encoding: str)
```

Safely write a file with error handling and optional OCC version check.

**Parameters**:

- `path`: Path to file
- `content`: Content to write
- `expected_version`: Optional version (hash) to check before writing
- `encoding`: File encoding

**Returns**: True if successful, False otherwise

---
