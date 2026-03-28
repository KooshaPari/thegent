# json_compat API Reference

> **Source**: `src/thegent/utils/json_compat.py`

JSON compatibility layer.

Provides orjson with json-compatible API.
Use this instead of json for 3-5x performance improvement.

---

## dump

```python
dump(obj: Any, fp: Any)
```

Serialize obj to file.

**Parameters**:

- `obj`: Object to serialize
- `fp`: File-like object with write()
- `**kwargs`: Additional options

---

## dumps

```python
dumps(obj: Any) -> str
```

Serialize obj to JSON string.

**Parameters**:

- `obj`: Object to serialize
- `**kwargs`: Additional options (indent, sort_keys supported)

**Returns** (`str`): JSON string

---

## load

```python
load(fp: Any)
```

Deserialize file to object.

**Parameters**:

- `fp`: File-like object with read()

**Returns**: Deserialized object

---

## loads

```python
loads(s: Any)
```

Deserialize JSON string to object.

**Parameters**:

- `s`: JSON string or bytes

**Returns**: Deserialized object

---

