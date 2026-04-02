# FR-GENT-003: Noisy Stderr Filtering

## ID
- **FR-ID**: FR-GENT-003
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL filter known noisy stderr patterns (node deprecation warnings, hook registry messages, usage stats, copilot info lines) from direct agent output before returning results, preserving only meaningful error content.

## Acceptance Criteria

- [ ] Filters node deprecation warnings
- [ ] Filters hook registry messages
- [ ] Filters usage stats output
- [ ] Preserves actual error messages

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_stderr_filtering` | `// @trace FR-GENT-003` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/agents/filters.py` | `filter_noisy_stderr()` | `@trace FR-GENT-003` |

## Related FRs

- FR-GENT-002: Direct Agent Invocation

## Status

- **Current**: implemented
- **Since**: 2026-01-20
