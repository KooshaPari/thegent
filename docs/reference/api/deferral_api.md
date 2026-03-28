# deferral API Reference

> **Source**: `src/thegent/orchestration/resilience/deferral.py`

WP-5004: Non-critical deferral rules.

WL-038: $defer <task> syntax — parse agent output and inject into PromptQueue.

---

## DeferralManager

Manages deferral of non-critical tasks under high load.

### Methods

#### DeferralManager.__init__

```python
__init__(self: Any, settings: ThegentSettings)
```

---

#### DeferralManager.defer_task

```python
defer_task(self: Any, task_id: str, reason: str)
```

Record a task as deferred.

---

#### DeferralManager.list_deferred

```python
list_deferred(self: Any)
```

List all currently deferred tasks.

---

#### DeferralManager.should_defer

```python
should_defer(self: Any, task_priority: str, load_level: float)
```

Determine if a task should be deferred.

Priority: P0 (critical) to P3 (low).

---

---

## DeferralRule

Rule for deferring non-critical tasks.

### Methods

#### DeferralRule.__init__

```python
__init__(self: Any, id: str, condition: str, action: str)
```

---

---

## defer_task

```python
defer_task(self: Any, task_id: str, reason: str)
```

Record a task as deferred.

---

## extract_deferred_tasks

```python
extract_deferred_tasks(output: str)
```

Parse ``$defer <task>`` directives from agent stdout/stderr.

Scans every line of *output* for the ``$defer`` syntax and returns the
list of deferred task texts in order of appearance.  Lines that do not
match are silently ignored.

# @trace WL-038

**Parameters**:

- `output`: Combined stdout/stderr text from an agent run.

**Returns**: Ordered list of deferred task description strings (stripped).

---

## inject_deferred_tasks

```python
inject_deferred_tasks(deferred_tasks: list[str], queue_path: Path, project: str, agent: Any)
```

Append deferred tasks to the Unified Prompt Queue as ``pending`` entries.

Each task text becomes a new entry in *queue_path* with status ``pending``
so it will be picked up by the next available worker.

# @trace WL-038

**Parameters**:

- `deferred_tasks`: Task texts extracted by :func:`extract_deferred_tasks`.
- `queue_path`:     Path to the ``prompt_queue.jsonl`` file.
- `project`:        Project identifier to associate with each entry.
- `agent`:          Optional preferred agent name for the deferred tasks.

**Returns**: Number of tasks successfully appended.

---

## list_deferred

```python
list_deferred(self: Any)
```

List all currently deferred tasks.

---

## process_output_for_deferrals

```python
process_output_for_deferrals(output: str, queue_path: Path, project: str, agent: Any)
```

Extract ``$defer`` directives from *output* and inject into the queue.

Convenience wrapper that combines :func:`extract_deferred_tasks` and
:func:`inject_deferred_tasks`.

# @trace WL-038

**Parameters**:

- `output`:     Combined agent output (stdout + stderr).
- `queue_path`: Path to the ``prompt_queue.jsonl`` file.
- `project`:    Project identifier for queue entries.
- `agent`:      Optional preferred agent name.

**Returns**: List of deferred task texts that were injected.

---

## should_defer

```python
should_defer(self: Any, task_priority: str, load_level: float)
```

Determine if a task should be deferred.

Priority: P0 (critical) to P3 (low).

---

