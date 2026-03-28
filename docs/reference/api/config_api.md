# config API Reference

> **Source**: `src/thegent/shell/config.py`

Shell Configuration

Configurable settings for shell execution.

---

## ShellConfig

Configuration for shell execution.

### Methods

#### ShellConfig.get_retry_delay

```python
get_retry_delay(self: Any, attempt: int)
```

Calculate exponential backoff delay.

---

#### ShellConfig.get_timeout

```python
get_timeout(self: Any, explicit_timeout: Any)
```

Get timeout value, respecting max.

---

---

## get_retry_delay

```python
get_retry_delay(self: Any, attempt: int)
```

Calculate exponential backoff delay.

---

## get_timeout

```python
get_timeout(self: Any, explicit_timeout: Any)
```

Get timeout value, respecting max.

---

