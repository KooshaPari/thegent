# input_sanitizer API Reference

> **Source**: `src/thegent/security/input_sanitizer.py`

Input sanitization and validation for security.

---

## InputSanitizer

Sanitizes and validates user inputs.

### Methods

#### InputSanitizer.detect_command_injection

```python
detect_command_injection(value: str)
```

Detect command injection attempts.

---

#### InputSanitizer.detect_sql_injection

```python
detect_sql_injection(value: str)
```

Detect SQL injection attempts.

---

#### InputSanitizer.detect_xss

```python
detect_xss(value: str)
```

Detect XSS attempts.

---

#### InputSanitizer.sanitize_input

```python
sanitize_input(value: Any, input_type: str)
```

Sanitize input based on type.

**Returns**: (sanitized_value, error_message)

---

#### InputSanitizer.sanitize_string

```python
sanitize_string(value: str, max_length: Any)
```

Sanitize string input.

---

#### InputSanitizer.validate_filename

```python
validate_filename(filename: str)
```

Validate filename safety.

**Returns**: (is_valid, error_message)

---

---

## detect_command_injection

```python
detect_command_injection(value: str)
```

Detect command injection attempts.

---

## detect_sql_injection

```python
detect_sql_injection(value: str)
```

Detect SQL injection attempts.

---

## detect_xss

```python
detect_xss(value: str)
```

Detect XSS attempts.

---

## sanitize_input

```python
sanitize_input(value: Any, input_type: str)
```

Sanitize input based on type.

**Returns**: (sanitized_value, error_message)

---

## sanitize_string

```python
sanitize_string(value: str, max_length: Any)
```

Sanitize string input.

---

## validate_filename

```python
validate_filename(filename: str)
```

Validate filename safety.

**Returns**: (is_valid, error_message)

---
