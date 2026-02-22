# unified_registry_cli API Reference

> **Source**: `src/thegent/agents/unified_registry_cli.py`

CLI commands for Unified Agent Registry.

---

## assign_project

```python
assign_project(agent_id: str, project_id: str, role: str)
```

Assign agent to a project.

---

## discover

```python
discover(description: str, capabilities: List[AgentCapability], project: Optional[str])
```

Discover best agent for a task.

---

## get_agent

```python
get_agent(agent_id: str)
```

Show details for a specific agent.

---

## list_agents

```python
list_agents(status: Optional[AgentStatus], project: Optional[str], capability: Optional[AgentCapability])
```

List all agents in the registry.

---

## register_agent

```python
register_agent(agent_id: str, name: str, capabilities: List[AgentCapability])
```

Register a new agent.

---
