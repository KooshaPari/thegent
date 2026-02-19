# resource_limits API Reference

> **Source**: `src/thegent/infra/resource_limits.py`

Resource limits and enforcement.

---

## ResourceLimits

Manage and enforce resource limits.

### Methods

#### ResourceLimits.__init__

Initialize resource limits manager.

```python
__init__(self)
```

#### ResourceLimits.get_fd_limit

Get current FD limit.

Returns:
    Current file descriptor limit.

```python
get_fd_limit(self)
```

#### ResourceLimits.get_process_limit

Get current process limit.

Returns:
    Current process limit, or default if not available.

```python
get_process_limit(self)
```

#### ResourceLimits.restore_limits

Restore original limits.

```python
restore_limits(self)
```

---

## get_fd_limit

Get current FD limit.

Returns:
    Current file descriptor limit.

```python
get_fd_limit(self)
```

---

## get_process_limit

Get current process limit.

Returns:
    Current process limit, or default if not available.

```python
get_process_limit(self)
```

---

## get_resource_limits

Get global resource limits manager.

---

## restore_limits

Restore original limits.

```python
restore_limits(self)
```

---

