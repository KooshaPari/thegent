# fast_json_schema API Reference

> **Source**: `src/thegent/infra/fast_json_schema.py`

Fast JSON schema validator with optimized backends.

This module provides a high-performance abstraction layer for JSON schema validation
that automatically selects the fastest available backend:
- fastjsonschema: 2-3x faster than jsonschema
- jsonschema: Standard fallback

Performance improvements:
- fastjsonschema compiles schemas to Python code (2-3x faster)
- Automatic backend selection based on availability
- Cached compiled schemas for repeated validation

---

## FastJSONSchemaValidator

High-performance JSON schema validator with automatic backend selection.

Backend priority (fastest first):
1. fastjsonschema (if installed) - 2-3x faster, compiles schemas to Python
2. jsonschema (standard fallback) - baseline performance

### Methods

#### FastJSONSchemaValidator.__init__

Initialize validator with a schema.

Args:
    schema: JSON schema dictionary

```python
__init__(self, schema)
```

#### FastJSONSchemaValidator.backend

Get current backend name.

```python
backend(self)
```

#### FastJSONSchemaValidator.is_valid

Check if instance is valid without raising exception.

Args:
    instance: Data to validate

Returns:
    True if valid, False otherwise

```python
is_valid(self, instance)
```

#### FastJSONSchemaValidator.validate

Validate instance against schema.

Args:
    instance: Data to validate

Raises:
    ValidationError: If validation fails

```python
validate(self, instance)
```

---

## backend

Get current backend name.

```python
backend(self)
```

---

## get_schema_validator

Get or create a schema validator (with caching).

Args:
    schema: JSON schema dictionary
    cache_key: Optional cache key (uses schema hash if not provided)

Returns:
    FastJSONSchemaValidator instance

```python
get_schema_validator(schema, cache_key)
```

---

## is_valid

Check if instance is valid without raising exception.

Args:
    instance: Data to validate

Returns:
    True if valid, False otherwise

```python
is_valid(self, instance)
```

---

## is_valid_json_schema

Check if instance is valid against schema.

Args:
    instance: Data to validate
    schema: JSON schema dictionary
    cache_key: Optional cache key for schema caching

Returns:
    True if valid, False otherwise

```python
is_valid_json_schema(instance, schema, cache_key)
```

---

## validate

Validate instance against schema.

Args:
    instance: Data to validate

Raises:
    ValidationError: If validation fails

```python
validate(self, instance)
```

---

## validate_json_schema

Validate instance against schema using fastest available backend.

Args:
    instance: Data to validate
    schema: JSON schema dictionary
    cache_key: Optional cache key for schema caching

Raises:
    ValidationError: If validation fails

```python
validate_json_schema(instance, schema, cache_key)
```

---

