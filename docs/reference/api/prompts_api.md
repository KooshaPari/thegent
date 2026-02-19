# prompts API Reference

> **Source**: `src/thegent/orchestration/prompts.py`

WP-Y5: Hierarchical prompt orchestration.

---

## PromptOrchestrator

Manages hierarchical decomposition of prompts and multi-agent routing.

### Methods

#### PromptOrchestrator.__init__

```python
__init__(self, settings)
```

#### PromptOrchestrator.decompose

Decompose a high-level goal into a sequence of sub-tasks.
In a real system, this would call an LLM (Decomposer Agent).
For now, we use a simple rule-based approach for demonstration.

```python
decompose(self, goal)
```

#### PromptOrchestrator.route_subtasks

Assign appropriate agents to sub-tasks based on content.

```python
route_subtasks(self, sub_tasks)
```

---

## decompose

Decompose a high-level goal into a sequence of sub-tasks.
In a real system, this would call an LLM (Decomposer Agent).
For now, we use a simple rule-based approach for demonstration.

```python
decompose(self, goal)
```

---

## route_subtasks

Assign appropriate agents to sub-tasks based on content.

```python
route_subtasks(self, sub_tasks)
```

---

