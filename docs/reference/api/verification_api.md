# verification API Reference

> **Source**: `src/thegent/agents/verification.py`

WP-16001: Multi-Step CoT Verification.
Chain-of-Thought (CoT) verification before agent execution.

---

## CoTVerifier

Verifies multi-step agent reasoning chains before final execution.

### Methods

#### CoTVerifier.__init__

```python
__init__(self, run_id)
```

#### CoTVerifier.get_summary

Summarize all verification results.

```python
get_summary(self)
```

#### CoTVerifier.verify_step

Verify a single reasoning step against its intended prompt.

```python
verify_step(self, step_id, prompt, reasoning)
```

---

## VerificationResult

Result of a CoT step verification.

**Inherits from**: `BaseModel`

---

## get_summary

Summarize all verification results.

```python
get_summary(self)
```

---

## verify_step

Verify a single reasoning step against its intended prompt.

```python
verify_step(self, step_id, prompt, reasoning)
```

---

