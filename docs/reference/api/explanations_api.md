# explanations API Reference

> **Source**: `src/thegent/ux/explanations.py`

WP-4002: Concise and detailed explanation tiers.

---

## ExplanationGenerator

Generates explanations for agent decisions at different levels of detail.

### Methods

#### ExplanationGenerator.__init__

```python
__init__(self, settings)
```

#### ExplanationGenerator.generate_explanation

Generate an explanation based on data and requested tier.

```python
generate_explanation(self, data, tier)
```

---

## ExplanationTier

Tier of explanation detail.

**Inherits from**: `str`

---

## generate_explanation

Generate an explanation based on data and requested tier.

```python
generate_explanation(self, data, tier)
```

---

