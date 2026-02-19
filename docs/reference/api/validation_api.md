# validation API Reference

> **Source**: `src/thegent/contracts/validation.py`

Semantic Validation Layer for agent structured messages.

Enforces invariants and cross-tag logic for CanonicalStructuredMessage (CSM).

---

## InvariantViolation

Raised when a specific invariant is violated.

**Inherits from**: `SemanticValidationError`

---

## SemanticPolicyEngine

WP-7005: Policy layer for semantic validation of agent outputs.

### Methods

#### SemanticPolicyEngine.__init__

```python
__init__(self, strict)
```

#### SemanticPolicyEngine.add_rule

Register a custom validation rule.

```python
add_rule(self, rule)
```

#### SemanticPolicyEngine.evaluate

Evaluate CSM against all semantic rules.

Returns:
    Dict with 'allowed', 'issues', 'drift_detected'.

```python
evaluate(self, csm)
```

---

## SemanticValidationError

Raised when a CSM fails semantic validation.

**Inherits from**: `Exception`

---

## add_rule

Register a custom validation rule.

```python
add_rule(self, rule)
```

---

## ensure_valid_csm

Raise InvariantViolation if CSM is semantically invalid.

```python
ensure_valid_csm(csm)
```

---

## evaluate

Evaluate CSM against all semantic rules.

Returns:
    Dict with 'allowed', 'issues', 'drift_detected'.

```python
evaluate(self, csm)
```

---

## validate_csm

Perform semantic validation on a CSM.

Returns:
    List of validation issue strings. Empty if valid.

```python
validate_csm(csm)
```

---

