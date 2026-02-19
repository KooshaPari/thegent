# synthesis API Reference

> **Source**: `src/thegent/agents/synthesis.py`

WP-27001: Neural-Symbolic Program Synthesis.
Combines LLM-based code generation with symbolic verification and formal methods.
Ensures synthesized programs are correct and safe by construction.

---

## ProgramSynthesizer

Orchestrates neural-symbolic program generation.

### Methods

#### ProgramSynthesizer.__init__

```python
__init__(self, run_id)
```

#### ProgramSynthesizer.synthesize

Synthesize a program from a prompt and optional formal spec.

```python
synthesize(self, prompt, formal_spec)
```

---

## SynthesisResult

Result of a neural-symbolic synthesis operation.

**Inherits from**: `BaseModel`

---

## synthesize

Synthesize a program from a prompt and optional formal spec.

```python
synthesize(self, prompt, formal_spec)
```

---

