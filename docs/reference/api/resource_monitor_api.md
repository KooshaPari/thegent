# resource_monitor API Reference

> **Source**: `src/thegent/infra/resource_monitor.py`

Resource monitoring and leak detection using psutil.

---

## ResourceMonitor

Monitor system resources using psutil and detect leaks.

### Methods

#### ResourceMonitor.__init__

Initialize resource monitor.

Args:
    check_interval: Interval in seconds between monitoring checks.

```python
__init__(self, check_interval)
```

#### ResourceMonitor.detect_leak

Detect potential resource leaks from history.

Returns:
    Description of detected leak, or None if no leak detected.

```python
detect_leak(self)
```

#### ResourceMonitor.get_history

Get resource usage history.

```python
get_history(self)
```

#### ResourceMonitor.get_process_info

Get detailed process information using psutil.

Args:
    pid: Process ID.

Returns:
    Dictionary with process information, or None if process not found.

```python
get_process_info(self, pid)
```

#### ResourceMonitor.get_stats

Get current resource statistics using psutil.

```python
get_stats(self)
```

#### ResourceMonitor.start

Start monitoring thread.

```python
start(self)
```

#### ResourceMonitor.stop

Stop monitoring thread.

```python
stop(self)
```

---

## ResourceStats

Resource usage statistics.

### Methods

#### ResourceStats.get_suspicion_level

Get suspicion level and optimization suggestions.

Returns (level, suggestions) where level is one of:
- "low": Normal usage, no concerns
- "medium": Elevated usage, monitor
- "high": High usage, investigate
- "critical": Critical usage, immediate action needed

```python
get_suspicion_level(self)
```

#### ResourceStats.is_critical

Check if resource usage is critical.

Critical thresholds:
- FD usage > 80% (file descriptor exhaustion risk)
- Process count > 500 (very high, may indicate leak)
- Memory > 2048MB (2GB) for this process

```python
is_critical(self)
```

---

## detect_leak

Detect potential resource leaks from history.

Returns:
    Description of detected leak, or None if no leak detected.

```python
detect_leak(self)
```

---

## get_history

Get resource usage history.

```python
get_history(self)
```

---

## get_process_info

Get detailed process information using psutil.

Args:
    pid: Process ID.

Returns:
    Dictionary with process information, or None if process not found.

```python
get_process_info(self, pid)
```

---

## get_resource_monitor

Get global resource monitor.

---

## get_stats

Get current resource statistics using psutil.

```python
get_stats(self)
```

---

## get_suspicion_level

Get suspicion level and optimization suggestions.

Returns (level, suggestions) where level is one of:
- "low": Normal usage, no concerns
- "medium": Elevated usage, monitor
- "high": High usage, investigate
- "critical": Critical usage, immediate action needed

```python
get_suspicion_level(self)
```

---

## is_critical

Check if resource usage is critical.

Critical thresholds:
- FD usage > 80% (file descriptor exhaustion risk)
- Process count > 500 (very high, may indicate leak)
- Memory > 2048MB (2GB) for this process

```python
is_critical(self)
```

---

## start

Start monitoring thread.

```python
start(self)
```

---

## stop

Stop monitoring thread.

```python
stop(self)
```

---

