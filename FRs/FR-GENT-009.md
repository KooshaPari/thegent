# FR-GENT-009: Retry with Exponential Backoff

## ID
- **FR-ID**: FR-GENT-009
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL retry agent subprocess executions using tenacity with configurable max_attempts (default 4), exponential wait (min 2s, max 60s), retrying only on `TransientAgentError` exceptions classified as rate_limit or transient failures.

## Acceptance Criteria

- [ ] Configurable max attempts (default 4)
- [ ] Exponential backoff 2s-60s
- [ ] Only retries on `TransientAgentError`
- [ ] Uses tenacity for retry logic

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_retry_backoff` | `// @trace FR-GENT-009` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/retry.py` | `retry_with_backoff()` | `@trace FR-GENT-009` |

## Related FRs

- FR-GENT-010: Failure Classification

## Status

- **Current**: implemented
- **Since**: 2026-02-20
