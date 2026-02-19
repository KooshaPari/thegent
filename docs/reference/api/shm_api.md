# shm API Reference

> **Source**: `src/thegent/orchestration/shm.py`

## SHMSystem

Wrapper for thegent_shm Rust extension.

### Methods

#### SHMSystem.award_xp

```python
award_xp(self, amount)
```

#### SHMSystem.get_xp_state

```python
get_xp_state(self)
```

#### SHMSystem.is_native_active

```python
is_native_active(self)
```

#### SHMSystem.is_open

```python
is_open(self, target, category, threshold, window_s, recovery_s)
```

#### SHMSystem.record_failure

```python
record_failure(self, target, category)
```

#### SHMSystem.set_level

```python
set_level(self, level)
```

---

## award_xp

```python
award_xp(self, amount)
```

---

## get_shm_system

```python
get_shm_system(session_dir)
```

---

## get_xp_state

```python
get_xp_state(self)
```

---

## is_native_active

```python
is_native_active(self)
```

---

## is_open

```python
is_open(self, target, category, threshold, window_s, recovery_s)
```

---

## record_failure

```python
record_failure(self, target, category)
```

---

## set_level

```python
set_level(self, level)
```

---

