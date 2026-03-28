# wl_ignore_list API Reference

> **Source**: `src/thegent/integrations/wl_ignore_list.py`

WL ignore list helper.

---

## WLIgnoreList

Deterministic set-like ignore list.

### Methods

#### WLIgnoreList.add

```python
add(self: Any, wl_id: str)
```

Add an ID to the ignore list.

---

#### WLIgnoreList.all_ignored

```python
all_ignored(self: Any)
```

Return all ignored IDs in sorted order.

---

#### WLIgnoreList.filter

```python
filter(self: Any, wl_ids: list[str])
```

Return input IDs excluding ignored values while preserving order.

---

#### WLIgnoreList.is_ignored

```python
is_ignored(self: Any, wl_id: str)
```

Return whether an ID is ignored.

---

#### WLIgnoreList.remove

```python
remove(self: Any, wl_id: str)
```

Remove an ID from the ignore list.

---

---

## add

```python
add(self: Any, wl_id: str)
```

Add an ID to the ignore list.

---

## all_ignored

```python
all_ignored(self: Any)
```

Return all ignored IDs in sorted order.

---

## filter

```python
filter(self: Any, wl_ids: list[str])
```

Return input IDs excluding ignored values while preserving order.

---

## is_ignored

```python
is_ignored(self: Any, wl_id: str)
```

Return whether an ID is ignored.

---

## remove

```python
remove(self: Any, wl_id: str)
```

Remove an ID from the ignore list.

---

