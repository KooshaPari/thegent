# FR-GENT-010: Failure Classification

## ID
- **FR-ID**: FR-GENT-010
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL classify agent run failures into FailureKind categories (RATE_LIMIT for 429/too-many-requests, TRANSIENT for 502/503/504/reconnecting, USAGE_LIMIT for quota/subscription/billing exhaustion, UNKNOWN otherwise) by matching stderr and stdout against defined regex patterns.

## Acceptance Criteria

- [ ] Classifies RATE_LIMIT (429)
- [ ] Classifies TRANSIENT (502/503/504)
- [ ] Classifies USAGE_LIMIT (quota/billing)
- [ ] Returns UNKNOWN for unclassified

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_failure_classification` | `// @trace FR-GENT-010` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/errors.py` | `classify_failure()` | `@trace FR-GENT-010` |

## Related FRs

- FR-GENT-009: Retry with Exponential Backoff

## Status

- **Current**: implemented
- **Since**: 2026-02-25
