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

```python
check(self: Any, prompt: str, agent: str, model: Any, cwd: Any)
```

Validate inputs. Returns passed=True if all rails pass.

---

---

## check

```python
check(self: Any, prompt: str, agent: str, model: Any, cwd: Any)
```

Validate inputs. Returns passed=True if all rails pass.

---

## guardrails_from_env

Deprecated: Use guardrails_from_settings() instead. Kept for backwards compatibility.

---

## guardrails_from_settings

```python
guardrails_from_settings(settings: Any)
```

Build InputGuardrails from ThegentSettings.

---

