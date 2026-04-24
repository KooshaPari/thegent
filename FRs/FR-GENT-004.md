# FR-GENT-004: Codex Proxy Runner

## ID
- **FR-ID**: FR-GENT-004
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL support running agents (claude, codex, gemini, copilot, antigravity, minimax, glm, cliproxy, roo, kilo) through CLIProxyAPIPlus by configuring the proxy base URL as `OPENAI_BASE_URL` and mapping each agent to its default model ID.

## Acceptance Criteria

- [ ] Supports all listed agents via proxy
- [ ] Configures `OPENAI_BASE_URL`
- [ ] Maps agents to model IDs
- [ ] Handles proxy failures gracefully

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_proxy_runner` | `// @trace FR-GENT-004` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/agents/proxy.py` | `CodexProxyRunner` | `@trace FR-GENT-004` |

## Related FRs

- FR-GENT-002: Direct Agent Invocation

## Status

- **Current**: implemented
- **Since**: 2026-01-25
