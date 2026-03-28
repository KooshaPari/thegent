# router API Reference

> **Source**: `src/thegent/agents/crew/router.py`

RouterManager with multi-runtime optimized backends.

---

## RouterManager

Unified routing interface that selects the best backend (Rust vs Pure Python).

### Methods

#### RouterManager.__init__

```python
__init__(self: Any, strategy: RoutingStrategy)
```

---

#### RouterManager.backend

```python
backend(self: Any)
```

---

#### RouterManager.refresh_from_mesh

```python
refresh_from_mesh(self: Any, mesh_root: Any)
```

Sync local routing metrics with the global IPC mesh.

---

#### RouterManager.select_agent

```python
select_agent(self: Any, task_description: str, available_agents: list)
```

---

#### RouterManager.update_agent_metrics

```python
update_agent_metrics(self: Any, agent_id: str, metrics: RouteMetrics)
```

---

---

## backend

```python
backend(self: Any) -> str
```

---

## refresh_from_mesh

```python
refresh_from_mesh(self: Any, mesh_root: Any)
```

Sync local routing metrics with the global IPC mesh.

---

## select_agent

```python
select_agent(self: Any, task_description: str, available_agents: list) -> Any
```

---

## update_agent_metrics

```python
update_agent_metrics(self: Any, agent_id: str, metrics: RouteMetrics) -> None
```

---

