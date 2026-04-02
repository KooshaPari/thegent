# FR-GENT-002: Direct Agent Invocation

## ID
- **FR-ID**: FR-GENT-002
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL invoke cursor-agent, gemini, codex, copilot, and claude agents directly through their native CLI binaries, resolving binary paths via environment variables (`THGENT_{AGENT}_CMD`), `shutil.which`, or `~/.local/bin` fallback locations.

## Acceptance Criteria

- [ ] Invokes agents via native CLIs
- [ ] Resolves paths via env vars, which, or fallback
- [ ] Supports all listed agents
- [ ] Handles missing binaries gracefully

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_direct_invocation` | `// @trace FR-GENT-002` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/agents/direct.py` | `DirectAgentRunner` | `@trace FR-GENT-002` |

## Related FRs

- FR-GENT-001: Base Runner Interface

## Status

- **Current**: implemented
- **Since**: 2026-01-15
