# validator API Reference

> **Source**: `src/thegent/task/validator.py`

Task validation implementation.

---

## TaskValidator

Task validator using JSON Schema.

### Methods

#### TaskValidator.__init__

Initialize validator with schema.

Args:
    schema_path: Path to JSON Schema file (defaults to schemas/task-input.schema.json)

```python
__init__(self, schema_path)
```

#### TaskValidator.validate

Validate a task dictionary.

Args:
    task: Task dictionary to validate

Returns:
    ValidationResult with validation status and errors

```python
validate(self, task)
```

#### TaskValidator.validate_file

Validate a task file.

Args:
    file_path: Path to task file

Returns:
    ValidationResult with validation status and errors

```python
validate_file(self, file_path)
```

---

## ValidationError

Single validation error.

---

## ValidationResult

Task validation result.

### Methods

#### ValidationResult.format_errors

Format errors for display.

```python
format_errors(self)
```

---

## format_errors

Format errors for display.

```python
format_errors(self)
```

---

## validate

Validate a task dictionary.

Args:
    task: Task dictionary to validate

Returns:
    ValidationResult with validation status and errors

```python
validate(self, task)
```

---

## validate_file

Validate a task file.

Args:
    file_path: Path to task file

Returns:
    ValidationResult with validation status and errors

```python
validate_file(self, file_path)
```

---

## validate_task

Validate a task dictionary.

Convenience function that creates a validator and validates.

Args:
    task: Task dictionary to validate
    schema_path: Optional path to schema file

Returns:
    ValidationResult

```python
validate_task(task, schema_path)
```

---

## validate_task_file

Validate a task file.

Convenience function that creates a validator and validates.

Args:
    file_path: Path to task file
    schema_path: Optional path to schema file

Returns:
    ValidationResult

```python
validate_task_file(file_path, schema_path)
```

---

