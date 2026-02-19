# registry API Reference

> **Source**: `src/thegent/agents/registry.py`

Agent registry.

---

## get_fallback_agents

Return fallback agents when this provider hits usage limit. Excludes current agent.

```python
get_fallback_agents(agent_name)
```

---

## get_runner

Get runner for agent. Returns None for unknown.

```python
get_runner(agent_name)
```

---

## list_agent_names

List available agent names (canonical CLI names).

---

## list_droid_names

List available droid names from .md files (legacy; droids disabled).

```python
list_droid_names(droids_dir)
```

---

## resolve_agent

Resolve label/alias to canonical CLI name. E.g. 'cursor' -> 'cursor-agent'.

```python
resolve_agent(agent_name)
```

---

