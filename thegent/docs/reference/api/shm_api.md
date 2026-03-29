# shm API Reference

> **Source**: `src/thegent/orchestration/shm.py`

## SHMSystem

Wrapper for thegent_shm Rust extension.

### Methods

#### SHMSystem.award_xp

```python
award_xp(self: Any, amount: int)
```

---

#### SHMSystem.get_xp_state

```python
get_xp_state(self: Any)
```

---

#### SHMSystem.is_native_active

```python
is_native_active(self: Any)
```

---

#### SHMSystem.is_open

```python
is_open(self: Any, target: str, category: str, threshold: int, window_s: int, recovery_s: int)
```

---

#### SHMSystem.record_failure

```python
record_failure(self: Any, target: str, category: str)
```

---

#### SHMSystem.set_level

```python
set_level(self: Any, level: int)
```

---

---

## award_xp

```python
award_xp(self: Any, amount: int)
```

---

## get_shm_system

```python
get_shm_system(session_dir: Path) -> SHMSystem
```

---

## get_xp_state

```python
get_xp_state(self: Any) -> dict[(str, Any)]
```

---

## is_native_active

```python
is_native_active(self: Any) -> bool
```

---

## is_open

```python
is_open(self: Any, target: str, category: str, threshold: int, window_s: int, recovery_s: int) -> bool
```

---

## record_failure

```python
record_failure(self: Any, target: str, category: str)
```

---

## set_level

```python
set_level(self: Any, level: int)
```

---
