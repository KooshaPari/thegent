# resources_system API Reference

> **Source**: `src/thegent/mcp/server/resources_system.py`

System/metadata resource handlers for MCP server.

---

## register_system_resources

---

## resource_meta

Server metadata: version, capabilities, health payload schema.

---

## resource_meta_impl

---

## resource_modes

```python
resource_modes(mode: Any)
```

Multi-agent orchestration modes: sequential_delegation, parallel_consensus, review_loop.

---

## resource_modes_impl

```python
resource_modes_impl(mode: Any) -> str
```

---

## resource_observe_summary

```python
resource_observe_summary(limit: int, drift_window: int, structural_budget_pct: float, semantic_budget_pct: float, provider: Any, trend_samples: int, top_escalations: int)
```

Observe summary payload for contract KPIs, drift status, and escalation backlog.

---

## resource_observe_summary_impl

---

## resource_operations

```python
resource_operations(operation: Any)
```

Universal operation taxonomy: orchestrate, govern, recover, observe, plan.

---

## resource_operations_impl

```python
resource_operations_impl(operation: Any) -> str
```

---

