# workstream_entities API Reference

> **Source**: `src/thegent/planning/workstream_entities.py`

Canonical workstream entity operations for CLI, MCP, and API surfaces.

---

## EntityTableSpec

Canonical table metadata for safe generic CRUD.

---

## delete_entity

```python
delete_entity(entity_type: str, entity_id: str) -> dict[(str, Any)]
```

---

## entity_operation

```python
entity_operation(operation: str, entity_type: str)
```

Dispatch workstream entity operations through one canonical API.

---

## export_entities

```python
export_entities(entity_type: str) -> dict[(str, Any)]
```

---

## import_entities

```python
import_entities(entity_type: str, records: list[dict[(str, Any)]]) -> dict[(str, Any)]
```

---

## list_entities

```python
list_entities(entity_type: str)
```

List canonical records for a supported workstream entity table.

---

## read_entity

```python
read_entity(entity_type: str, entity_id: str) -> dict[(str, Any)]
```

---

## search_entities

```python
search_entities(entity_type: str, query: str) -> dict[(str, Any)]
```

---

## sync_entities_from_sources

Sync canonical tables from markdown, AgilePlus, and queue sources.

---

## upsert_entity

```python
upsert_entity(entity_type: str) -> dict[(str, Any)]
```

---

