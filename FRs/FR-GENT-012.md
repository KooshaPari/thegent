# FR-GENT-012: Droid Runner

## ID
- **FR-ID**: FR-GENT-012
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL invoke Factory droids via `droid exec` subprocess with frontmatter-parsed config, resolving the droid binary from `~/.local/bin/droid` or `~/.factory/bin/droid`, supporting prompt injection, working directory, timeout, and streaming output.

## Acceptance Criteria

- [ ] Invokes droids via `droid exec`
- [ ] Parses frontmatter config
- [ ] Resolves droid binary path
- [ ] Supports streaming output

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_droid_runner` | `// @trace FR-GENT-012` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/agents/droid.py` | `DroidRunner` | `@trace FR-GENT-012` |

## Related FRs

- FR-GENT-001: Base Runner Interface

## Status

- **Current**: implemented
- **Since**: 2026-03-05
