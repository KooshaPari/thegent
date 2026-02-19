# parser API Reference

> **Source**: `src/thegent/task/parser.py`

Task parsing implementation.

---

## TaskParseError

Error parsing task file.

**Inherits from**: `Exception`

---

## detect_task_format

Auto-detect task format.

Args:
    content: File content

Returns:
    Format type: 'yaml_frontmatter', 'legacy', 'json', or 'unknown'

```python
detect_task_format(content)
```

---

## extract_markdown_sections

Extract markdown sections by header.

Args:
    body: Markdown body content

Returns:
    Dictionary mapping section names to content

```python
extract_markdown_sections(body)
```

---

## parse_legacy_task

Parse legacy task format (backward compatibility).

Args:
    content: Legacy task content

Returns:
    Parsed task dictionary

```python
parse_legacy_task(content)
```

---

## parse_task_file

Parse a task file (auto-detects format).

Args:
    file_path: Path to task file

Returns:
    Parsed task dictionary

Raises:
    TaskParseError: If file cannot be parsed

```python
parse_task_file(file_path)
```

---

## parse_yaml_frontmatter

Parse YAML frontmatter from markdown content.

Args:
    content: Markdown content with YAML frontmatter

Returns:
    Tuple of (frontmatter_dict, markdown_body)

Raises:
    ValueError: If frontmatter is invalid or missing

```python
parse_yaml_frontmatter(content)
```

---

