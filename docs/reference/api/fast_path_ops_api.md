# fast_path_ops API Reference

> **Source**: `src/thegent/infra/fast_path_ops.py`

Fast path operations with optimizations.

This module provides optimized path operations:
- Direct os.path operations for hot paths
- Optimized path joining and normalization
- Fast path existence checks

Performance improvements:
- Direct os.path: Faster than pathlib for simple operations
- Optimized for common path operations

---

## FastPathOps

High-performance path operations with optimizations.

### Methods

#### FastPathOps.abspath

Get absolute path efficiently.

Args:
    path: Path to resolve

Returns:
    Absolute path

```python
abspath(path)
```

#### FastPathOps.basename

Get basename efficiently.

Args:
    path: Path

Returns:
    Basename (filename)

```python
basename(path)
```

#### FastPathOps.dirname

Get directory name efficiently.

Args:
    path: Path

Returns:
    Directory name

```python
dirname(path)
```

#### FastPathOps.exists

Check if path exists efficiently.

Args:
    path: Path to check

Returns:
    True if path exists

Performance:
    - os.path.exists: Fast existence check
    - Avoids Path overhead for simple checks

```python
exists(path)
```

#### FastPathOps.is_dir

Check if path is a directory efficiently.

Args:
    path: Path to check

Returns:
    True if path is a directory

```python
is_dir(path)
```

#### FastPathOps.is_file

Check if path is a file efficiently.

Args:
    path: Path to check

Returns:
    True if path is a file

```python
is_file(path)
```

#### FastPathOps.join

Join path parts efficiently.

Args:
    *parts: Path components

Returns:
    Joined path string

Performance:
    - os.path.join: Faster than Path() for simple joins
    - Optimized for common cases

#### FastPathOps.normalize

Normalize path efficiently.

Args:
    path: Path to normalize

Returns:
    Normalized path

Performance:
    - os.path.normpath: Fast normalization
    - Handles .. and . correctly

```python
normalize(path)
```

#### FastPathOps.split

Split path into directory and filename efficiently.

Args:
    path: Path to split

Returns:
    Tuple of (directory, filename)

```python
split(path)
```

#### FastPathOps.splitext

Split path into base and extension efficiently.

Args:
    path: Path to split

Returns:
    Tuple of (base, extension)

```python
splitext(path)
```

---

## abspath

Get absolute path efficiently.

Args:
    path: Path to resolve

Returns:
    Absolute path

```python
abspath(path)
```

---

## basename

Get basename efficiently.

Args:
    path: Path

Returns:
    Basename (filename)

```python
basename(path)
```

---

## dirname

Get directory name efficiently.

Args:
    path: Path

Returns:
    Directory name

```python
dirname(path)
```

---

## exists

Check if path exists efficiently.

Args:
    path: Path to check

Returns:
    True if path exists

Performance:
    - os.path.exists: Fast existence check
    - Avoids Path overhead for simple checks

```python
exists(path)
```

---

## is_dir

Check if path is a directory efficiently.

Args:
    path: Path to check

Returns:
    True if path is a directory

```python
is_dir(path)
```

---

## is_file

Check if path is a file efficiently.

Args:
    path: Path to check

Returns:
    True if path is a file

```python
is_file(path)
```

---

## join

Join path parts efficiently.

Args:
    *parts: Path components

Returns:
    Joined path string

Performance:
    - os.path.join: Faster than Path() for simple joins
    - Optimized for common cases

---

## normalize

Normalize path efficiently.

Args:
    path: Path to normalize

Returns:
    Normalized path

Performance:
    - os.path.normpath: Fast normalization
    - Handles .. and . correctly

```python
normalize(path)
```

---

## path_exists

Check if path exists efficiently.

```python
path_exists(path)
```

---

## path_is_dir

Check if path is a directory efficiently.

```python
path_is_dir(path)
```

---

## path_is_file

Check if path is a file efficiently.

```python
path_is_file(path)
```

---

## path_join

Join path parts efficiently.

---

## path_normalize

Normalize path efficiently.

```python
path_normalize(path)
```

---

## split

Split path into directory and filename efficiently.

Args:
    path: Path to split

Returns:
    Tuple of (directory, filename)

```python
split(path)
```

---

## splitext

Split path into base and extension efficiently.

Args:
    path: Path to split

Returns:
    Tuple of (base, extension)

```python
splitext(path)
```

---

