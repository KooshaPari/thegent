# speculative_strategies API Reference

> **Source**: `src/thegent/orchestration/speculative_strategies.py`

Speculative execution strategies for resource optimization.

WP-5001: Multi-provider racing, adaptive timeouts, cost-quality tradeoffs.

---

## SpeculativeConfig

Configuration for speculative execution.

### Methods

---

## SpeculativeStrategy

Speculative execution strategies.

**Inherits from**: `Enum`

---

## compute_adaptive_timeout

```python
compute_adaptive_timeout(historical_p95_ms: float, base_timeout_ms: int, safety_multiplier: float)
```

Compute adaptive timeout based on historical performance.

---

## select_speculative_providers

```python
select_speculative_providers(available_providers: list[str], strategy: SpeculativeStrategy, cost_budget: float)
```

Select providers for speculative execution based on strategy.

---

## should_terminate_early

```python
should_terminate_early(elapsed_ms: float, timeout_ms: int, other_results: list[Any], strategy: SpeculativeStrategy)
```

Determine if a speculative execution should terminate early.

---
