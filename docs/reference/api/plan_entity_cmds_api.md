# plan_entity_cmds API Reference

> **Source**: `src/thegent/cli/commands/plan_entity_cmds.py`

Canonical workstream entity commands.

---

## entity_delete

```python
entity_delete(entity_type: str, entity_id: str, format: str) -> None
```

---

## entity_export

```python
entity_export(entity_type: str, output_path: Any, limit: int, offset: int) -> None
```

---

## entity_import

```python
entity_import(entity_type: str, input_path: Path, format: str) -> None
```

---

## entity_list

```python
entity_list(entity_type: str, limit: int, offset: int, format: str) -> None
```

---

## entity_read

```python
entity_read(entity_type: str, entity_id: str, format: str) -> None
```

---

## entity_search

```python
entity_search(entity_type: str, query: str, limit: int, format: str) -> None
```

---

## entity_sync

```python
entity_sync(source: str, cd: Any, format: str) -> None
```

---

## entity_upsert

```python
entity_upsert(entity_type: str, entity_id: Any, property_value: Any, properties_file: Any, format: str) -> None
```

---

