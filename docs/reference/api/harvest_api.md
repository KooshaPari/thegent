# harvest API Reference

> **Source**: `src/thegent/utils/routing_impl/harvest.py`

WP-7002: LiteLLM cost/latency data harvesting implementation.

---

## harvest_routing_metrics

```python
harvest_routing_metrics(session_id: str, output_path: Any)
```

Harvest cost and latency data for a session and save to output_path.

**Parameters**:

- `session_id`: The session ID to harvest for.
- `output_path`: Optional path to save JSON metrics.

**Returns**: Dictionary of harvested metrics.

---

