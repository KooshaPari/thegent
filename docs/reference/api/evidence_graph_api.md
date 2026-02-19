# evidence_graph API Reference

> **Source**: `src/thegent/governance/evidence_graph.py`

WP-12006: Evidence graph and export bundling.

Builds a closed-loop graph of all evidence artifacts and provides deterministic export bundling.

---

## EvidenceGraph

Graph of evidence artifacts with deterministic bundling.

### Methods

#### EvidenceGraph.__init__

```python
__init__(self, session_dir)
```

#### EvidenceGraph.add_link

Add a link between two evidence artifacts.

```python
add_link(self, parent_id, child_id)
```

#### EvidenceGraph.bundle_evidence

WP-12006: Deterministic export of the evidence graph and artifacts.

```python
bundle_evidence(self, target_path)
```

---

## add_link

Add a link between two evidence artifacts.

```python
add_link(self, parent_id, child_id)
```

---

## bundle_evidence

WP-12006: Deterministic export of the evidence graph and artifacts.

```python
bundle_evidence(self, target_path)
```

---

