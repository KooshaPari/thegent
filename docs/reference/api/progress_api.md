# progress API Reference

> **Source**: `src/thegent/infra/progress.py`

Progress indicators and status updates for long-running operations.

This module provides utilities for displaying progress bars, spinners, and
status updates in a consistent, beautiful way.

---

## decorator

```python
decorator(func: Any)
```

---

## measure_time

```python
measure_time(description: str)
```

Decorator to measure and display execution time.

**Parameters**:

- `description`: Description of the operation

**Examples**:

```python
>>> @measure_time("Processing data")
... def process_data():
...     time.sleep(1)
```

---

## print_section

```python
print_section(title: str)
```

Print a section header.

**Parameters**:

- `title`: Section title

**Examples**:

```python
>>> print_section("Configuration")
```

---

## print_status

```python
print_status(message: str, status: str)
```

Print a status message with appropriate styling.

**Parameters**:

- `message`: Status message
- `status`: Status type (info, success, warning, error)

**Examples**:

```python
>>> print_status("Operation completed", "success")
```

---

## print_step

```python
print_step(step: int, total: int, message: str)
```

Print a step indicator.

**Parameters**:

- `step`: Current step number
- `total`: Total number of steps
- `message`: Step message

**Examples**:

```python
>>> print_step(1, 3, "Installing dependencies")
```

---

## progress_context

```python
progress_context(description: str, total: Any, show_eta: bool, show_speed: bool)
```

Context manager for progress tracking.

**Parameters**:

- `description`: Description of the operation
- `total`: Total number of steps (None for indeterminate)
- `show_eta`: Show estimated time remaining
- `show_speed`: Show processing speed

**Examples**:

```python
>>> with progress_context("Processing files", total=100) as progress:
...     for i in range(100):
...         progress.update(1)
```

---

## spinner_context

```python
spinner_context(message: str)
```

Context manager for spinner display.

**Parameters**:

- `message`: Message to display while spinning

**Examples**:

```python
>>> with spinner_context("Loading data..."):
...     time.sleep(2)
```

---

## wrapper

---

