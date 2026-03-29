<DONE>
# Research — Governance Escalation + DLQ

**WORK_STREAM ID:** `research-governance-escalation-dlq`
**Priority:** P2
**Status:** ✅ Implemented

## Purpose

Clarify DLQ-to-escalation integration rules and implementation boundary for terminal/recovery-fail paths.

## Decision and Evidence

- Escalation is now explicit in `DLQManager.enqueue(...)` and only emitted when terminal reason is provided.
- Existing playbook path passes explicit reason `"Recovery attempts exhausted"` for `dlq_enqueue` flows.
- This removes implicit escalation and ensures non-terminal queueing does not create noise in escalation queue.

## Evidence

- `src/thegent/execution.py` (added optional `reason_for_escalation` + explicit escalate call)
- `src/thegent/orchestration/strategies/playbooks.py` (explicit recovery-exhausted reason in DLQ enqueue path)
- `tests/test_unit_dlq_manager.py` (covers escalate/no-escalate branches)

## Decision

- Workstream item is now complete with a tested implementation path.
