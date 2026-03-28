# state API Reference

> **Source**: `src/thegent/execution/state.py`

Execution run metadata and registry for thegent orchestration.

DEPRECATED: Domain entities are now in thegent.domain.entities.run.
This module is kept for backward compatibility and CalibrationRegistry.

---

## CalibrationRegistry

WP-4008: Persists calibration factors and curves for agents (G-GP-09).

### Methods

#### CalibrationRegistry.__init__

```python
__init__(self: Any, session_dir: Path)
```

---

#### CalibrationRegistry.get_factor

```python
get_factor(self: Any, agent: str)
```

Return the persisted calibration factor for an agent.

---

#### CalibrationRegistry.update_agent

```python
update_agent(self: Any, agent: str, factor: float, sample_size: int)
```

Persist a new calibration factor for an agent.

---

---

## get_execution_diagnostics

Return diagnostics snapshot for execution-path degradation.

---

## get_factor

```python
get_factor(self: Any, agent: str)
```

Return the persisted calibration factor for an agent.

---

## reset_execution_diagnostics

Reset execution diagnostics (test helper).

---

## update_agent

```python
update_agent(self: Any, agent: str, factor: float, sample_size: int)
```

Persist a new calibration factor for an agent.

---

