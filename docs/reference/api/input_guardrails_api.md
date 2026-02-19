# input_guardrails API Reference

> **Source**: `src/thegent/governance/input_guardrails.py`

Input guardrails (NeMo-style) before policy checks. G-GP-02.

Validates prompt, agent, model, cwd before PolicyEngine.
See docs/governance/NEMO_GUARDRAILS_DESIGN.md.

---

## GuardrailResult

Result of input guardrail check.

---

## InputGuardrails

Input validation rails before OPA/PolicyEngine. G-GP-02.

### Methods

#### InputGuardrails.check

Validate inputs. Returns passed=True if all rails pass.

```python
check(self, prompt, agent, model, cwd)
```

---

## check

Validate inputs. Returns passed=True if all rails pass.

```python
check(self, prompt, agent, model, cwd)
```

---

