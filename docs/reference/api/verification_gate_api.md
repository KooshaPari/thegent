# verification_gate API Reference

> **Source**: `src/thegent/governance/verification_gate.py`

Post-agent verification gate for AgilePlus cycles.

Re-runs targeted scanner dimensions after each agent task completes to verify
improvement, detect regressions, and determine pass/fail verdicts.

---

## DimensionScanResult

Protocol for a single dimension's scan output.

**Inherits from**: `Protocol`

---

## HealthComputerProtocol

Protocol for HealthScoreComputer -- used to get dimension weights.

**Inherits from**: `Protocol`

### Methods

#### HealthComputerProtocol.compute

```python
compute(self, scan_result)
```

---

## RemediationTaskProtocol

Protocol for a remediation task from the planner.

**Inherits from**: `Protocol`

---

## ScanResultProtocol

Protocol for a full codebase scan result.

**Inherits from**: `Protocol`

### Methods

#### ScanResultProtocol.get_dimension

```python
get_dimension(self, dimension)
```

---

## ScannerProtocol

Protocol for CodebaseScanner -- only scan_dimension is needed here.

**Inherits from**: `Protocol`

### Methods

#### ScannerProtocol.scan

```python
scan(self)
```

#### ScannerProtocol.scan_dimension

```python
scan_dimension(self, dimension)
```

---

## TaskExecutionProtocol

Protocol for the result of executing a remediation task.

**Inherits from**: `Protocol`

---

## TaskVerification

Result of verifying a single task's effect on codebase health.

**Inherits from**: `BaseModel`

---

## VerificationGate

Verifies that agent tasks actually improved the targeted dimension.

After each task execution, re-scans the targeted dimension and compares
against the pre-scan baseline. Detects regressions in other dimensions.

### Methods

#### VerificationGate.__init__

```python
__init__(self, scanner, health_computer, max_rerolls)
```

#### VerificationGate.get_escalated_tier

Return the next agent tier for reroll escalation.

Returns None if already at the highest tier.

```python
get_escalated_tier(self, current_tier)
```

#### VerificationGate.should_reroll

Return True if the task should be retried based on attempt count.

```python
should_reroll(self, attempts)
```

#### VerificationGate.verify_task

Verify a completed task by re-scanning its target dimension.

Compares post-execution metrics against the pre-scan baseline to
determine whether the task improved, regressed, or had no effect.

```python
verify_task(self, task, execution, pre_scan)
```

---

## VerificationVerdict

Outcome of post-task verification.

**Inherits from**: `str, Enum`

---

## compute

```python
compute(self, scan_result)
```

---

## get_dimension

```python
get_dimension(self, dimension)
```

---

## get_escalated_tier

Return the next agent tier for reroll escalation.

Returns None if already at the highest tier.

```python
get_escalated_tier(self, current_tier)
```

---

## scan

```python
scan(self)
```

---

## scan_dimension

```python
scan_dimension(self, dimension)
```

---

## should_reroll

Return True if the task should be retried based on attempt count.

```python
should_reroll(self, attempts)
```

---

## verify_task

Verify a completed task by re-scanning its target dimension.

Compares post-execution metrics against the pre-scan baseline to
determine whether the task improved, regressed, or had no effect.

```python
verify_task(self, task, execution, pre_scan)
```

---

