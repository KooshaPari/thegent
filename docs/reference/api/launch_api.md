# launch API Reference

> **Source**: `src/thegent/ux/launch.py`

WP-6007: Post-launch observation and rollback reserve.

---

## LaunchObserver

Observes system health post-launch and manages rollback triggers.

### Methods

#### LaunchObserver.__init__

```python
__init__(self, settings)
```

#### LaunchObserver.check_health

Check post-launch health metrics.

```python
check_health(self)
```

#### LaunchObserver.trigger_rollback

Trigger an emergency rollback to the last stable state.

```python
trigger_rollback(self, reason)
```

---

## check_health

Check post-launch health metrics.

```python
check_health(self)
```

---

## trigger_rollback

Trigger an emergency rollback to the last stable state.

```python
trigger_rollback(self, reason)
```

---

