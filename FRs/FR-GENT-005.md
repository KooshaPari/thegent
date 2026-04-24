# FR-GENT-005: Cursor API Runner

## ID
- **FR-ID**: FR-GENT-005
- **Repository**: thegent
- **Domain**: AGT (Agents)

## Description

The system SHALL support running cursor-api agents through the wisdgod cursor-api backend by verifying reachability via `GET /v1/models`, configuring `OPENAI_BASE_URL` and `OPENAI_API_KEY` from settings, and executing codex CLI with the proxy model.

## Acceptance Criteria

- [ ] Verifies backend reachability
- [ ] Configures OpenAI-compatible settings
- [ ] Executes via codex CLI
- [ ] Handles API errors gracefully

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/agent_tests.rs` | `test_cursor_api_runner` | `// @trace FR-GENT-005` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/agents/cursor.py` | `CursorApiRunner` | `@trace FR-GENT-005` |

## Related FRs

- FR-GENT-004: Codex Proxy Runner

## Status

- **Current**: implemented
- **Since**: 2026-02-01
