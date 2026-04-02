# FR-GENT-001: Base Runner Interface

## ID
- **FR-ID**: FR-GENT-001
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL define an `AgentRunner` base class with a `run()` method accepting prompt, cwd, mode, timeout, streaming flags, and stdout/stderr callbacks, returning a `RunResult` with exit_code, stdout, stderr, and timed_out fields.

## Acceptance Criteria

- [ ] Defines `AgentRunner` abstract base class
- [ ] `run()` accepts all required parameters
- [ ] Returns `RunResult` with all fields
- [ ] Supports streaming and non-streaming modes

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_base_runner` | `// @trace FR-GENT-001` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/runner.py` | `AgentRunner` | `@trace FR-GENT-001` |

## Related FRs

- FR-GENT-002: Direct Agent Invocation

## Status

- **Current**: implemented
- **Since**: 2026-01-10
