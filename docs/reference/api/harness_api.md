# harness API Reference

> **Source**: `src/thegent/planning/harness.py`

WP-14005: Policy-safe exploration harness for candidate policy variants.

---

## ExplorationResult

---

## PolicyExplorationHarness

Harness for controlled simulation of candidate policy variants (WP-14005).

### Methods

#### PolicyExplorationHarness.__init__

```python
__init__(self, simulation_engine)
```

#### PolicyExplorationHarness.explore_variant

Run simulation across a set of historical runs for a policy variant.

```python
explore_variant(self, variant_id, base_run_ids)
```

---

## explore_variant

Run simulation across a set of historical runs for a policy variant.

```python
explore_variant(self, variant_id, base_run_ids)
```

---

