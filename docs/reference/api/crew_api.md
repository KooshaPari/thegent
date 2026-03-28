# crew API Reference

> **Source**: `src/thegent/agents/crew/crew.py`

Crew data model - orchestrates agents and tasks.

---

## Crew

Orchestrates agents and tasks for complex problem solving.

A crew manages a collection of agents and their tasks, coordinating
their execution to achieve a goal.

### Methods

#### Crew.add_agent

```python
add_agent(self: Any, agent: Any)
```

Add agent to crew.

---

#### Crew.add_task

```python
add_task(self: Any, task: Any)
```

Add task to crew.

---

#### Crew.get_agent_by_id

```python
get_agent_by_id(self: Any, agent_id: str)
```

Get agent by ID.

---

#### Crew.get_task_by_id

```python
get_task_by_id(self: Any, task_id: str)
```

Get task by ID.

---

---

## ExecutionMode

Crew execution modes.

**Inherits from**: `StrEnum`

---

## add_agent

```python
add_agent(self: Any, agent: Any)
```

Add agent to crew.

---

## add_task

```python
add_task(self: Any, task: Any)
```

Add task to crew.

---

## get_agent_by_id

```python
get_agent_by_id(self: Any, agent_id: str)
```

Get agent by ID.

---

## get_task_by_id

```python
get_task_by_id(self: Any, task_id: str)
```

Get task by ID.

---

