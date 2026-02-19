# proof_carrying API Reference

> **Source**: `src/thegent/verification/proof_carrying.py`

WP-18003: Proof-Carrying Code for MCP Tools.
Ensures that all MCP tools carry logical proofs or signatures that can be verified at runtime.

---

## PCCVerifier

Verifies proof-carrying code for MCP tools.

### Methods

#### PCCVerifier.__init__

```python
__init__(self)
```

#### PCCVerifier.register_proof

Register a proof for a tool.

```python
register_proof(self, tool_id, property_id, signature, proof_type)
```

#### PCCVerifier.verify_tool

Verify that a tool's code matches its registered proofs.

```python
verify_tool(self, tool_id, tool_code)
```

---

## Proof

A proof or signature for an MCP tool.

**Inherits from**: `BaseModel`

---

## register_proof

Register a proof for a tool.

```python
register_proof(self, tool_id, property_id, signature, proof_type)
```

---

## verify_tool

Verify that a tool's code matches its registered proofs.

```python
verify_tool(self, tool_id, tool_code)
```

---

