# FR-GENT-006: CLIProxyAPIPlus Lifecycle

## ID
- **FR-ID**: FR-GENT-006
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL manage the CLIProxyAPIPlus proxy lifecycle including binary resolution, config YAML generation with provider blocks (minimax, glm, antigravity via iFlow), proxy process startup with health-check polling, and ready-timeout enforcement of 5 seconds.

## Acceptance Criteria

- [ ] Resolves proxy binary path
- [ ] Generates config YAML with providers
- [ ] Starts proxy process
- [ ] Health-check polling with 5s timeout

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_proxy_lifecycle` | `// @trace FR-GENT-006` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/proxy/lifecycle.py` | `ProxyManager` | `@trace FR-GENT-006` |

## Related FRs

- FR-GENT-004: Codex Proxy Runner

## Status

- **Current**: implemented
- **Since**: 2026-02-05
