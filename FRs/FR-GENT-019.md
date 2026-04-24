# FR-GENT-019: Policy Engine

## ID
- **FR-ID**: FR-GENT-019
- **Repository**: thegent
- **Domain**: GOV (Governance)

## Description

The system SHALL implement a policy engine that evaluates governance rules against agent outputs. Rules SHALL be defined in a declarative format with conditions and actions. The engine SHALL support rule evaluation by ID and context, returning allow/deny/warn decisions with reasons.

## Acceptance Criteria

- [ ] Defines policy rule format
- [ ] Evaluates rules by ID
- [ ] Returns allow/deny/warn
- [ ] Includes decision reasons

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `crates/thegent-policy/tests/integration_tests.rs` | `test_policy_engine` | `/// @trace FR-GOV-001` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `crates/thegent-policy/src/engine.rs` | `PolicyEngine` | `/// @trace FR-GOV-001` |

## Related FRs

- FR-GENT-020: Compliance Validation

## Status

- **Current**: implemented
- **Since**: 2026-02-10
