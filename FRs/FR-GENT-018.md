# FR-GENT-018: Semantic Validation

## ID
- **FR-ID**: FR-GENT-018
- **Repository**: thegent
- **Domain**: CTR (Contracts)

## Description

The system SHALL validate CSM invariants including: COMPLETED status requires progress >= 1.0 and non-empty summary; PENDING status requires progress == 0.0; FAILED status requires non-empty issues or decision_reason_code; REVIEWER phase requires decision_reason_code; PLANNER COMPLETED requires objective; OPERATOR COMPLETED requires actions_completed or summary.

## Acceptance Criteria

- [ ] Validates COMPLETED requirements
- [ ] Validates PENDING requirements
- [ ] Validates FAILED requirements
- [ ] Validates phase-specific requirements

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/validation_tests.rs` | `test_semantic_validation` | `// @trace FR-GENT-018` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/validation.py` | `validate_csm()` | `@trace FR-GENT-018` |

## Related FRs

- FR-GENT-014: Canonical Structured Message Schema

## Status

- **Current**: implemented
- **Since**: 2026-02-05
