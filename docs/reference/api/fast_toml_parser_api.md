# fast_toml_parser API Reference

> **Source**: `src/thegent/infra/fast_toml_parser.py`

Fast TOML parser with optimized backends.

This module provides a high-performance abstraction layer for TOML parsing
that automatically selects the fastest available backend:
- rtoml (Rust-based): 10-20x faster than tomlkit
- tomli/tomli-w (Python 3.11+): 3-5x faster for reading
- tomlkit: Standard fallback (good for editing)

Performance improvements:
- rtoml uses Rust implementation (10-20x faster)
- tomli optimized pure-Python (3-5x faster)
- Automatic backend selection based on availability and use case

---

## FastTOMLParser

High-performance TOML parser with automatic backend selection.

Backend priority (fastest first):
1. rtoml (if installed) - 10-20x faster, Rust-based
2. tomli/tomli-w (if installed) - 3-5x faster, pure-Python
3. tomlkit (standard fallback) - good for editing, slower for reading

### Methods

#### FastTOMLParser.__init__

Initialize TOML parser.

Args:
    edit_mode: If True, prefer tomlkit for editing capabilities

```python
__init__(self, edit_mode)
```

#### FastTOMLParser.backend

Get current backend name.

```python
backend(self)
```

#### FastTOMLParser.dump

Dump TOML to string or file.

Args:
    data: Data to serialize
    stream: Optional file-like object or Path to write to
    **kwargs: Additional options

Returns:
    TOML string if stream is None, else None

```python
dump(self, data, stream)
```

#### FastTOMLParser.dumps

Dump TOML to string.

Args:
    data: Data to serialize
    **kwargs: Additional options

Returns:
    TOML string

```python
dumps(self, data)
```

#### FastTOMLParser.load

Load TOML from string or file path.

Args:
    stream: TOML string, Path object, or file-like object

Returns:
    Parsed TOML as dictionary

```python
load(self, stream)
```

#### FastTOMLParser.loads

Load TOML from string.

Args:
    s: TOML string

Returns:
    Parsed TOML as dictionary

```python
loads(self, s)
```

---

## backend

Get current backend name.

```python
backend(self)
```

---

## dump

Dump TOML to string or file.

Args:
    data: Data to serialize
    stream: Optional file-like object or Path to write to
    **kwargs: Additional options

Returns:
    TOML string if stream is None, else None

```python
dump(self, data, stream)
```

---

## dumps

Dump TOML to string.

Args:
    data: Data to serialize
    **kwargs: Additional options

Returns:
    TOML string

```python
dumps(self, data)
```

---

## get_toml_parser

Get global fast TOML parser instance.

Args:
    edit_mode: If True, prefer tomlkit for editing capabilities

Returns:
    FastTOMLParser instance

```python
get_toml_parser(edit_mode)
```

---

## load

Load TOML from string or file path.

Args:
    stream: TOML string, Path object, or file-like object

Returns:
    Parsed TOML as dictionary

```python
load(self, stream)
```

---

## loads

Load TOML from string.

Args:
    s: TOML string

Returns:
    Parsed TOML as dictionary

```python
loads(self, s)
```

---

## toml_dump

Dump TOML using fastest available backend.

```python
toml_dump(data, stream)
```

---

## toml_dumps

Dump TOML to string using fastest available backend.

```python
toml_dumps(data)
```

---

## toml_load

Load TOML using fastest available backend.

```python
toml_load(stream)
```

---

## toml_loads

Load TOML string using fastest available backend.

```python
toml_loads(s)
```

---

