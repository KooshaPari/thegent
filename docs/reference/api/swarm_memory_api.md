# swarm_memory API Reference

> **Source**: `src/thegent/orchestration/swarm_memory.py`

WP-24003: Swarm Memory Consolidation.
Consolidates distributed agent memories into a unified swarm knowledge base.
Uses cross-agent memory synthesis to eliminate redundancy and conflicts.

---

## SwarmMemoryConsolidator

Synthesizes memory artifacts from multiple agents into a unified view.

### Methods

#### SwarmMemoryConsolidator.__init__

```python
__init__(self, swarm_id, local_memory)
```

#### SwarmMemoryConsolidator.consolidate

Consolidate peer memories with local memory.

```python
consolidate(self, peer_memories)
```

---

## consolidate

Consolidate peer memories with local memory.

```python
consolidate(self, peer_memories)
```

---

