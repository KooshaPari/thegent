# errors API Reference

> **Source**: `src/thegent/utils/errors.py`

Error handling utilities for thegent.

Common error handling patterns and custom exceptions.

---

## AuthenticationError

Authentication errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `AuthenticationError -> ThegentError`

---

## ConfigurationError

Configuration-related errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `ConfigurationError -> ThegentError`

---

## ErrorContext

Context manager for error handling.

### Methods

#### ErrorContext.__init__

```python
__init__(self: Any, context: str, reraise: bool, log_level: str)
```

---

---

## NetworkError

Network-related errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `NetworkError -> ThegentError`

---

## NotFoundError

Resource not found errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `NotFoundError -> ThegentError`

---

## RateLimitError

Rate limiting errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `RateLimitError -> ThegentError`

---

## ThegentError

Base exception for thegent.

**Inherits from**: `Exception`

---

## TimeoutError

Timeout errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `TimeoutError -> ThegentError`

---

## ValidationError

Validation errors.

**Inherits from**: `ThegentError`

**Method Resolution Order**: `ValidationError -> ThegentError`

---

## decorator

```python
decorator(func: Callable[(Ellipsis, T)]) -> Callable[(Ellipsis, T)]
```

---

## handle_error

```python
handle_error(error: Exception, context: str, reraise: bool, log_level: str)
```

Handle an error with consistent logging.

**Parameters**:

- `error`: The exception that occurred
- `context`: Additional context about where the error occurred
- `reraise`: Whether to re-raise the exception after handling
- `log_level`: Logging level (debug, info, warning, error, critical)

---

## safe_execute

```python
safe_execute(func: Callable[(Ellipsis, T)])
```

Execute a function safely, returning default on error.

**Parameters**:

- `func`: Function to execute
- `*args`: Positional arguments for func
- `default`: Default value to return on error
- `log_errors`: Whether to log errors
- `**kwargs`: Keyword arguments for func

**Returns**: Result of func or default on error

---

## suppress_errors

```python
suppress_errors(default: Any)
```

Decorator that suppresses errors and returns default.

**Parameters**:

- `default`: Default value to return on error

**Examples**:

```python
@suppress_errors(default=[])
def get_items():
    raise ValueError("test")
```

---

## wrap_errors

```python
wrap_errors(new_exception: type[Exception])
```

Decorator that wraps errors in a new exception type.

**Parameters**:

- `new_exception`: Exception type to wrap with

**Examples**:

```python
@wrap_errors(NetworkError)
def fetch_url(url: str) -> str:
    raise ValueError("invalid")
```

---

## wrapper

---

