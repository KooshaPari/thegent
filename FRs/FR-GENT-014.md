# FR-GENT-014: Canonical Structured Message Schema

## ID
- **FR-ID**: FR-GENT-014
- **Repository**: thegent
- **Domain**: CTR (Contracts)

## Description

The system SHALL define a `CanonicalStructuredMessage` dataclass with fields for identifiers (task_id, run_id, chunk_id), lifecycle (status as CSMStatus enum, phase as CSMPhase enum, progress 0.0-1.0), content (objective, summary, actions_completed, issues, next_steps), governance (evidence_set_hash, policy_gate_id, decision_reason_code), and metadata (schema_version "csm-v1", source_contract, raw_payload), with `to_dict()` and `from_dict()` serialization.

## Acceptance Criteria

- [ ] Defines CSM dataclass with all fields
- [ ] Status and phase as enums
- [ ] Progress is 0.0-1.0 range
- [ ] `to_dict()` and `from_dict()` work

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/csm_tests.rs` | `test_csm_schema` | `// @trace FR-GENT-014` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/contracts/csm.py` | `CanonicalStructuredMessage` | `@trace FR-GENT-014` |

## Related FRs

- FR-GENT-015: XML Parser

## Status

- **Current**: implemented
- **Since**: 2026-01-15
