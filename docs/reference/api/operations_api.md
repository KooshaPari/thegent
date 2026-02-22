# operations API Reference

> **Source**: `src/thegent/operations.py`

Universal operation interfaces for thegent orchestration.

Stable operation-based taxonomy per Kush docs deep dive (D-B).
Maps CLI commands to operations: orchestrate, govern, recover, observe, plan.

---

## Operation

Canonical operation types for thegent capabilities.

**Inherits from**: `StrEnum`

---

## OperationEntry

A command or capability mapped to an operation.

---

## get_operations_by_type

```python
get_operations_by_type(op: Operation)
```

Return all entries for an operation type.

---

## list_operations

Return operations grouped by type for CLI/MCP.

---
