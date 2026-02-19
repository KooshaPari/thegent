# drift_corrector API Reference

> **Source**: `src/thegent/infra/drift_corrector.py`

WP-31003: Infra Drift Self-Correction Loop.
Monitors provisioned resources and automatically corrects deviations from the target spec.
Ensures agent infrastructure remains stable and compliant over time.

---

## DriftCorrector

Orchestrates self-correction of agent infrastructure drift.

### Methods

#### DriftCorrector.__init__

```python
__init__(self, provisioner)
```

#### DriftCorrector.check_drift

Check if a resource has drifted from its target specification.

```python
check_drift(self, resource_id, target_spec)
```

#### DriftCorrector.correct_drift

Automatically correct detected infrastructure drift.

```python
correct_drift(self, resource_id, target_spec)
```

---

## check_drift

Check if a resource has drifted from its target specification.

```python
check_drift(self, resource_id, target_spec)
```

---

## correct_drift

Automatically correct detected infrastructure drift.

```python
correct_drift(self, resource_id, target_spec)
```

---

