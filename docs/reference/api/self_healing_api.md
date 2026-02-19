# self_healing API Reference

> **Source**: `src/thegent/agents/self_healing.py`

WP-2004: Automated recovery and self-healing orchestration.

---

## RecoveryRouter

Routes failed runs to automated recovery playbooks.

### Methods

#### RecoveryRouter.__init__

```python
__init__(self)
```

#### RecoveryRouter.attempt_recovery

Suggest a recovery action based on the failure classification.

```python
attempt_recovery(self, result)
```

#### RecoveryRouter.back_project_failure

WP-16002: Analyze failure and project fix into instructions.

```python
back_project_failure(self, run_id, prompt, failure_type)
```

---

## StabilityTracker

Monitors session stability and performance over time.

### Methods

#### StabilityTracker.__init__

```python
__init__(self, window_size)
```

#### StabilityTracker.get_stability_score

Calculate stability score (0.0 - 1.0) based on success rate.

```python
get_stability_score(self)
```

#### StabilityTracker.record_result

Record a run result and prune old history.

```python
record_result(self, result)
```

---

## attempt_recovery

Suggest a recovery action based on the failure classification.

```python
attempt_recovery(self, result)
```

---

## back_project_failure

WP-16002: Analyze failure and project fix into instructions.

```python
back_project_failure(self, run_id, prompt, failure_type)
```

---

## get_stability_score

Calculate stability score (0.0 - 1.0) based on success rate.

```python
get_stability_score(self)
```

---

## record_result

Record a run result and prune old history.

```python
record_result(self, result)
```

---

