# lanes API Reference

> **Source**: `src/thegent/orchestration/lanes.py`

Priority and urgency lane model (WP-1002, FR-019).

Defines execution lanes with priority ordering and critical lane protection.
Critical lane bypasses overload rejection and gets reserved capacity under burst.

---

## Lane

Canonical execution lanes (WP-1002).

**Inherits from**: `str, Enum`

---

## LaneModel

Priority and urgency lane model for task management (WP-1002, FR-019).

Usage:
    model = LaneModel()
    model.get_priority("critical")  # 0 (highest)
    model.is_protected("critical")   # True - bypasses overload rejection
    model.reserved_slots_for_critical  # 2

### Methods

#### LaneModel.check_capacity

Check if lane has capacity (starvation prevention, FR-019).

Critical lane always has capacity. Non-critical lanes leave reserved
slots for critical to prevent starvation under burst.

```python
check_capacity(cls, lane, active_count, total_capacity)
```

#### LaneModel.get_priority

Return numeric priority for a lane (lower = higher priority).

```python
get_priority(cls, lane)
```

#### LaneModel.get_urgency

Return urgency tier for a lane.

```python
get_urgency(cls, lane)
```

#### LaneModel.is_protected

True if lane bypasses overload rejection (FR-019 critical lane protection).

```python
is_protected(cls, lane)
```

#### LaneModel.sort_tasks

Sort tasks by lane priority (asc) then by creation time (asc).

```python
sort_tasks(cls, tasks)
```

---

## check_capacity

Check if lane has capacity (starvation prevention, FR-019).

Critical lane always has capacity. Non-critical lanes leave reserved
slots for critical to prevent starvation under burst.

```python
check_capacity(cls, lane, active_count, total_capacity)
```

---

## get_priority

Return numeric priority for a lane (lower = higher priority).

```python
get_priority(cls, lane)
```

---

## get_urgency

Return urgency tier for a lane.

```python
get_urgency(cls, lane)
```

---

## is_protected

True if lane bypasses overload rejection (FR-019 critical lane protection).

```python
is_protected(cls, lane)
```

---

## sort_tasks

Sort tasks by lane priority (asc) then by creation time (asc).

```python
sort_tasks(cls, tasks)
```

---

