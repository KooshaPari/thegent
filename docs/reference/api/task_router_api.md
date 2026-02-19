# task_router API Reference

> **Source**: `src/thegent/routing/task_router.py`

## ConstraintValidator

Validates task metadata against configured constraints.

### Methods

#### ConstraintValidator.__init__

```python
__init__(self, config)
```

#### ConstraintValidator.validate

Validate task against hard constraints:
- Instantaneous cost (per-call)
- Cumulative cost (MTD per category)
- Speed (SLA)

```python
validate(self, task_metadata, registry, model)
```

---

## TaskClassifier

Categorizes tasks based on prompt analysis and heuristics.

### Methods

#### TaskClassifier.__init__

```python
__init__(self, config)
```

#### TaskClassifier.classify

Classify task complexity based on prompt content.
Heuristics:
- Word count (token estimate proxy)
- Keywords (architecture, design -> HIGH_COMPLEX)
- Structure (bullets, code blocks -> COMPLEX)

```python
classify(self, prompt, agent_role)
```

#### TaskClassifier.detect_role

Detect task role from agent metadata or prompt keywords.

Priority:
1. Agent-specified role (from agent frontmatter)
2. Auto-detect from prompt keywords
3. Default to "workhorse"

Args:
    prompt: User prompt text
    agent_role: Role from agent metadata (e.g., "planner", "writer", "researcher")

Returns:
    Role string (workhorse/researcher/writer_fast/writer_high/planner/large_context)

```python
detect_role(self, prompt, agent_role)
```

---

## TaskRouter

Orchestrates task classification and constraint validation.

### Methods

#### TaskRouter.__init__

```python
__init__(self, config)
```

#### TaskRouter.classify

Classify task.

```python
classify(self, prompt)
```

#### TaskRouter.find_active_terminal_for_path

Find an active tmux pane matching the given project path.
Returns pane_id if found.

```python
find_active_terminal_for_path(self, path)
```

#### TaskRouter.get_fallback_chain

Get LiteLLM-style fallback chain for task category (WP-1001).

```python
get_fallback_chain(self, category)
```

#### TaskRouter.route

Full routing: classify + validate.
Returns (TaskMetadata, violations).

```python
route(self, prompt, registry, model)
```

#### TaskRouter.route_by_capability

Route to an agent based on task capability (WP-1007).

```python
route_by_capability(self, task_type)
```

#### TaskRouter.route_dag_tasks

Route multiple tasks from a DAG, considering dependencies (WP-1001).

```python
route_dag_tasks(self, dag)
```

#### TaskRouter.shape_task

WP-11006: Adaptive task shaping (split/merge engine).

```python
shape_task(self, prompt, category)
```

#### TaskRouter.should_delegate_to_reviewer

Determine if a task should be delegated to a reviewer based on confidence (WP-1007).

```python
should_delegate_to_reviewer(self, confidence)
```

#### TaskRouter.validate

Validate task against constraints.

```python
validate(self, task_metadata, registry, model)
```

---

## classify

Classify task.

```python
classify(self, prompt)
```

---

## detect_role

Detect task role from agent metadata or prompt keywords.

Priority:
1. Agent-specified role (from agent frontmatter)
2. Auto-detect from prompt keywords
3. Default to "workhorse"

Args:
    prompt: User prompt text
    agent_role: Role from agent metadata (e.g., "planner", "writer", "researcher")

Returns:
    Role string (workhorse/researcher/writer_fast/writer_high/planner/large_context)

```python
detect_role(self, prompt, agent_role)
```

---

## find_active_terminal_for_path

Find an active tmux pane matching the given project path.
Returns pane_id if found.

```python
find_active_terminal_for_path(self, path)
```

---

## get_fallback_chain

Get LiteLLM-style fallback chain for task category (WP-1001).

```python
get_fallback_chain(self, category)
```

---

## route

Full routing: classify + validate.
Returns (TaskMetadata, violations).

```python
route(self, prompt, registry, model)
```

---

## route_by_capability

Route to an agent based on task capability (WP-1007).

```python
route_by_capability(self, task_type)
```

---

## route_dag_tasks

Route multiple tasks from a DAG, considering dependencies (WP-1001).

```python
route_dag_tasks(self, dag)
```

---

## shape_task

WP-11006: Adaptive task shaping (split/merge engine).

```python
shape_task(self, prompt, category)
```

---

## should_delegate_to_reviewer

Determine if a task should be delegated to a reviewer based on confidence (WP-1007).

```python
should_delegate_to_reviewer(self, confidence)
```

---

## validate

Validate task against constraints.

```python
validate(self, task_metadata, registry, model)
```

---

