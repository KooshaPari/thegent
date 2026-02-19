# moral_ui API Reference

> **Source**: `src/thegent/ux/moral_ui.py`

WP-29003: Human-in-the-Loop Moral Arbitration.
Provides a UI interface for humans to resolve moral dilemmas encountered by agents.

---

## ArbitrationResult

The result of human moral arbitration.

**Inherits from**: `BaseModel`

---

## MoralDilemma

Represents a moral conflict that needs arbitration.

**Inherits from**: `BaseModel`

---

## MoralUI

Manages the UI flow for moral arbitration.

### Methods

#### MoralUI.__init__

```python
__init__(self)
```

#### MoralUI.present_dilemma

Register a dilemma for human review.

```python
present_dilemma(self, dilemma)
```

#### MoralUI.resolve_dilemma

Apply the human decision to a pending dilemma.

```python
resolve_dilemma(self, result)
```

---

## present_dilemma

Register a dilemma for human review.

```python
present_dilemma(self, dilemma)
```

---

## resolve_dilemma

Apply the human decision to a pending dilemma.

```python
resolve_dilemma(self, result)
```

---

