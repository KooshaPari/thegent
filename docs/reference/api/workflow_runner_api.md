# workflow_runner API Reference

> **Source**: `src/thegent/ports/driven/workflow_runner.py`

Protocol for workflow/pipeline execution.

---

## WorkflowRunner

Port interface for workflow and pipeline execution.

Breaks cli ↔ workflow circular dependency by allowing CLI code
to invoke workflows without importing workflow orchestration details.

**Inherits from**: `Protocol`

---

