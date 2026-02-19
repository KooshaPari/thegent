# schema_formal API Reference

> **Source**: `src/thegent/verification/schema_formal.py`

WP-27003: Formal Verification of Schema Evolution.
Ensures schema changes maintain backward compatibility and follow evolution policies.

---

## SchemaEvolutionVerifier

Verifies evolution between two schema versions to prevent breaking changes.

### Methods

#### SchemaEvolutionVerifier.check_liveness_impact

WP-25001: Check if evolution impacts agent liveness.
Removing critical tags (STATUS, SUMMARY) impacts liveness.

```python
check_liveness_impact(self, evolution_report)
```

#### SchemaEvolutionVerifier.verify_compatibility

Check for breaking changes between old and new schema.

A breaking change is:
- Removal of a field
- Change of field type (if strictly typed)
- Making an existing optional field mandatory

```python
verify_compatibility(self, old_schema, new_schema)
```

#### SchemaEvolutionVerifier.verify_tag_evolution

Verify evolution of a list of allowed XML tags.
Removing a tag is breaking; adding is an evolution.

```python
verify_tag_evolution(self, old_tags, new_tags)
```

---

## check_liveness_impact

WP-25001: Check if evolution impacts agent liveness.
Removing critical tags (STATUS, SUMMARY) impacts liveness.

```python
check_liveness_impact(self, evolution_report)
```

---

## verify_compatibility

Check for breaking changes between old and new schema.

A breaking change is:
- Removal of a field
- Change of field type (if strictly typed)
- Making an existing optional field mandatory

```python
verify_compatibility(self, old_schema, new_schema)
```

---

## verify_tag_evolution

Verify evolution of a list of allowed XML tags.
Removing a tag is breaking; adding is an evolution.

```python
verify_tag_evolution(self, old_tags, new_tags)
```

---

