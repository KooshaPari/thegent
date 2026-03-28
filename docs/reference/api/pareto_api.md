# pareto API Reference

> **Source**: `src/thegent/utils/routing_impl/pareto.py`

Public dict-based ParetoRouter shim.

Wraps the internal RouteCandidate-based ParetoRouter from pareto_router.py
with a simple dict API suitable for property-based testing and external callers.

Provider dict schema::

    {
        "model":       str,    # model identifier (must be unique per list)
        "cost":        float,  # cost per call (>= 0)
        "latency_ms":  int,    # expected latency in milliseconds
        "quality":     float,  # quality score in [0, 1]
    }

---

## ParetoRouter

Select Pareto-optimal provider from a list of provider dicts.

### Methods

#### ParetoRouter.__init__

```python
__init__(self: Any, providers: list[dict])
```

---

#### ParetoRouter.select

```python
select(self: Any, max_cost_per_call: float)
```

Return the Pareto-optimal provider dict, or None if no candidates pass constraints.

A provider is feasible when its ``cost`` <= *max_cost_per_call*.
Among feasible providers the non-dominated set (Pareto frontier on
cost and quality) is computed, then the candidate with the highest
quality/cost ratio is returned (highest quality when cost == 0).

Duplicate model names are deduplicated: the first occurrence is used.

**Parameters**:

- `max_cost_per_call`: Hard cost ceiling; providers above this are excluded.

**Returns**: The selected provider dict, or None when no provider passes the
cost constraint.

---

---

## select

```python
select(self: Any, max_cost_per_call: float)
```

Return the Pareto-optimal provider dict, or None if no candidates pass constraints.

A provider is feasible when its ``cost`` <= *max_cost_per_call*.
Among feasible providers the non-dominated set (Pareto frontier on
cost and quality) is computed, then the candidate with the highest
quality/cost ratio is returned (highest quality when cost == 0).

Duplicate model names are deduplicated: the first occurrence is used.

**Parameters**:

- `max_cost_per_call`: Hard cost ceiling; providers above this are excluded.

**Returns**: The selected provider dict, or None when no provider passes the
cost constraint.

---

