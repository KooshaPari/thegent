# code_annotation API Reference

> **Source**: `src/thegent/docgen/code_annotation.py`

Implement code annotation component for documentation.

---

## CodeAnnotationGenerator

Generate code annotations for documentation.

### Methods

#### CodeAnnotationGenerator.__init__

```python
__init__(self: Any, annotation_format: str)
```

---

#### CodeAnnotationGenerator.generate_annotation_component

```python
generate_annotation_component(self: Any, annotations: list[dict[(str, Any)]])
```

Generate documentation component from annotations.

**Parameters**:

- `annotations`: List of parsed annotations

**Returns**: Formatted documentation component

---

#### CodeAnnotationGenerator.parse_annotations

```python
parse_annotations(self: Any, code: str)
```

Parse annotations from code (comments like # @annotation).

**Parameters**:

- `code`: Source code

**Returns**: List of annotations

---

---

## generate_annotation_component

```python
generate_annotation_component(self: Any, annotations: list[dict[(str, Any)]])
```

Generate documentation component from annotations.

**Parameters**:

- `annotations`: List of parsed annotations

**Returns**: Formatted documentation component

---

## parse_annotations

```python
parse_annotations(self: Any, code: str)
```

Parse annotations from code (comments like # @annotation).

**Parameters**:

- `code`: Source code

**Returns**: List of annotations

---
