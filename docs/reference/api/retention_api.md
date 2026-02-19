# retention API Reference

> **Source**: `src/thegent/governance/retention.py`

WP-3006: Compliance evidence retention.

---

## EvidenceRetentionManager

Manages retention and archival of compliance evidence.

### Methods

#### EvidenceRetentionManager.__init__

```python
__init__(self, settings)
```

#### EvidenceRetentionManager.enforce_retention

Scan evidence and archive or delete based on policy.
Returns counts of processed items.

```python
enforce_retention(self)
```

#### EvidenceRetentionManager.list_archived

Return list of archived evidence files.

```python
list_archived(self)
```

---

## enforce_retention

Scan evidence and archive or delete based on policy.
Returns counts of processed items.

```python
enforce_retention(self)
```

---

## list_archived

Return list of archived evidence files.

```python
list_archived(self)
```

---

