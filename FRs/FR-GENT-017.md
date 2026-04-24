# FR-GENT-017: Contract Telemetry

## ID
- **FR-ID**: FR-GENT-017
- **Repository**: thegent
- **Domain**: CTR (Contracts)

## Description

The system SHALL record normalization events to a JSONL file (`contract_telemetry.jsonl`) with timestamp, event_type, run_id, provider, contract, confidence, and success fields, emit structural and semantic drift events per G-RV-07, and provide `get_drift_budget_status()` to check drift rates against configurable budgets (default 5% structural, 10% semantic).

## Acceptance Criteria

- [ ] Records events to JSONL
- [ ] Includes all required fields
- [ ] Emits drift events
- [ ] `get_drift_budget_status()` works

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/telemetry_tests.rs` | `test_contract_telemetry` | `// @trace FR-GENT-017` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/telemetry.py` | `record_telemetry()` | `@trace FR-GENT-017` |

## Related FRs

- FR-GENT-016: Provider Adapter Registry

## Status

- **Current**: implemented
- **Since**: 2026-02-01
