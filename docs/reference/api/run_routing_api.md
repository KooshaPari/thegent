# run_routing API Reference

> **Source**: `src/thegent/cli/services/run_routing.py`

Routing helpers for run execution.

Extracted from run_execution_core_helpers.py for maintainability.

---

## build_route_candidates

```python
build_route_candidates(model: Any, provider: Any, agent: Any, settings: ThegentSettings)
```

Build list of route candidates for Pareto routing.

**Parameters**:

- `model`: Requested model
- `provider`: Requested provider
- `agent`: Requested agent
- `settings`: Thegent settings

**Returns**: List of route candidate dicts

---

## classify_auto_route

```python
classify_auto_route(prompt: str, model: Any, agent: Any)
```

Classify and select route for auto-routing.

**Parameters**:

- `prompt`: User prompt
- `model`: Requested model
- `agent`: Requested agent

**Returns**: Tuple of (provider, model)

---

## select_pareto_route

```python
select_pareto_route(candidates: list[dict[(str, Any)]], quality_weight: float, cost_weight: float, latency_weight: float)
```

Select best route using Pareto optimization.

**Parameters**:

- `candidates`: List of route candidates
- `quality_weight`: Weight for quality score
- `cost_weight`: Weight for cost (inverse)
- `latency_weight`: Weight for latency (inverse)

**Returns**: Best candidate or None if no candidates

---

