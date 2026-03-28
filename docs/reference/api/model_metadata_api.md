# model_metadata API Reference

> **Source**: `src/thegent/utils/routing_impl/model_metadata.py`

Model metadata registry for all models.

---

## get_all_models_with_metadata

Get list of all models with metadata.

**Returns**: List of model IDs

---

## get_model_metadata

```python
get_model_metadata(model_id: str)
```

Get comprehensive metadata for a model.

**Parameters**:

- `model_id`: Model identifier (may be alias or canonical name)

**Returns**: Model metadata dict or None if not found

---

## has_model_metadata

```python
has_model_metadata(model_id: str)
```

Check if model has metadata available.

**Parameters**:

- `model_id`: Model identifier

**Returns**: True if metadata exists, False otherwise

---

## mark_metadata_stale

```python
mark_metadata_stale(metadata: dict[(str, Any)])
```

Mark metadata envelope as stale.

---

## stamp_metadata_freshness

```python
stamp_metadata_freshness(metadata: dict[(str, Any)])
```

Return metadata with freshness envelope fields.

---

## validate_metadata_freshness

```python
validate_metadata_freshness(metadata: dict[(str, Any)])
```

Return metadata with explicit freshness marker based on expires_at.

---

