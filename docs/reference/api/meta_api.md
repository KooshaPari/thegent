# meta API Reference

> **Source**: `src/thegent/governance/meta.py`

WP-20004: Meta-Governance & Constitutional AI.
Provides high-level, human-aligned rules (constitution) for all agent operations.
Inspired by Constitutional AI principles (Anthropic).

---

## ConstitutionalPrinciple

**Inherits from**: `str, Enum`

---

## MetaGovernance

Manages the agent constitution and high-level governance rules.

### Methods

#### MetaGovernance.__init__

```python
__init__(self, constitution_path)
```

#### MetaGovernance.get_constitution_summary

Return a formatted summary of the agent constitution.

```python
get_constitution_summary(self)
```

#### MetaGovernance.save_constitution

Save the constitution to disk.

```python
save_constitution(self)
```

#### MetaGovernance.validate_action

Validate an agent's intended action against the constitution.

```python
validate_action(self, action_description, tags)
```

---

## Rule

A high-level governance rule aligned with a constitutional principle.

---

## get_constitution_summary

Return a formatted summary of the agent constitution.

```python
get_constitution_summary(self)
```

---

## save_constitution

Save the constitution to disk.

```python
save_constitution(self)
```

---

## validate_action

Validate an agent's intended action against the constitution.

```python
validate_action(self, action_description, tags)
```

---

