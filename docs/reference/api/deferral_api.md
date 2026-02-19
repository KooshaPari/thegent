# deferral API Reference

> **Source**: `src/thegent/orchestration/deferral.py`

WP-5004: Non-critical deferral rules.

---

## DeferralManager

Manages deferral of non-critical tasks under high load.

### Methods

#### DeferralManager.__init__

```python
__init__(self, settings)
```

#### DeferralManager.defer_task

Record a task as deferred.

```python
defer_task(self, task_id, reason)
```

#### DeferralManager.list_deferred

List all currently deferred tasks.

```python
list_deferred(self)
```

#### DeferralManager.should_defer

Determine if a task should be deferred.
Priority: P0 (critical) to P3 (low).

```python
should_defer(self, task_priority, load_level)
```

---

## DeferralRule

Rule for deferring non-critical tasks.

### Methods

#### DeferralRule.__init__

```python
__init__(self, id, condition, action)
```

---

## defer_task

Record a task as deferred.

```python
defer_task(self, task_id, reason)
```

---

## list_deferred

List all currently deferred tasks.

```python
list_deferred(self)
```

---

## should_defer

Determine if a task should be deferred.
Priority: P0 (critical) to P3 (low).

```python
should_defer(self, task_priority, load_level)
```

---

