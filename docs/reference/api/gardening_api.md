# gardening API Reference

> **Source**: `src/thegent/sitback/gardening.py`

Gardening manager for never-idle loop.

Manages proactive gardening checks: governance health, backlog, test failures,
traceability, escalations, quality, and DAG sync.

---

## GardeningManager

Manages aggressive gardening checks in never-idle loop.

Runs governance health, backlog checks, test failure detection,
traceability verification, escalation monitoring, quality gates,
and DAG synchronization.

### Methods

#### GardeningManager.__init__

Initialize the gardening manager.

Args:
    project_root: Root directory for the project. Defaults to cwd.

```python
__init__(self, project_root)
```

#### GardeningManager.clear_findings

Clear stored findings.

```python
clear_findings(self)
```

#### GardeningManager.get_findings

Return gardening findings that need attention.

```python
get_findings(self)
```

#### GardeningManager.get_last_results

Return results from last run of each step.

```python
get_last_results(self)
```

#### GardeningManager.get_summary

Return a summary of gardening status.

```python
get_summary(self)
```

---

## clear_findings

Clear stored findings.

```python
clear_findings(self)
```

---

## get_findings

Return gardening findings that need attention.

```python
get_findings(self)
```

---

## get_last_results

Return results from last run of each step.

```python
get_last_results(self)
```

---

## get_summary

Return a summary of gardening status.

```python
get_summary(self)
```

---

