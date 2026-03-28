# chunkhound API Reference

> **Source**: `src/thegent/integrations/chunkhound.py`

ChunkHound Integration - Local-first code intelligence

Provides code chunking/indexing for local code intelligence.
Low infra overhead for code analysis.

Security:
- Verify MIT license compatibility

License: MIT (verified at https://github.com/chunkhound/chunkhound)

---

## ChunkHoundClient

### Methods

#### ChunkHoundClient.__init__

```python
__init__(self: Any, config: Any)
```

---

#### ChunkHoundClient.index

```python
index(self: Any, path: str)
```

---

#### ChunkHoundClient.is_enabled

```python
is_enabled(self: Any)
```

---

#### ChunkHoundClient.query

```python
query(self: Any, query: str)
```

---

---

## ChunkHoundConfig

**Inherits from**: `DataclassConfig`

---

## ChunkHoundStatus

**Inherits from**: `Enum`

---

## get_chunkhound

---

## index

```python
index(self: Any, path: str)
```

---

## is_enabled

```python
is_enabled(self: Any)
```

---

## query

```python
query(self: Any, query: str)
```

---

