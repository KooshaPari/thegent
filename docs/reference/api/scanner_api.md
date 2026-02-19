# scanner API Reference

> **Source**: `src/thegent/governance/scanner.py`

Codebase scanner producing structured dimension measurements.

Python port of hooks/gardener-scan.sh.  Runs 8 scan dimensions
(test coverage, lint violations, doc organisation, fragmented research,
missing specs, technical debt, stale items, agent failure) and returns
pydantic models consumable by the health-score computer.

---

## CodebaseScanner

Scans the codebase across 8 governance dimensions.

### Methods

#### CodebaseScanner.__init__

```python
__init__(self, project_dir, session_dir)
```

#### CodebaseScanner.scan_all

Run every dimension scan and return the aggregated result.

```python
scan_all(self)
```

#### CodebaseScanner.scan_dimension

Run a single dimension scan by name.

```python
scan_dimension(self, dimension)
```

---

## DimensionScan

Result of a single scan dimension.

**Inherits from**: `BaseModel`

---

## ScanResult

Aggregated result of all dimension scans.

**Inherits from**: `BaseModel`

---

## scan_all

Run every dimension scan and return the aggregated result.

```python
scan_all(self)
```

---

## scan_dimension

Run a single dimension scan by name.

```python
scan_dimension(self, dimension)
```

---

