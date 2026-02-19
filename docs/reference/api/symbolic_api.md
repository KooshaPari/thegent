# symbolic API Reference

> **Source**: `src/thegent/verification/symbolic.py`

WP-18002: Symbolic Execution for Risk Assessment.
Uses symbolic execution principles to explore possible execution paths and identify high-risk branches.

---

## RiskPath

A specific execution path with its associated risk score.

---

## SymbolicRiskExplorer

Symbolically explores task dependency graphs to identify potential failures.

### Methods

#### SymbolicRiskExplorer.__init__

```python
__init__(self, dag)
```

#### SymbolicRiskExplorer.explore

Explore all reachable paths from start_node and calculate risk.

```python
explore(self, start_node)
```

#### SymbolicRiskExplorer.get_highest_risk_path

Return the path with the highest risk score.

```python
get_highest_risk_path(self)
```

---

## explore

Explore all reachable paths from start_node and calculate risk.

```python
explore(self, start_node)
```

---

## get_highest_risk_path

Return the path with the highest risk score.

```python
get_highest_risk_path(self)
```

---

