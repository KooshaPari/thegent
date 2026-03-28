# json_utils API Reference

> **Source**: `src/thegent/utils/json_utils.py`

Common JSON utilities for thegent.

Provides JSON parsing, loading, and saving with consistent error handling.

---

## load_json

```python
load_json(path: Path)
```

Load JSON from a file.

---

## load_json_fast

```python
load_json_fast(path: Path)
```

Load JSON from a file using orjson (faster).

---

## parse_json

```python
parse_json(text: str)
```

Parse JSON text, returning None on error.

---

## parse_json_fast

```python
parse_json_fast(text: str)
```

Parse JSON text using orjson, returning None on error.

---

## parse_json_lines

```python
parse_json_lines(text: str)
```

Parse multiple JSON objects from text (JSONL format).

---

## safe_get

```python
safe_get(data: dict[(str, Any)])
```

Safely get nested dictionary values.

**Parameters**:

- `data`: Dictionary to search
- `*keys`: Sequence of keys to traverse
- `default`: Default value if key not found

**Examples**:

```python
safe_get(config, "database", "host", default="localhost")
```

---

## save_json

```python
save_json(path: Path, data: dict[(str, Any)], indent: int)
```

Save JSON to a file.

---

## save_json_fast

```python
save_json_fast(path: Path, data: dict[(str, Any)])
```

Save JSON to a file using orjson (faster).

---

