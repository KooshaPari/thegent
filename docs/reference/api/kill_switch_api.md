# kill_switch API Reference

> **Source**: `src/thegent/governance/kill_switch.py`

WP-39001: Super-intelligence Safety Break (Kill-Switch).
Provides an emergency override to immediately halt all agent operations if recursive self-improvement
exceeds human-defined safety bounds.

---

## SafetyKillSwitch

Hard-wired emergency stop for all agent processes.

### Methods

#### SafetyKillSwitch.__init__

```python
__init__(self, workspace_root)
```

#### SafetyKillSwitch.activate

WP-39001: Trigger the global kill-switch.

```python
activate(self, reason)
```

#### SafetyKillSwitch.check_status

Check if the system is currently halted.

```python
check_status(self)
```

#### SafetyKillSwitch.verify_alignment_drift

Monitor for dangerous recursive improvement speed.

```python
verify_alignment_drift(self, self_improvement_rate)
```

---

## activate

WP-39001: Trigger the global kill-switch.

```python
activate(self, reason)
```

---

## check_status

Check if the system is currently halted.

```python
check_status(self)
```

---

## verify_alignment_drift

Monitor for dangerous recursive improvement speed.

```python
verify_alignment_drift(self, self_improvement_rate)
```

---

