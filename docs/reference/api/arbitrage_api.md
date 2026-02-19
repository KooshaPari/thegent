# arbitrage API Reference

> **Source**: `src/thegent/economy/arbitrage.py`

WP-35001: Global Compute Arbitrage Engine.
Optimizes task execution cost by finding the cheapest available agent service globally.

---

## ArbitrageEngine

Finds and exploits price differences across regional agent markets.

### Methods

#### ArbitrageEngine.__init__

```python
__init__(self, market)
```

#### ArbitrageEngine.estimate_global_savings

Estimate total savings using arbitrage over standard fixed routing.

```python
estimate_global_savings(self, run_count)
```

#### ArbitrageEngine.find_best_value

WP-35001: Run an arbitrage cycle to find the highest value provider.

```python
find_best_value(self, task_id, capabilities, max_budget)
```

---

## estimate_global_savings

Estimate total savings using arbitrage over standard fixed routing.

```python
estimate_global_savings(self, run_count)
```

---

## find_best_value

WP-35001: Run an arbitrage cycle to find the highest value provider.

```python
find_best_value(self, task_id, capabilities, max_budget)
```

---

