# library_replacements API Reference

> **Source**: `src/thegent/research/library_replacements.py`

Library replacement implementations.

---

## check_tomlkit_available

Check if tomlkit is available.

**Returns**: True if available

---

## replace_md5_with_sha256

```python
replace_md5_with_sha256(data: bytes)
```

Replace MD5 with SHA256 for hashing.

**Parameters**:

- `data`: Data to hash

**Returns**: SHA256 hash hex string

---

## use_diskcache

```python
use_diskcache(cache_dir: Path)
```

Use diskcache for caching.

**Parameters**:

- `cache_dir`: Cache directory

**Returns**: Cache instance

---

## use_psutil_monitoring

Use psutil for resource monitoring.

**Returns**: Resource metrics dictionary

---

