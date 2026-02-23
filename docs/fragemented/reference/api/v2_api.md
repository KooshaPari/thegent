# v2 API Reference

> **Source**: `src/thegent/contracts/csm/v2/__init__.py`

WP-10001: Operation envelope schema v2.

Provides a unified schema for all operations across CLI and MCP.

---

## OperationEnvelopeV2

Unified operation envelope for Phase 10 convergence.

**Inherits from**: `BaseModel`

---

## validate_envelope_v2

```python
validate_envelope_v2(envelope: dict[(str, Any)])
```

Validate a raw dict against the OperationEnvelopeV2 schema.

---
