# triggers API Reference

> **Source**: `src/thegent/governance/triggers.py`

AgilePlus trigger modes: watchdog, timer, and manual.

Provides three ways to trigger governance cycles:
- Watchdog: File system watcher with debounce (uses watchfiles for 5-10x performance)
- Timer: Periodic interval-based triggering
- Manual: One-shot CLI invocation

---

## HealthThresholdTrigger

Trigger governance cycle when health drops below threshold.

### Methods

#### HealthThresholdTrigger.__init__

```python
__init__(self: Any, loop: Any, threshold: float, check_interval: int)
```

---

#### HealthThresholdTrigger.run

```python
run(self: Any, force: bool)
```

Run a single governance cycle (for health threshold, triggers immediately).

---

#### HealthThresholdTrigger.start

```python
start(self: Any)
```

Start health monitoring in background.

---

#### HealthThresholdTrigger.stop

```python
stop(self: Any)
```

Stop health monitoring.

---

---

## ManualTrigger

One-shot manual trigger.

Runs a single governance cycle and exits.

### Methods

#### ManualTrigger.__init__

```python
__init__(self: Any, loop: Any)
```

---

#### ManualTrigger.run

```python
run(self: Any, force: bool)
```

Run a single governance cycle.

---

#### ManualTrigger.start

```python
start(self: Any)
```

Start the trigger (no-op for manual mode).

---

#### ManualTrigger.stop

```python
stop(self: Any)
```

Stop the trigger (no-op for manual mode).

---

---

## TimerTrigger

Periodic timer-based trigger.

Triggers governance cycles at fixed intervals.

### Methods

#### TimerTrigger.__init__

```python
__init__(self: Any, loop: Any, config: TriggerConfig)
```

---

#### TimerTrigger.run

```python
run(self: Any, force: bool)
```

Run a single governance cycle (for timer, triggers immediately).

---

#### TimerTrigger.start

```python
start(self: Any)
```

Start the timer trigger.

---

#### TimerTrigger.stop

```python
stop(self: Any)
```

Stop the timer trigger.

---

---

## TriggerConfig

Configuration for trigger modes.

**Inherits from**: `BaseModel`

---

## TriggerProtocol

Protocol for trigger implementations.

**Inherits from**: `Protocol`

### Methods

#### TriggerProtocol.run

```python
run(self: Any, force: bool)
```

---

#### TriggerProtocol.start

```python
start(self: Any)
```

---

#### TriggerProtocol.stop

```python
stop(self: Any)
```

---

---

## WatchdogTrigger

File system watcher trigger with debounce.

Uses watchfiles (5-10x faster) or watchdog fallback to watch specified paths
for changes and triggers cycles after a debounce period without new changes.

### Methods

#### WatchdogTrigger.__init__

```python
__init__(self: Any, loop: Any, config: TriggerConfig)
```

---

#### WatchdogTrigger.run

```python
run(self: Any, force: bool)
```

Run a single governance cycle (for watchdog, triggers immediately).

---

#### WatchdogTrigger.start

```python
start(self: Any)
```

Start the watchdog trigger.

---

#### WatchdogTrigger.stop

```python
stop(self: Any)
```

Stop the watchdog trigger.

---

---

## _WatchdogEventHandler

Event handler for watchdog file system events (fallback).

Filters events to only process relevant file changes.
Only used when watchfiles is not available.

**Inherits from**: `FileSystemEventHandler`

### Methods

#### _WatchdogEventHandler.__init__

```python
__init__(self: Any, on_change: Any, exclude_dirs: frozenset[str], watch_extensions: frozenset[str])
```

---

#### _WatchdogEventHandler.on_created

```python
on_created(self: Any, event: Any)
```

Called when a file is created.

---

#### _WatchdogEventHandler.on_deleted

```python
on_deleted(self: Any, event: Any)
```

Called when a file is deleted.

---

#### _WatchdogEventHandler.on_modified

```python
on_modified(self: Any, event: Any)
```

Called when a file is modified.

---

---

## cli

```python
cli(mode: str, interval: int, debounce: int, max_cycles: Any, force: bool, watch: Any, project_dir: Path, health_targets: Any, threshold: float, lifecycle_mode: str, watch_health: float, watch_health_interval: int)
```

Run AgilePlus trigger modes.

---

## create_trigger

```python
create_trigger(mode: str, loop: Any, config: TriggerConfig)
```

Factory function to create the appropriate trigger.

---

## main

CLI entry point for triggers.

---

## monitor

---

## on_created

```python
on_created(self: Any, event: Any)
```

Called when a file is created.

---

## on_deleted

```python
on_deleted(self: Any, event: Any)
```

Called when a file is deleted.

---

## on_modified

```python
on_modified(self: Any, event: Any)
```

Called when a file is modified.

---

## run

```python
run(self: Any, force: bool)
```

Run a single governance cycle (for health threshold, triggers immediately).

---

## shutdown

```python
shutdown(signum: int, frame: Any) -> None
```

---

## start

```python
start(self: Any)
```

Start health monitoring in background.

---

## stop

```python
stop(self: Any)
```

Stop health monitoring.

---

## watch_filter

```python
watch_filter(change: Change, path_str: str)
```

Filter changes to only process relevant files.

---

