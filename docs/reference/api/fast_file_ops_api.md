# fast_file_ops API Reference

> **Source**: `src/thegent/infra/fast_file_ops.py`

Fast file operations with platform-specific optimizations.

This module provides optimized file operations that use platform-specific
optimizations for better performance:
- Linux: os.sendfile() for large file copies (zero-copy)
- All platforms: Optimized shutil operations
- Batch operations where possible

Performance improvements:
- sendfile() on Linux: Zero-copy for large files (10-100MB+)
- Optimized directory operations
- Batch file operations

---

## FastFileOps

High-performance file operations with platform-specific optimizations.

### Methods

#### FastFileOps.copy

Copy file with optimized method selection.

Args:
    src: Source file path
    dst: Destination file path
    preserve_metadata: Whether to preserve file metadata

Performance:
    - Linux: Uses sendfile() for large files (>10MB) - zero-copy
    - Other platforms: Uses optimized shutil.copy2()

```python
copy(src, dst, preserve_metadata)
```

#### FastFileOps.copy_tree

Copy directory tree with optimizations.

Args:
    src: Source directory path
    dst: Destination directory path
    ignore: Optional list of patterns to ignore

```python
copy_tree(src, dst, ignore)
```

#### FastFileOps.ensure_dir

Ensure directory exists (create if needed).

Args:
    path: Directory path
    mode: Directory permissions

Returns:
    Path object

```python
ensure_dir(path, mode)
```

#### FastFileOps.get_size

Get file or directory size (optimized).

Args:
    path: Path to file or directory

Returns:
    Size in bytes

```python
get_size(path)
```

#### FastFileOps.move

Move file or directory (optimized).

Args:
    src: Source path
    dst: Destination path

```python
move(src, dst)
```

#### FastFileOps.remove

Remove file or directory (optimized).

Args:
    path: Path to remove
    recursive: If True, remove directory recursively

```python
remove(path, recursive)
```

---

## copy

Copy file with optimized method selection.

Args:
    src: Source file path
    dst: Destination file path
    preserve_metadata: Whether to preserve file metadata

Performance:
    - Linux: Uses sendfile() for large files (>10MB) - zero-copy
    - Other platforms: Uses optimized shutil.copy2()

```python
copy(src, dst, preserve_metadata)
```

---

## copy_file

Copy file with optimized method.

```python
copy_file(src, dst, preserve_metadata)
```

---

## copy_tree

Copy directory tree with optimizations.

Args:
    src: Source directory path
    dst: Destination directory path
    ignore: Optional list of patterns to ignore

```python
copy_tree(src, dst, ignore)
```

---

## ensure_dir

Ensure directory exists (create if needed).

Args:
    path: Directory path
    mode: Directory permissions

Returns:
    Path object

```python
ensure_dir(path, mode)
```

---

## ensure_directory

Ensure directory exists.

```python
ensure_directory(path, mode)
```

---

## get_path_size

Get file or directory size.

```python
get_path_size(path)
```

---

## get_size

Get file or directory size (optimized).

Args:
    path: Path to file or directory

Returns:
    Size in bytes

```python
get_size(path)
```

---

## ignore_func

```python
ignore_func(directory, files)
```

---

## move

Move file or directory (optimized).

Args:
    src: Source path
    dst: Destination path

```python
move(src, dst)
```

---

## move_file

Move file or directory.

```python
move_file(src, dst)
```

---

## remove

Remove file or directory (optimized).

Args:
    path: Path to remove
    recursive: If True, remove directory recursively

```python
remove(path, recursive)
```

---

## remove_path

Remove file or directory.

```python
remove_path(path, recursive)
```

---

