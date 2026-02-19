# simulation API Reference

> **Source**: `src/thegent/planning/simulation.py`

Planning simulation overlays: PERT, resource contention, continuity risk (G-CA-04).

Design: docs/PLANNING_SIMULATION_DESIGN.md

---

## BudgetGuard

WP-8007: Adaptive routing budget guard based on predictive load.

### Methods

#### BudgetGuard.__init__

```python
__init__(self, daily_budget_usd)
```

#### BudgetGuard.should_throttle

Determine if we should throttle non-critical tasks.

```python
should_throttle(self, current_spend, predicted_load_pct)
```

---

## ContentionResult

Resource contention analysis result.

---

## ContinuityRiskInput

Input for continuity risk scoring.

---

## ContinuityRiskResult

Continuity risk score and factors.

---

## ForecastAuditor

WP-8010/11002: Audit and calibration of hardened duration forecasts.

### Methods

#### ForecastAuditor.__init__

```python
__init__(self)
```

#### ForecastAuditor.check_drift

WP-11002: Check if forecast quality has drifted beyond threshold over 14 days (simplified).

```python
check_drift(self, threshold)
```

#### ForecastAuditor.get_bias

Calculate prediction bias (p - a). Positive means over-optimistic/long?

```python
get_bias(self)
```

#### ForecastAuditor.get_calibration_error

Calculate Mean Absolute Percentage Error (MAPE).

```python
get_calibration_error(self)
```

#### ForecastAuditor.record_actual

Record a data point for calibration and quality tracking.

```python
record_actual(self, predicted, actual, task_id)
```

---

## InterventionPolicy

WP-8009: Governance for semi-automated intervention decisions.

### Methods

#### InterventionPolicy.evaluate_intervention

Return the required oversight level for an intervention.

```python
evaluate_intervention(self, risk_score, confidence)
```

---

## PERTNode

Task node for PERT analysis.

---

## PERTResult

PERT analysis result per task.

---

## ResourceProfile

Resource capacity definition.

---

## RunbookAuthor

WP-8008: Simulation-backed runbook generation.

---

## TaskResourceDemand

Task demand for a resource.

---

## analyze_bottlenecks

WP-8003: Identify top bottlenecks and tasks with no slack.

```python
analyze_bottlenecks(nodes, mc_stats)
```

---

## check_drift

WP-11002: Check if forecast quality has drifted beyond threshold over 14 days (simplified).

```python
check_drift(self, threshold)
```

---

## continuity_risk_predictor

WP-11007: Predicts continuity risk before predicted shift or stall events.

```python
continuity_risk_predictor(registry)
```

---

## evaluate_intervention

Return the required oversight level for an intervention.

```python
evaluate_intervention(self, risk_score, confidence)
```

---

## extract_plan_graph

WP-8001: Extract PERT nodes from a DagDocument.

```python
extract_plan_graph(dag)
```

---

## get_bias

Calculate prediction bias (p - a). Positive means over-optimistic/long?

```python
get_bias(self)
```

---

## get_calibration_error

Calculate Mean Absolute Percentage Error (MAPE).

```python
get_calibration_error(self)
```

---

## pert_forward_pass

Compute expected duration, variance, critical path (D1 stub).

```python
pert_forward_pass(nodes)
```

---

## record_actual

Record a data point for calibration and quality tracking.

```python
record_actual(self, predicted, actual, task_id)
```

---

## score_continuity_risk

Compute continuity risk for shift handoff (D3 stub).

```python
score_continuity_risk(input)
```

---

## should_throttle

Determine if we should throttle non-critical tasks.

```python
should_throttle(self, current_spend, predicted_load_pct)
```

---

## simulate_monte_carlo

WP-8002: Monte Carlo simulation for task durations using triangular distribution.

```python
simulate_monte_carlo(nodes, iterations)
```

---

## simulate_resource_contention

Identify resource contention windows (D2 stub).

```python
simulate_resource_contention(tasks, resources, _)
```

---

## suggest_reschedules

WP-8004: Recommendations for rescheduling or resource reallocation.

```python
suggest_reschedules(bottlenecks)
```

---

## surge_watcher

WP-8006: Monitor surge in runs and recommend safe-mode.

```python
surge_watcher(recent_runs, threshold)
```

---

