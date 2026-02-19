# constitution API Reference

> **Source**: `src/thegent/governance/constitution.py`

Constitutional AI and alignment enforcement for thegent (WP-3001).

---

## ConstitutionManager

WP-3001: Manages project principles and critique logic.

### Methods

#### ConstitutionManager.__init__

```python
__init__(self, constitution_path)
```

#### ConstitutionManager.critique_action

WP-3001: Pre-execution critique of a proposed agent action.

```python
critique_action(self, action)
```

#### ConstitutionManager.generate_poa

Generate a Proof of Alignment for a MAIF artifact.

```python
generate_poa(self, action_id, aligned)
```

---

## ConstitutionalViolation

**Inherits from**: `BaseModel`

---

## ProofOfAlignment

Verifiable proof that an action aligns with the constitution.

**Inherits from**: `BaseModel`

---

## critique_action

WP-3001: Pre-execution critique of a proposed agent action.

```python
critique_action(self, action)
```

---

## generate_poa

Generate a Proof of Alignment for a MAIF artifact.

```python
generate_poa(self, action_id, aligned)
```

---

