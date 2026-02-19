# drift API Reference

> **Source**: `src/thegent/governance/drift.py`

WP-3005: Policy drift detection and sweep.

---

## DriftDetector

Detects drift in policy state and cleans up stale overrides.

### Methods

#### DriftDetector.__init__

```python
__init__(self, settings)
```

#### DriftDetector.detect_drift

Check for drift between current state and baseline.
Returns a report of detected issues.

```python
detect_drift(self)
```

#### DriftDetector.sweep

Perform a sweep to correct detected drift.
Returns counts of corrected items.

```python
sweep(self)
```

---

## detect_drift

Check for drift between current state and baseline.
Returns a report of detected issues.

```python
detect_drift(self)
```

---

## sweep

Perform a sweep to correct detected drift.
Returns counts of corrected items.

```python
sweep(self)
```

---

