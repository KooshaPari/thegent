# explainability API Reference

> **Source**: `src/thegent/observability/explainability.py`

WP-9002: Explainability stack (summary/detail/trace).

Provides a structured way to generate and present explanations for agent decisions
at three levels of detail.

---

## DetailLevel

**Inherits from**: `StrEnum`

---

## ExplainabilityEngine

Stack for managing and rendering progressive disclosure explanations.

### Methods

#### ExplainabilityEngine.__init__

```python
__init__(self)
```

#### ExplainabilityEngine.get_explanation

Return the explanation string for the requested level.

```python
get_explanation(self, decision_id, level)
```

#### ExplainabilityEngine.record_decision

Register an explanation for a specific decision.

```python
record_decision(self, decision_id, explanation)
```

#### ExplainabilityEngine.render_all

Render a progressive disclosure view of the explanation.

```python
render_all(self, decision_id)
```

---

## Explanation

A single decision explanation at multiple levels.

---

## get_explanation

Return the explanation string for the requested level.

```python
get_explanation(self, decision_id, level)
```

---

## record_decision

Register an explanation for a specific decision.

```python
record_decision(self, decision_id, explanation)
```

---

## render_all

Render a progressive disclosure view of the explanation.

```python
render_all(self, decision_id)
```

---

