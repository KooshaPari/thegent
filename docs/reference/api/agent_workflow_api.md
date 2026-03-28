# agent_workflow API Reference

> **Source**: `src/thegent/docgen/agent_workflow.py`

Agent workflow for auto-populating documentation.

---

## AgentWorkflow

Workflow for agents to auto-populate documentation.

### Methods

#### AgentWorkflow.__init__

```python
__init__(self: Any)
```

Initialize agent workflow.

---

#### AgentWorkflow.create_docgen_workflow

```python
create_docgen_workflow(self: Any)
```

Create a standard documentation generation workflow.

**Returns**: Configured workflow

---

#### AgentWorkflow.execute

```python
execute(self: Any, context: dict[(str, Any)])
```

Execute the workflow.

**Parameters**:

- `context`: Execution context

**Returns**: Execution results

---

#### AgentWorkflow.register_step

```python
register_step(self: Any, name: str, func: Callable[(Ellipsis, Any)], dependencies: Any)
```

Register a workflow step.

**Parameters**:

- `name`: Step name
- `func`: Step function
- `dependencies`: List of step names this depends on

---

---

## create_docgen_workflow

```python
create_docgen_workflow(self: Any)
```

Create a standard documentation generation workflow.

**Returns**: Configured workflow

---

## execute

```python
execute(self: Any, context: dict[(str, Any)])
```

Execute the workflow.

**Parameters**:

- `context`: Execution context

**Returns**: Execution results

---

## register_step

```python
register_step(self: Any, name: str, func: Callable[(Ellipsis, Any)], dependencies: Any)
```

Register a workflow step.

**Parameters**:

- `name`: Step name
- `func`: Step function
- `dependencies`: List of step names this depends on

---

