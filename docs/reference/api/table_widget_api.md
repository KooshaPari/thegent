# table_widget API Reference

> **Source**: `src/thegent/tui/widgets/table_widget.py`

Sortable/paginated table widget for compositor sidebars (WL-017).

---

## TableWidget

Data table with in-memory sort and simple pagination.

**Inherits from**: `Widget`

### Methods

#### TableWidget.__init__

```python
__init__(self: Any, page_size: int)
```

---

#### TableWidget.compose

```python
compose(self: Any)
```

---

#### TableWidget.next_page

```python
next_page(self: Any)
```

---

#### TableWidget.prev_page

```python
prev_page(self: Any)
```

---

#### TableWidget.set_columns

```python
set_columns(self: Any, columns: list[str])
```

---

#### TableWidget.set_rows

```python
set_rows(self: Any, rows: list[tuple[(str, Ellipsis)]])
```

---

#### TableWidget.sort_by

```python
sort_by(self: Any, column_index: int, reverse: bool)
```

---

---

## compose

```python
compose(self: Any)
```

---

## next_page

```python
next_page(self: Any) -> None
```

---

## prev_page

```python
prev_page(self: Any) -> None
```

---

## set_columns

```python
set_columns(self: Any, columns: list[str]) -> None
```

---

## set_rows

```python
set_rows(self: Any, rows: list[tuple[(str, Ellipsis)]]) -> None
```

---

## sort_by

```python
sort_by(self: Any, column_index: int, reverse: bool) -> None
```

---

