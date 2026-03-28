# format API Reference

> **Source**: `src/thegent/utils/format.py`

Formatting utilities for thegent.

Common formatting functions for consistent output across the codebase.

---

## format_bool

```python
format_bool(value: bool, true: str, false: str)
```

Format boolean as string.

**Parameters**:

- `value`: Boolean value
- `true`: String for True
- `false`: String for False

---

## format_bytes

```python
format_bytes(size: int)
```

Format bytes to human-readable size.

**Parameters**:

- `size`: Size in bytes

---

## format_duration

```python
format_duration(seconds: float)
```

Format seconds to human-readable duration.

**Parameters**:

- `seconds`: Duration in seconds

---

## format_list

```python
format_list(items: list[Any], max_items: int, sep: str)
```

Format list with ellipsis if too long.

**Parameters**:

- `items`: List of items
- `max_items`: Maximum items to show
- `sep`: Separator between items

---

## format_number

```python
format_number(n: int)
```

Format number with thousands separator.

**Parameters**:

- `n`: Number to format

---

## format_percent

```python
format_percent(value: float, decimals: int)
```

Format float as percentage.

**Parameters**:

- `value`: Value between 0 and 1 (or 0 and 100)
- `decimals`: Number of decimal places

---

## format_table_row

```python
format_table_row(columns: list[str], widths: list[int])
```

Format a table row with fixed column widths.

**Parameters**:

- `columns`: Column values
- `widths`: Column widths

---

## format_timestamp

```python
format_timestamp(ts: Any, fmt: str)
```

Format a timestamp to string.

**Parameters**:

- `ts`: datetime object or Unix timestamp
- `fmt`: strftime format string

---

## truncate

```python
truncate(s: str, max_len: int, suffix: str)
```

Truncate string to max length.

**Parameters**:

- `s`: String to truncate
- `max_len`: Maximum length
- `suffix`: Suffix to add if truncated

---

