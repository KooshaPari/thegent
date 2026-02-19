# plan_system API Reference

> **Source**: `src/thegent/integration/plan_system.py`

Integration with PLAN.md and plan status tracking.

---

## PlanSystemIntegration

Integrate with PLAN.md and plan status.

This class handles integration with the project plan system,
including parsing PLAN.md, tracking task status, and managing dependencies.

Examples:
    >>> integration = PlanSystemIntegration()
    >>> tasks = integration.get_tasks_for_phase("Phase 1")
    >>> integration.update_task_status("task-1.1", "completed")
    >>> blocked = integration.get_blocked_tasks()

### Methods

#### PlanSystemIntegration.__init__

Initialize plan system integration.

Args:
    plan_file: Path to PLAN.md file. Defaults to PLAN.md
    plan_status_file: Path to PLAN_STATUS.md file.
                      Defaults to docs/reference/PLAN_STATUS.md

```python
__init__(self, plan_file, plan_status_file)
```

#### PlanSystemIntegration.get_blocked_tasks

Get tasks blocked by incomplete dependencies.

Returns:
    List of blocked task dictionaries

```python
get_blocked_tasks(self)
```

#### PlanSystemIntegration.get_tasks_for_phase

Get tasks for specific phase.

Args:
    phase: Phase identifier (e.g., "Phase 1" or "1")

Returns:
    List of task dictionaries

```python
get_tasks_for_phase(self, phase)
```

#### PlanSystemIntegration.update_task_status

Update task status in plan.

Updates both PLAN.md (if task is in plan) and PLAN_STATUS.md.

Args:
    task_id: ID of task to update
    status: New status (e.g., "completed", "in_progress", "pending")

```python
update_task_status(self, task_id, status)
```

---

## get_blocked_tasks

Get tasks blocked by incomplete dependencies.

Returns:
    List of blocked task dictionaries

```python
get_blocked_tasks(self)
```

---

## get_tasks_for_phase

Get tasks for specific phase.

Args:
    phase: Phase identifier (e.g., "Phase 1" or "1")

Returns:
    List of task dictionaries

```python
get_tasks_for_phase(self, phase)
```

---

## update_task_status

Update task status in plan.

Updates both PLAN.md (if task is in plan) and PLAN_STATUS.md.

Args:
    task_id: ID of task to update
    status: New status (e.g., "completed", "in_progress", "pending")

```python
update_task_status(self, task_id, status)
```

---

