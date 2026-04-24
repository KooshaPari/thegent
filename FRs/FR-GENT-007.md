# FR-GENT-007: Agent Registry

## ID
- **FR-ID**: FR-GENT-007
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL maintain a canonical registry of agent names (gemini, codex, copilot, cursor-agent, cursor-api, claude, antigravity, minimax, glm, cliproxy, roo, kilo), resolve aliases (e.g. "cursor" to "cursor-agent"), and return the appropriate runner type via `get_runner()`.

## Acceptance Criteria

- [ ] Maintains canonical agent registry
- [ ] Resolves aliases to canonical names
- [ ] Returns correct runner type per agent
- [ ] `get_runner()` works for all agents

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_agent_registry` | `// @trace FR-GENT-007` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/registry.py` | `AgentRegistry` | `@trace FR-GENT-007` |

## Related FRs

- FR-GENT-001: Base Runner Interface

## Status

- **Current**: implemented
- **Since**: 2026-02-10
