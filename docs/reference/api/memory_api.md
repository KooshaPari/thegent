# memory API Reference

> **Source**: `src/thegent/orchestration/memory.py`

## FrictionScope

**Inherits from**: `str, Enum`

---

## MemoryCategory

**Inherits from**: `str, Enum`

---

## MemoryFragment

---

## MemorySystem

MTSP-17: Dual Issue & Memory Collection System.
Append-only audit log for agent observations, synthesized into formal docs.

### Methods

#### MemorySystem.__init__

```python
__init__(self, project_root)
```

#### MemorySystem.get_recent

```python
get_recent(self, limit, category)
```

#### MemorySystem.record

```python
record(self, content, category, agent_id, scope, metadata)
```

#### MemorySystem.synthesize_to_markdown

Helper to generate a summary for an agent to incorporate.

```python
synthesize_to_markdown(self)
```

---

## get_recent

```python
get_recent(self, limit, category)
```

---

## record

```python
record(self, content, category, agent_id, scope, metadata)
```

---

## synthesize_to_markdown

Helper to generate a summary for an agent to incorporate.

```python
synthesize_to_markdown(self)
```

---

