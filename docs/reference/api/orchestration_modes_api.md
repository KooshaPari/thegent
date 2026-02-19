# orchestration_modes API Reference

> **Source**: `src/thegent/orchestration_modes.py`

Multi-agent orchestration mode catalog (G-KD-04).

Formalizes orchestration patterns per Kush docs D-D and Kagentop MultiAgentOrchestration.
Mode selection policy tied to risk, urgency, and confidence.

---

## ConflictArbitrator

WP-1006: Arbitration rules and quorum policy for multi-agent consensus.

### Methods

#### ConflictArbitrator.__init__

```python
__init__(self, quorum_threshold)
```

#### ConflictArbitrator.arbitrate

Arbitrate between conflicting results using quorum policy.

```python
arbitrate(self, results)
```

#### ConflictArbitrator.detect_conflicts

Detect conflicts between multiple agent outputs.

```python
detect_conflicts(self, results)
```

---

## ModeEntry

Catalog entry for a multi-agent mode.

---

## MultiAgentMode

Canonical multi-agent orchestration modes.

**Inherits from**: `StrEnum`

---

## arbitrate

Arbitrate between conflicting results using quorum policy.

```python
arbitrate(self, results)
```

---

## calculate_risk_score

WP-2008: Calculate risk score for a task to trigger oversight.

```python
calculate_risk_score(prompt, lane)
```

---

## detect_conflicts

Detect conflicts between multiple agent outputs.

```python
detect_conflicts(self, results)
```

---

## get_mode

Return mode entry by id, or None if not found.

```python
get_mode(mode_id)
```

---

## list_modes

Return all modes for CLI/MCP discovery.

---

## suggest_mode

Suggest mode based on risk, urgency, and confidence (mode selection policy).

```python
suggest_mode(risk, urgency, confidence)
```

---

