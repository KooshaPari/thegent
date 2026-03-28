# task_classifier API Reference

> **Source**: `src/thegent/governance/task_classifier.py`

Governance task classifier for delegation placement and gate selection (W78-B01).

This module implements a schema-first loader and a deterministic rule engine for
computing governance placement recommendations from
`docs/governance/TASK_CLASSIFIER_SCHEMA.yaml`.

---

## SchemaSpec

---

## TaskClassification

### Methods

#### TaskClassification.as_payload

```python
as_payload(self: Any)
```

---

---

## TaskClassifierError

Raised for schema, payload, or classification failures.

**Inherits from**: `ValueError`

---

## TaskMetadata

---

## as_payload

```python
as_payload(self: Any) -> dict[(str, Any)]
```

---

## classify

```python
classify(payload: dict[(str, Any)]) -> tuple[(TaskMetadata, TaskClassification)]
```

---

## load_schema

---

## validate_classification_payload

```python
validate_classification_payload(payload: dict[(str, Any)], schema: SchemaSpec) -> None
```

---

