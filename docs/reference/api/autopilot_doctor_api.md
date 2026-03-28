# autopilot_doctor API Reference

> **Source**: `src/thegent/integrations/autopilot_doctor.py`

Autopilot Doctor Command for system health checks.

WL-172: Autopilot Doctor Command
Provides diagnostic checks and health monitoring for the autopilot system.

---

## AutopilotDoctor

Doctor command for running system health checks.

### Methods

#### AutopilotDoctor.__init__

```python
__init__(self: Any)
```

Initialize the autopilot doctor.

---

#### AutopilotDoctor.add_check

```python
add_check(self: Any, name: str, check_fn: Callable[(Any, bool)], message: str)
```

Register a health check.

**Parameters**:

- `name`: Unique name for the check.
- `check_fn`: Callable that returns True if check passed, False otherwise.
- `message`: Optional message to display with results.

---

#### AutopilotDoctor.all_passed

```python
all_passed(checks: list[DoctorCheck])
```

Check if all health checks passed.

**Parameters**:

- `checks`: List of DoctorCheck results.

**Returns**: True if all checks passed, False otherwise.

---

#### AutopilotDoctor.run

```python
run(self: Any)
```

Run all registered checks and return results.

**Returns**: List of DoctorCheck results.

---

---

## DoctorCheck

Result of a single diagnostic check.

---

## add_check

```python
add_check(self: Any, name: str, check_fn: Callable[(Any, bool)], message: str)
```

Register a health check.

**Parameters**:

- `name`: Unique name for the check.
- `check_fn`: Callable that returns True if check passed, False otherwise.
- `message`: Optional message to display with results.

---

## all_passed

```python
all_passed(checks: list[DoctorCheck])
```

Check if all health checks passed.

**Parameters**:

- `checks`: List of DoctorCheck results.

**Returns**: True if all checks passed, False otherwise.

---

## run

```python
run(self: Any)
```

Run all registered checks and return results.

**Returns**: List of DoctorCheck results.

---

