# evidence_ledger API Reference

> **Source**: `src/thegent/governance/evidence_ledger.py`

Hash-chained JSONL evidence ledger for AgilePlus cycles.

Records evidence events with cryptographic hash chaining for tamper detection,
following the RunRegistry pattern from execution.py.

---

## EvidenceEvent

A single evidence event in the hash-chained ledger.

**Inherits from**: `BaseModel`

---

## EvidenceLedger

Hash-chained JSONL evidence ledger for AgilePlus cycles.

Follows the RunRegistry pattern: each record contains a prev_hash linking
to the previous record's hash, forming a tamper-evident chain.

### Methods

#### EvidenceLedger.__init__

```python
__init__(self, session_dir)
```

#### EvidenceLedger.ledger_path

```python
ledger_path(self)
```

#### EvidenceLedger.link_to_graph

Link an evidence event to an artifact in the EvidenceGraph.

```python
link_to_graph(self, graph, event_hash, artifact_id)
```

#### EvidenceLedger.query

Query evidence events, optionally filtering by cycle_id and/or event_type.

```python
query(self, cycle_id, event_type)
```

#### EvidenceLedger.record

Record an evidence event with hash chaining.

Returns the hash of the newly recorded event.

```python
record(self, event_type, cycle_id, payload)
```

#### EvidenceLedger.verify_chain

Verify the integrity of the hash chain.

Returns True if every record's hash is correct and prev_hash links
form an unbroken chain. Returns False on any inconsistency.

```python
verify_chain(self)
```

---

## ledger_path

```python
ledger_path(self)
```

---

## link_to_graph

Link an evidence event to an artifact in the EvidenceGraph.

```python
link_to_graph(self, graph, event_hash, artifact_id)
```

---

## query

Query evidence events, optionally filtering by cycle_id and/or event_type.

```python
query(self, cycle_id, event_type)
```

---

## record

Record an evidence event with hash chaining.

Returns the hash of the newly recorded event.

```python
record(self, event_type, cycle_id, payload)
```

---

## verify_chain

Verify the integrity of the hash chain.

Returns True if every record's hash is correct and prev_hash links
form an unbroken chain. Returns False on any inconsistency.

```python
verify_chain(self)
```

---

