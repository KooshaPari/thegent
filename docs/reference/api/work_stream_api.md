# work_stream API Reference

> **Source**: `src/thegent/planning/work_stream.py`

WP-13001: Work stream and WBS automation manager.

---

## WorkStreamManager

Manages the lifecycle of work packages across WORK_STREAM, WBS_AGENT_PROGRESS, and UNIFIED-WBS.

### Methods

#### WorkStreamManager.__init__

```python
__init__(self, settings, base_dir)
```

#### WorkStreamManager.claim

Claim an item across all coordination files.

```python
claim(self, item_id, agent_id)
```

#### WorkStreamManager.complete

Mark an item as complete across all files.

```python
complete(self, item_id, agent_id)
```

---

## claim

Claim an item across all coordination files.

```python
claim(self, item_id, agent_id)
```

---

## complete

Mark an item as complete across all files.

```python
complete(self, item_id, agent_id)
```

---

