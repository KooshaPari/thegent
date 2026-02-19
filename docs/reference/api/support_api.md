# support API Reference

> **Source**: `src/thegent/governance/support.py`

WP-15005: End-user support mode with automatic PII and secret redaction.

---

## SupportModeSession

Least-privilege session for platform support engineers.

### Methods

#### SupportModeSession.__init__

```python
__init__(self, engineer_id)
```

#### SupportModeSession.get_view

Return a redacted view of the system output.

```python
get_view(self, raw_output)
```

---

## SupportRedactor

Automatic redaction of PII and secrets for support mode (WP-15005).

### Methods

#### SupportRedactor.__init__

```python
__init__(self)
```

#### SupportRedactor.redact_payload

Recursively redact strings within a nested dictionary payload.

```python
redact_payload(self, payload)
```

#### SupportRedactor.redact_text

Apply all redaction patterns to the provided text.

```python
redact_text(self, text)
```

---

## get_view

Return a redacted view of the system output.

```python
get_view(self, raw_output)
```

---

## redact_payload

Recursively redact strings within a nested dictionary payload.

```python
redact_payload(self, payload)
```

---

## redact_text

Apply all redaction patterns to the provided text.

```python
redact_text(self, text)
```

---

