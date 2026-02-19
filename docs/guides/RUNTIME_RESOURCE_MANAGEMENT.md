# Runtime Resource Management Guide

**Quick reference for preventing resource leaks in thegent.**

---

## Quick Start

### Using Subprocess Manager (Recommended)

**For new code, always use the subprocess manager:**

```python
from thegent.infra.subprocess_manager import get_subprocess_manager

manager = get_subprocess_manager()

# Context manager - automatic cleanup
with manager.popen(["command", "args"], name="my-process") as proc:
    # Process automatically cleaned up on exit
    result = proc.wait()

# Or use run() for simple cases
result = manager.run(
    ["command", "args"],
    name="my-process",
    timeout=30.0,
)
```

### Registering Existing Processes

**For existing `subprocess.Popen` calls, register them:**

```python
from thegent.infra.process_registry import get_registry

proc = subprocess.Popen([...], ...)
registry = get_registry()
registry.register(proc=proc, name="process-name", cleanup_on_exit=True)
```

### File Handling

**Always use context managers:**

```python
# ✅ CORRECT
with open(file_path, "w") as f:
    proc = subprocess.Popen([...], stdout=f)
    registry.register(proc, name="process")

# ❌ WRONG - File handle leak
proc = subprocess.Popen([...], stdout=open(file_path, "w"))
```

---

## Common Patterns

### Background Process

```python
from thegent.infra.process_registry import get_registry

with open(output_file, "w") as f:
    proc = subprocess.Popen(
        ["long-running", "command"],
        stdout=f,
        stderr=subprocess.DEVNULL,
    )
    registry = get_registry()
    registry.register(proc, name="background-task", cleanup_on_exit=True)
    # Process runs in background, cleaned up on exit
```

### Process with Output Capture

```python
from thegent.infra.subprocess_manager import get_subprocess_manager

manager = get_subprocess_manager()
result = manager.run(
    ["command", "args"],
    name="capture-output",
    timeout=10.0,
    capture_output=True,
    text=True,
)
print(result.stdout)
```

### Process Pool

```python
from thegent.infra.subprocess_manager import get_subprocess_manager

manager = get_subprocess_manager()
processes = []

try:
    for item in items:
        proc = manager.popen(
            ["process", item],
            name=f"process-{item}",
        )
        processes.append(proc)
    
    # Wait for all
    for proc in processes:
        proc.wait()
finally:
    # Cleanup handled by context manager
    pass
```

---

## Resource Monitoring

### Check Current Resource Usage

```python
from thegent.infra.resource_monitor import get_resource_monitor

monitor = get_resource_monitor()
stats = monitor.get_stats()

print(f"File descriptors: {stats.fd_count}/{stats.fd_limit}")
print(f"Processes: {stats.process_count}")
print(f"Memory: {stats.memory_mb}MB")
```

### Detect Leaks

```python
monitor = get_resource_monitor()
leak = monitor.detect_leak()
if leak:
    print(f"Leak detected: {leak}")
```

### Process Registry Stats

```python
from thegent.infra.process_registry import get_registry

registry = get_registry()
stats = registry.get_stats()

print(f"Total processes: {stats['total']}")
print(f"Alive: {stats['alive']}")
print(f"Dead: {stats['dead']}")
```

---

## Anti-Patterns to Avoid

### ❌ Don't: Create Popen without tracking

```python
# ❌ Process leak
proc = subprocess.Popen([...])
# Process never cleaned up
```

### ❌ Don't: Open files without context managers

```python
# ❌ File descriptor leak
proc = subprocess.Popen([...], stdout=open("file.txt", "w"))
# File handle never closed
```

### ❌ Don't: Leave PIPE streams undrained

```python
# ❌ Can cause blocking
proc = subprocess.Popen([...], stdout=subprocess.PIPE)
# If process writes to stdout and we don't read, buffer fills
# Process blocks, FD held
```

### ❌ Don't: Ignore process exit codes

```python
# ❌ Zombie process
proc = subprocess.Popen([...])
# Never wait() or communicate(), process becomes zombie
```

---

## Best Practices

1. **Always use subprocess manager** for new code
2. **Register all Popen calls** in existing code
3. **Use context managers** for file handles
4. **Drain PIPE streams** or use DEVNULL
5. **Set timeouts** for all subprocess calls
6. **Monitor resource usage** in long-running processes
7. **Clean up on errors** using try/finally

---

## Migration Checklist

When updating existing code:

- [ ] Replace `subprocess.Popen` with `manager.popen()` context manager
- [ ] Replace `subprocess.run` with `manager.run()`
- [ ] Register any remaining `subprocess.Popen` calls
- [ ] Ensure file handles use `with open()`
- [ ] Add timeouts to all subprocess calls
- [ ] Test for resource leaks
- [ ] Monitor resource usage

---

## See Also

- [RUNTIME_INFRASTRUCTURE_RESOURCE_LEAKS_AUDIT_AND_PLAN.md](../research/RUNTIME_INFRASTRUCTURE_RESOURCE_LEAKS_AUDIT_AND_PLAN.md) — Comprehensive audit and plan
- [PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md](../research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md) — Production packaging plan
