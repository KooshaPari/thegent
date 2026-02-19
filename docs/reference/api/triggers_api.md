# triggers API Reference

> **Source**: `src/thegent/governance/triggers.py`

AgilePlus trigger modes: watchdog, timer, and manual.

Provides three ways to trigger governance cycles:
- Watchdog: File system watcher with debounce
- Timer: Periodic interval-based triggering
- Manual: One-shot CLI invocation

---

## HealthThresholdTrigger

Trigger governance cycle when health drops below threshold.

### Methods

#### HealthThresholdTrigger.__init__

```python
__init__(self, loop, threshold, check_interval)
```

#### HealthThresholdTrigger.start

Start health monitoring in background.

```python
start(self)
```

#### HealthThresholdTrigger.stop

Stop health monitoring.

```python
stop(self)
```

---

## ManualTrigger

One-shot manual trigger.

Runs a single governance cycle and exits.

### Methods

#### ManualTrigger.__init__

```python
__init__(self, loop)
```

#### ManualTrigger.run

Run a single governance cycle.

```python
run(self, force)
```

---

## TimerTrigger

Periodic timer-based trigger.

Triggers governance cycles at fixed intervals.

### Methods

#### TimerTrigger.__init__

```python
__init__(self, loop, config)
```

#### TimerTrigger.start

Start the timer trigger.

```python
start(self)
```

#### TimerTrigger.stop

Stop the timer trigger.

```python
stop(self)
```

---

## TriggerConfig

Configuration for trigger modes.

**Inherits from**: `BaseModel`

---

## TriggerProtocol

Protocol for trigger implementations.

**Inherits from**: `Protocol`

### Methods

#### TriggerProtocol.start

```python
start(self)
```

#### TriggerProtocol.stop

```python
stop(self)
```

---

## WatchdogTrigger

File system watcher trigger with debounce.

Uses watchdog library to watch specified paths for changes and
triggers cycles after a debounce period without new changes.

### Methods

#### WatchdogTrigger.__init__

```python
__init__(self, loop, config)
```

#### WatchdogTrigger.start

Start the watchdog trigger.

```python
start(self)
```

#### WatchdogTrigger.stop

Stop the watchdog trigger.

```python
stop(self)
```

---

## _WatchdogEventHandler

Event handler for watchdog file system events.

Filters events to only process relevant file changes.

**Inherits from**: `FileSystemEventHandler`

### Methods

#### _WatchdogEventHandler.__init__

```python
__init__(self, on_change, exclude_dirs, watch_extensions)
```

#### _WatchdogEventHandler.on_created

Called when a file is created.

```python
on_created(self, event)
```

#### _WatchdogEventHandler.on_deleted

Called when a file is deleted.

```python
on_deleted(self, event)
```

#### _WatchdogEventHandler.on_modified

Called when a file is modified.

```python
on_modified(self, event)
```

---

## create_trigger

Factory function to create the appropriate trigger.

```python
create_trigger(mode, loop, config)
```

---

## main

CLI entry point for triggers.

---

## monitor

---

## on_created

Called when a file is created.

```python
on_created(self, event)
```

---

## on_deleted

Called when a file is deleted.

```python
on_deleted(self, event)
```

---

## on_modified

Called when a file is modified.

```python
on_modified(self, event)
```

---

## run

Run a single governance cycle.

```python
run(self, force)
```

---

## shutdown

```python
shutdown(signum, frame)
```

---

## start

Start health monitoring in background.

```python
start(self)
```

---

## stop

Stop health monitoring.

```python
stop(self)
```

---

