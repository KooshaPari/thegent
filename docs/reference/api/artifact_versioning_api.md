# artifact_versioning API Reference

> **Source**: `src/thegent/integrations/artifact_versioning.py`

Artifact format versioning for schema management.

# @trace WL-277

---

## ArtifactFormatRegistry

Registry for managing artifact format versions.

### Methods

#### ArtifactFormatRegistry.__init__

```python
__init__(self: Any)
```

Initialize the artifact format registry.

---

#### ArtifactFormatRegistry.all_versions

```python
all_versions(self: Any)
```

Get all registered artifact format versions.

**Returns**: A list of all ArtifactVersion objects.

---

#### ArtifactFormatRegistry.get

```python
get(self: Any, format_version: str)
```

Get a specific artifact format version.

**Parameters**:

- `format_version`: The version to retrieve.

**Returns**: The ArtifactVersion object.

---

#### ArtifactFormatRegistry.latest

```python
latest(self: Any)
```

Get the latest registered artifact format version.

**Returns**: The most recently created ArtifactVersion, or None if no versions exist.

---

#### ArtifactFormatRegistry.register

```python
register(self: Any, format_version: str, schema_hash: str)
```

Register a new artifact format version.

**Parameters**:

- `format_version`: The version identifier.
- `schema_hash`: The hash of the schema definition.

**Returns**: The created ArtifactVersion.

---

---

## ArtifactVersion

Represents a versioned artifact format.

---

## all_versions

```python
all_versions(self: Any)
```

Get all registered artifact format versions.

**Returns**: A list of all ArtifactVersion objects.

---

## get

```python
get(self: Any, format_version: str)
```

Get a specific artifact format version.

**Parameters**:

- `format_version`: The version to retrieve.

**Returns**: The ArtifactVersion object.

**Raises**:

- `KeyError`: If the version is not found.

---

## latest

```python
latest(self: Any)
```

Get the latest registered artifact format version.

**Returns**: The most recently created ArtifactVersion, or None if no versions exist.

---

## register

```python
register(self: Any, format_version: str, schema_hash: str)
```

Register a new artifact format version.

**Parameters**:

- `format_version`: The version identifier.
- `schema_hash`: The hash of the schema definition.

**Returns**: The created ArtifactVersion.

---

