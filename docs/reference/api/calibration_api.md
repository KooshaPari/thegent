# calibration API Reference

> **Source**: `src/thegent/ux/calibration.py`

WP-4008: Feedback loops and confidence calibration.

---

## ConfidenceCalibrator

Calibrates agent confidence scores based on operator feedback.

### Methods

#### ConfidenceCalibrator.__init__

```python
__init__(self, settings)
```

#### ConfidenceCalibrator.calibrate

Apply calibration bias to a raw confidence score.

```python
calibrate(self, agent_name, raw_confidence)
```

#### ConfidenceCalibrator.record_feedback

Record feedback to update bias map.

```python
record_feedback(self, agent_name, provided_confidence, actual_success)
```

---

## calibrate

Apply calibration bias to a raw confidence score.

```python
calibrate(self, agent_name, raw_confidence)
```

---

## record_feedback

Record feedback to update bias map.

```python
record_feedback(self, agent_name, provided_confidence, actual_success)
```

---

