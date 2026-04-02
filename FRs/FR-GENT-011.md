# FR-GENT-011: Fallback State Machine

## ID
- **FR-ID**: FR-GENT-011
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL implement a `FallbackStateMachine` that iterates through a provider list, executing each with retry, falling back to the next provider on usage limits, normalizing output via adapters, running semantic validation, evaluating fallback policies, and recording telemetry including drift events.

## Acceptance Criteria

- [ ] Iterates through provider list
- [ ] Retries each provider
- [ ] Falls back on usage limits
- [ ] Records telemetry and drift

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_fallback_state_machine` | `// @trace FR-GENT-011` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/fallback.py` | `FallbackStateMachine` | `@trace FR-GENT-011` |

## Related FRs

- FR-GENT-008: Provider Fallback Chain
- FR-GENT-010: Failure Classification

## Status

- **Current**: implemented
- **Since**: 2026-03-01
