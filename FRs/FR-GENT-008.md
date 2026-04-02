# FR-GENT-008: Provider Fallback Chain

## ID
- **FR-ID**: FR-GENT-008
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL define ordered fallback chains per provider so that when an agent hits a usage limit, `get_fallback_agents()` returns the next providers to attempt, excluding the current agent from the chain.

## Acceptance Criteria

- [ ] Defines fallback chains per provider
- [ ] Excludes current agent from chain
- [ ] Returns ordered list of fallbacks
- [ ] Handles unknown providers gracefully

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_fallback_chain` | `// @trace FR-GENT-008` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/fallback.py` | `get_fallback_agents()` | `@trace FR-GENT-008` |

## Related FRs

- FR-GENT-011: Fallback State Machine

## Status

- **Current**: implemented
- **Since**: 2026-02-15
