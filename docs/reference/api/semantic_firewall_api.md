# semantic_firewall API Reference

> **Source**: `src/thegent/governance/semantic_firewall.py`

WP-28002: Semantic Firewall for Model Output.
Analyzes model outputs for semantic violations, alignment drift, and forbidden patterns.
Sits between the model and the final execution environment.

---

## FirewallRule

Definition of a semantic firewall rule.

**Inherits from**: `BaseModel`

---

## SemanticFirewall

Protects the agent environment from unsafe model outputs.

### Methods

#### SemanticFirewall.__init__

```python
__init__(self)
```

#### SemanticFirewall.inspect_output

Inspect model output and apply firewall rules.

```python
inspect_output(self, output)
```

---

## inspect_output

Inspect model output and apply firewall rules.

```python
inspect_output(self, output)
```

---

