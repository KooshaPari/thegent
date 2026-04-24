# FR-GENT-020: Compliance Validation

## ID
- **FR-ID**: FR-GENT-020
- **Repository**: thegent
- **Domain**: GOV (Governance)

## Description

The system SHALL validate compliance with organizational policies by checking evidence coverage against defined rules. The compliance report SHALL summarize FR coverage, identify gaps, and provide recommendations for remediation.

## Acceptance Criteria

- [ ] Validates FR coverage per rule
- [ ] Generates compliance report
- [ ] Identifies coverage gaps
- [ ] Provides remediation recommendations

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `crates/thegent-policy/tests/compliance_tests.rs` | `test_compliance_validation` | `/// @trace FR-GOV-004` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `crates/thegent-policy/src/compliance.rs` | `validate_compliance()` | `/// @trace FR-GOV-004` |

## Related FRs

- FR-GENT-019: Policy Engine

## Status

- **Current**: implemented
- **Since**: 2026-02-15
