# synthesis API Reference

> **Source**: `src/thegent/agents/synthesis.py`

WP-27001: Neural-Symbolic Program Synthesis.

Combines LLM-based code generation with symbolic verification and formal methods.
Ensures synthesized programs are correct and safe by construction.

---

## CodeGenerationProvider

Provider contract used by ProgramSynthesizer.

**Inherits from**: `Protocol`

### Methods

#### CodeGenerationProvider.generate_code

```python
generate_code(self: Any, prompt: str, formal_spec: Any)
```

Generate source code for prompt + optional formal specification.

---

---

## ConfiguredCodeGenerationProvider

Default provider that must be replaced by an injected runtime provider.

### Methods

#### ConfiguredCodeGenerationProvider.generate_code

```python
generate_code(self: Any, prompt: str, formal_spec: Any)
```

---

---

## GenerationResponse

Provider generation response with observability metadata.

---

## ProgramSynthesizer

Orchestrates neural-symbolic program generation.

### Methods

#### ProgramSynthesizer.__init__

```python
__init__(self: Any, run_id: str, provider: Any)
```

---

#### ProgramSynthesizer.synthesize

```python
synthesize(self: Any, prompt: str, formal_spec: Any)
```

Synthesize a program from a prompt and optional formal spec.

---

---

## SynthesisResult

Result of a neural-symbolic synthesis operation.

**Inherits from**: `BaseModel`

---

## generate_code

```python
generate_code(self: Any, prompt: str, formal_spec: Any) -> GenerationResponse
```

---

## synthesize

```python
synthesize(self: Any, prompt: str, formal_spec: Any)
```

Synthesize a program from a prompt and optional formal spec.

---

