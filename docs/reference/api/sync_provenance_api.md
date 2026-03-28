# sync_provenance API Reference

> **Source**: `src/thegent/integrations/sync_provenance.py`

Provenance metadata for sync operations.

Adds per-item provenance stamps to tracked sync records with sync ID,
timestamp, source, operator, and cycle number.

FR traceability: WL-201 (Sync Provenance Stamps)

---

## SyncProvenanceStamp

Provenance metadata for a sync operation.

**Inherits from**: `SerializableMixin`

### Methods

#### SyncProvenanceStamp.canonical_payload

```python
canonical_payload(self: Any)
```

Render a deterministic payload used for hash/signature generation.

---

#### SyncProvenanceStamp.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create a stamp from a dictionary.

**Parameters**:

- `data`: Dictionary with required keys.

**Returns**: A new SyncProvenanceStamp instance.

---

---

## canonical_owner

```python
canonical_owner(record: dict[(str, Any)])
```

Resolve canonical owner across local/GitHub/Linear field variants.

---

## canonical_payload

```python
canonical_payload(self: Any)
```

Render a deterministic payload used for hash/signature generation.

---

## chain_provenance_stamps

```python
chain_provenance_stamps(stamps: list[SyncProvenanceStamp], secret: str)
```

Attach deterministic hash chain fields and signatures to stamps.

---

## enrich_sync_metadata

```python
enrich_sync_metadata(record: dict[(str, Any)])
```

Attach standardized metadata enrichment fields to a sync record.

---

## extract_provenance

```python
extract_provenance(record: dict[(str, Any)])
```

Extract the provenance stamp from a record.

**Parameters**:

- `record`: The record to extract from.

**Returns**: The SyncProvenanceStamp if present, None otherwise.

**Raises**:

- `ValueError`: If the provenance data is malformed.

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Create a stamp from a dictionary.

**Parameters**:

- `data`: Dictionary with required keys.

**Returns**: A new SyncProvenanceStamp instance.

**Raises**:

- `KeyError`: If required fields are missing.

---

## get_current_timestamp

Get the current timestamp in ISO 8601 format.

**Returns**: ISO 8601 formatted timestamp.

---

## has_provenance

```python
has_provenance(record: dict[(str, Any)])
```

Check if a record has provenance metadata.

**Parameters**:

- `record`: The record to check.

**Returns**: True if the record has provenance metadata.

---

## new_run_correlation_id

Return a run-scoped correlation identifier.

---

## propagate_owner_metadata

```python
propagate_owner_metadata(record: dict[(str, Any)], owner: str)
```

Propagate canonical owner into connector-specific owner fields.

---

## remove_provenance

```python
remove_provenance(record: dict[(str, Any)])
```

Remove provenance metadata from a record.

Creates a shallow copy without the provenance key.

**Parameters**:

- `record`: The record to clean.

**Returns**: A new dict without provenance metadata.

---

## sign_provenance_stamp

```python
sign_provenance_stamp(stamp: SyncProvenanceStamp, secret: str)
```

Create a deterministic signature for a provenance stamp.

---

## stamp_sync_record

```python
stamp_sync_record(record: dict[(str, Any)], stamp: SyncProvenanceStamp)
```

Attach a provenance stamp to a record.

Creates a shallow copy of the record with the stamp attached.

**Parameters**:

- `record`: The record to stamp (dict).
- `stamp`: The provenance stamp to attach.

**Returns**: A new dict with the stamp attached under the provenance key.

**Raises**:

- `ValueError`: If record is not a dictionary.

---

## verify_provenance_chain

```python
verify_provenance_chain(stamps: list[SyncProvenanceStamp], secret: str)
```

Verify prev-hash continuity and signatures for a chain of stamps.

---

## verify_provenance_signature

```python
verify_provenance_signature(stamp: SyncProvenanceStamp, secret: str)
```

Verify that the signature matches the stamp payload.

---

