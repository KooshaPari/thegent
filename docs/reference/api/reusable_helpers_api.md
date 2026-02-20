# reusable_helpers API Reference

> **Source**: `src/thegent/utils/reusable_helpers.py`

Reusable helper library for common patterns.

---

## ReusableHelpers

Collection of reusable helper functions.

### Methods

#### ReusableHelpers.ensure_directory

```python
ensure_directory(path: Path)
```

Ensure a directory exists.

**Parameters**:

- `path`: Directory path

**Returns**: Path object

---

#### ReusableHelpers.find_files

```python
find_files(directory: Path, pattern: str, recursive: bool)
```

Find files matching a pattern.

**Parameters**:

- `directory`: Directory to search
- `pattern`: File pattern
- `recursive`: Search recursively

**Returns**: List of matching file paths

---

#### ReusableHelpers.read_file_efficiency

```python
read_file_efficiency(file_path: Path, offset: int, limit: Any)
```

Read a file with offset and limit.

**Parameters**:

- `file_path`: File to read
- `offset`: Starting line (0-indexed)
- `limit`: Maximum number of lines to read

**Returns**: File content as string

---

#### ReusableHelpers.read_json_safe

```python
read_json_safe(file_path: Path)
```

Safely read a JSON file.

**Parameters**:

- `file_path`: JSON file path

**Returns**: Parsed JSON or None

---

#### ReusableHelpers.retry_on_failure

```python
retry_on_failure(func: Callable, max_retries: int, delay: float)
```

Retry a function on failure using tenacity.

**Parameters**:

- `func`: Function to retry
- `max_retries`: Maximum retry attempts
- `delay`: Delay between retries (seconds)
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns**: Function result

---

#### ReusableHelpers.safe_execute

```python
safe_execute(func: Callable)
```

Safely execute a function with error handling.

**Parameters**:

- `func`: Function to execute
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns**: Tuple of (result, error)

---

#### ReusableHelpers.write_json_safe

```python
write_json_safe(file_path: Path, data: dict[(str, Any)])
```

Safely write a JSON file.

**Parameters**:

- `file_path`: JSON file path
- `data`: Data to write

**Returns**: True if successful

---

---

## ensure_directory

```python
ensure_directory(path: Path)
```

Ensure a directory exists.

**Parameters**:

- `path`: Directory path

**Returns**: Path object

---

## find_files

```python
find_files(directory: Path, pattern: str, recursive: bool)
```

Find files matching a pattern.

**Parameters**:

- `directory`: Directory to search
- `pattern`: File pattern
- `recursive`: Search recursively

**Returns**: List of matching file paths

---

## read_file_efficiency

```python
read_file_efficiency(file_path: Path, offset: int, limit: Any)
```

Read a file with offset and limit.

**Parameters**:

- `file_path`: File to read
- `offset`: Starting line (0-indexed)
- `limit`: Maximum number of lines to read

**Returns**: File content as string

---

## read_json_safe

```python
read_json_safe(file_path: Path)
```

Safely read a JSON file.

**Parameters**:

- `file_path`: JSON file path

**Returns**: Parsed JSON or None

---

## retry_on_failure

```python
retry_on_failure(func: Callable, max_retries: int, delay: float)
```

Retry a function on failure using tenacity.

**Parameters**:

- `func`: Function to retry
- `max_retries`: Maximum retry attempts
- `delay`: Delay between retries (seconds)
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns**: Function result

---

## safe_execute

```python
safe_execute(func: Callable)
```

Safely execute a function with error handling.

**Parameters**:

- `func`: Function to execute
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns**: Tuple of (result, error)

---

## write_json_safe

```python
write_json_safe(file_path: Path, data: dict[(str, Any)])
```

Safely write a JSON file.

**Parameters**:

- `file_path`: JSON file path
- `data`: Data to write

**Returns**: True if successful

---

