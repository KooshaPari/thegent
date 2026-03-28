# workstream_db_items API Reference

> **Source**: `src/thegent/planning/workstream_db_items.py`

Item transformation helpers for workstream DB.

---

## build_next_item

```python
build_next_item(item_id: str, title: str, source_system: str, priority: str, meta: dict[(str, Any)])
```

Build do_next payload shape for queue/workstream consumers.

---

## build_prompt_suggestion

```python
build_prompt_suggestion(source_system: str, item_id: str, title: str, meta: dict[(str, Any)])
```

Build prompt suggestion string from canonical source metadata.

---

## parse_meta_json

```python
parse_meta_json(meta_json: Any)
```

Parse metadata JSON payload into a dict.

---

