# artifact_redaction API Reference

> **Source**: `src/thegent/integrations/artifact_redaction.py`

Artifact redaction pipeline for sensitive field masking.

# @trace WL-276

---

## ArtifactRedactionPipeline

Pipeline for redacting sensitive fields from artifacts.

### Methods

#### ArtifactRedactionPipeline.__init__

```python
__init__(self: Any)
```

Initialize the redaction pipeline.

---

#### ArtifactRedactionPipeline.add_rule

```python
add_rule(self: Any, field_path: str, replacement: str)
```

Add a redaction rule.

**Parameters**:

- `field_path`: The top-level key to redact.
- `replacement`: The replacement value (default: "[REDACTED]").

**Returns**: The created RedactionRule.

---

#### ArtifactRedactionPipeline.redact

```python
redact(self: Any, data: dict[(str, Any)])
```

Redact sensitive fields from a dictionary.

**Parameters**:

- `data`: The input data dictionary.

**Returns**: A copy of the data with matching top-level keys replaced.

---

#### ArtifactRedactionPipeline.rules

```python
rules(self: Any)
```

Return all redaction rules.

**Returns**: A list of all registered RedactionRule objects.

---

---

## RedactionRule

Represents a field redaction rule.

---

## add_rule

```python
add_rule(self: Any, field_path: str, replacement: str)
```

Add a redaction rule.

**Parameters**:

- `field_path`: The top-level key to redact.
- `replacement`: The replacement value (default: "[REDACTED]").

**Returns**: The created RedactionRule.

---

## redact

```python
redact(self: Any, data: dict[(str, Any)])
```

Redact sensitive fields from a dictionary.

**Parameters**:

- `data`: The input data dictionary.

**Returns**: A copy of the data with matching top-level keys replaced.

---

## rules

```python
rules(self: Any)
```

Return all redaction rules.

**Returns**: A list of all registered RedactionRule objects.

---

