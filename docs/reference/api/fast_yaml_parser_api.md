# fast_yaml_parser API Reference

> **Source**: `src/thegent/infra/fast_yaml_parser.py`

Fast YAML parser with optimized backends.

This module provides a high-performance abstraction layer for YAML parsing
that automatically selects the fastest available backend:
- oyaml (orjson-based): 3-5x faster than PyYAML
- ruamel.yaml: 2-3x faster, preserves formatting
- PyYAML: Standard fallback

Performance improvements:
- oyaml uses orjson for JSON-like speed (3-5x faster)
- ruamel.yaml optimized C implementation (2-3x faster)
- Automatic backend selection based on availability

---

## FastYAMLParser

High-performance YAML parser with automatic backend selection.

Backend priority (fastest first):
1. oyaml (if installed) - 3-5x faster, orjson-based
2. ruamel.yaml (if installed) - 2-3x faster, preserves formatting
3. PyYAML (standard fallback) - baseline performance

### Methods

#### FastYAMLParser.__init__

Initialize YAML parser.

Args:
    preserve_formatting: If True, prefer ruamel.yaml for round-trip preservation

```python
__init__(self, preserve_formatting)
```

#### FastYAMLParser.backend

Get current backend name.

```python
backend(self)
```

#### FastYAMLParser.dump

Dump YAML to string or file.

Args:
    data: Data to serialize
    stream: Optional file-like object or Path to write to
    **kwargs: Additional options

Returns:
    YAML string if stream is None, else None

```python
dump(self, data, stream)
```

#### FastYAMLParser.dumps

Dump YAML to string.

Args:
    data: Data to serialize
    **kwargs: Additional options

Returns:
    YAML string

```python
dumps(self, data)
```

#### FastYAMLParser.load

Load YAML from string or file path.

Args:
    stream: YAML string, Path object, or file-like object

Returns:
    Parsed YAML as dictionary

```python
load(self, stream)
```

#### FastYAMLParser.loads

Load YAML from string.

Args:
    s: YAML string

Returns:
    Parsed YAML as dictionary

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

Dump YAML to string or file.

Args:
    data: Data to serialize
    stream: Optional file-like object or Path to write to
    **kwargs: Additional options

Returns:
    YAML string if stream is None, else None

```python
dump(self, data, stream)
```

---

## dumps

Dump YAML to string.

Args:
    data: Data to serialize
    **kwargs: Additional options

Returns:
    YAML string

```python
dumps(self, data)
```

---

## get_yaml_parser

Get global fast YAML parser instance.

Args:
    preserve_formatting: If True, prefer ruamel.yaml for round-trip preservation

Returns:
    FastYAMLParser instance

```python
get_yaml_parser(preserve_formatting)
```

---

## load

Load YAML from string or file path.

Args:
    stream: YAML string, Path object, or file-like object

Returns:
    Parsed YAML as dictionary

```python
load(self, stream)
```

---

## loads

Load YAML from string.

Args:
    s: YAML string

Returns:
    Parsed YAML as dictionary

```python
loads(self, s)
```

---

## yaml_dump

Dump YAML using fastest available backend.

```python
yaml_dump(data, stream)
```

---

## yaml_dumps

Dump YAML to string using fastest available backend.

```python
yaml_dumps(data)
```

---

## yaml_load

Load YAML using fastest available backend.

```python
yaml_load(stream)
```

---

## yaml_loads

Load YAML string using fastest available backend.

```python
yaml_loads(s)
```

---

