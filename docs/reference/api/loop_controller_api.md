# loop_controller API Reference

> **Source**: `src/thegent/agents/loop_controller.py`

Lifecycle Loop Controller with Checker Agent oversight.

---

## LifecycleController

Handles agent execution loops (Ralph Wiggum loops) with Checker Agent oversight.

### Methods

#### LifecycleController.__init__

```python
__init__(self, settings, worker_agent_name, checker_agent_name, mode, max_iterations, worker_model, task_id, verification_callback)
```

#### LifecycleController.run_loop

Execute the Lifecycle loop.

```python
run_loop(self, initial_prompt, todo_spec, on_worker_output, on_progress)
```

---

## LoopMode

Lifecycle loop modes.

**Inherits from**: `str, Enum`

---

## LoopState

Current state of a Lifecycle loop.

**Inherits from**: `BaseModel`

---

## run_loop

Execute the Lifecycle loop.

```python
run_loop(self, initial_prompt, todo_spec, on_worker_output, on_progress)
```

---

