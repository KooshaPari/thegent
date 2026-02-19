# slo_regulator API Reference

> **Source**: `src/thegent/planning/slo_regulator.py`

WP-11001: SLO regulator loop controller.

Provides stable control updates with anti-oscillation guarantees for system SLOs.

---

## SLORegulator

Closed-loop controller for regulating system performance against SLOs.

### Methods

#### SLORegulator.__init__

```python
__init__(self, target_latency_ms)
```

#### SLORegulator.evaluate_and_adjust

Evaluate SLO performance and adjust throttle if needed.

```python
evaluate_and_adjust(self, current_latency_ms)
```

---

## evaluate_and_adjust

Evaluate SLO performance and adjust throttle if needed.

```python
evaluate_and_adjust(self, current_latency_ms)
```

---

