# graph API Reference

> **Source**: `src/thegent/orchestration/graph.py`

WP-5001-SM-Graph: Supermemory Knowledge Graph integration.

---

## KnowledgeGraph

Interface to Supermemory.ai knowledge graph.

### Methods

#### KnowledgeGraph.__init__

```python
__init__(self, api_token)
```

#### KnowledgeGraph.add_relation

Add a new relation to the knowledge graph.

```python
add_relation(self, source, relation, target)
```

#### KnowledgeGraph.query

Query the knowledge graph for relevant entities and relations.

```python
query(self, query_text)
```

---

## add_relation

Add a new relation to the knowledge graph.

```python
add_relation(self, source, relation, target)
```

---

## query

Query the knowledge graph for relevant entities and relations.

```python
query(self, query_text)
```

---

