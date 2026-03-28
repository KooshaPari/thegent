# analyzer API Reference

> **Source**: `src/thegent/governance/analyzer.py`

Finding prioritisation and ranking for governance scans.

Takes a ScanResult produced by scanner.py and produces a severity-ranked
list of Finding objects that downstream components (backlog, remediation
planner) consume.

---

## Finding

A single actionable finding produced by the analyser.

**Inherits from**: `BaseModel`

---

## HealthAnalyzer

Converts raw scan results into a prioritised list of findings.

### Methods

#### HealthAnalyzer.__init__

```python
__init__(self: Any, health_targets_path: Path)
```

---

#### HealthAnalyzer.analyze

```python
analyze(self: Any, scan_result: ScanResult, backlog_items: Any)
```

Produce a ranked list of findings from *scan_result*.

Green dimensions (at or exceeding target) are excluded.

**Parameters**:

- `scan_result`: output of CodebaseScanner.scan_all().
- `backlog_items`: optional list of previous backlog entries used to
boost priority of repeatedly-attempted dimensions.  Each
entry is expected to carry a ``dimension`` key.

**Returns**: Findings sorted descending by priority (highest first).

---

---

## analyze

```python
analyze(self: Any, scan_result: ScanResult, backlog_items: Any)
```

Produce a ranked list of findings from *scan_result*.

Green dimensions (at or exceeding target) are excluded.

**Parameters**:

- `scan_result`: output of CodebaseScanner.scan_all().
- `backlog_items`: optional list of previous backlog entries used to
boost priority of repeatedly-attempted dimensions.  Each
entry is expected to carry a ``dimension`` key.

**Returns**: Findings sorted descending by priority (highest first).

---

