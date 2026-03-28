# link_checker API Reference

> **Source**: `src/thegent/docgen/link_checker.py`

Automated link checking for documentation.

---

## DocLinkChecker

Check links in documentation files.

### Methods

#### DocLinkChecker.__init__

```python
__init__(self: Any, base_dir: Any, ignore_patterns: Any, timeout: float)
```

Initialize link checker.

**Parameters**:

- `base_dir`: Base directory for documentation
- `ignore_patterns`: List of regex patterns to ignore
- `timeout`: HTTP request timeout

---

#### DocLinkChecker.check_internal_link

```python
check_internal_link(self: Any, url: str, base_path: Path)
```

Check if an internal link is valid.

**Parameters**:

- `url`: Internal URL
- `base_path`: Path of the file containing the link

**Returns**: Check result

---

#### DocLinkChecker.find_links

```python
find_links(self: Any, file_path: Path)
```

Find all links in a markdown file.

**Parameters**:

- `file_path`: Path to markdown file

**Returns**: List of link dictionaries

---

---

## check_internal_link

```python
check_internal_link(self: Any, url: str, base_path: Path)
```

Check if an internal link is valid.

**Parameters**:

- `url`: Internal URL
- `base_path`: Path of the file containing the link

**Returns**: Check result

---

## find_links

```python
find_links(self: Any, file_path: Path)
```

Find all links in a markdown file.

**Parameters**:

- `file_path`: Path to markdown file

**Returns**: List of link dictionaries

---

