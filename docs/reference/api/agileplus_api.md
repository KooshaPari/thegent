# agileplus API Reference

> **Source**: `src/thegent/governance/agileplus.py`

AgilePlus core loop orchestrator.

State machine: IDLE -> SCANNING -> ANALYZING -> PLANNING -> DEPLOYING -> VERIFYING -> COMMITTING -> IDLE

The loop composes scanner, analyzer, planner, deployer, verifier, and evidence
ledger to form a complete autonomous governance cycle.

---

## AgilePlusLoop

Orchestrates the complete 4X governance cycle.

States:
- IDLE: Health >= threshold, no action needed
- SCANNING: Running dimension scans
- ANALYZING: Prioritizing findings
- PLANNING: Generating remediation DAG
- DEPLOYING: Spawning agents
- VERIFYING: Post-task verification
- COMMITTING: Recording to evidence ledger

### Methods

#### AgilePlusLoop.__init__

```python
__init__(self, project_dir, health_targets_path, health_threshold, max_tasks_per_cycle, max_rerolls, lifecycle_mode)
```

#### AgilePlusLoop.cycle_id

Current cycle ID.

```python
cycle_id(self)
```

#### AgilePlusLoop.get_status

Get current status without running a cycle.

```python
get_status(self)
```

#### AgilePlusLoop.request_shutdown

Request graceful shutdown.

```python
request_shutdown(self)
```

#### AgilePlusLoop.run_continuous

Run continuous governance cycles.

Args:
    interval_seconds: Seconds between cycles
    max_cycles: Maximum cycles to run (None = infinite)

Returns:
    List of CycleResult for each completed cycle

```python
run_continuous(self, interval_seconds, max_cycles)
```

#### AgilePlusLoop.run_once

Run a single governance cycle.

Returns a CycleResult with the outcome of the complete
scan-analyze-plan-deploy-verify-commit loop.

```python
run_once(self, force)
```

#### AgilePlusLoop.state

Current cycle state.

```python
state(self)
```

---

## CycleResult

Result of a single AgilePlus cycle.

**Inherits from**: `BaseModel`

---

## CycleState

AgilePlus cycle states.

**Inherits from**: `str, Enum`

---

## cycle_id

Current cycle ID.

```python
cycle_id(self)
```

---

## get_status

Get current status without running a cycle.

```python
get_status(self)
```

---

## request_shutdown

Request graceful shutdown.

```python
request_shutdown(self)
```

---

## run_continuous

Run continuous governance cycles.

Args:
    interval_seconds: Seconds between cycles
    max_cycles: Maximum cycles to run (None = infinite)

Returns:
    List of CycleResult for each completed cycle

```python
run_continuous(self, interval_seconds, max_cycles)
```

---

## run_once

Run a single governance cycle.

Returns a CycleResult with the outcome of the complete
scan-analyze-plan-deploy-verify-commit loop.

```python
run_once(self, force)
```

---

## state

Current cycle state.

```python
state(self)
```

---

