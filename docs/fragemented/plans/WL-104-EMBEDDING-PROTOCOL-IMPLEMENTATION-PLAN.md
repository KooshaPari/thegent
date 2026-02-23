# WL-104 Implementation Plan: Embedding Protocol (JSON-RPC stdio Daemon)

## Status
- `blocked` (depends on `WL-102`)

## Unblock Condition
- Confirm `WL-102` completion and stable session/turn contract in CLI run path.

## Goal
- Implement `thegent agent-server` stdio daemon with Codex App Server v2-compatible JSONL request/response + notifications.

## Scope
- Add daemon entrypoint and protocol router.
- Implement methods:
  - `session/start`
  - `session/resume`
  - `turn/submit`
  - `turn/cancel`
  - `session/list`
  - `session/read`
  - `config/read`
- Implement notifications:
  - `turn/started`
  - `turn/completed`
  - `item/agentMessage/delta`
  - `item/toolCall/started`
  - `item/toolCall/completed`
  - `approval/requested`

## Planned File Touches
- `src/thegent/cli/apps/main.py`
- `src/thegent/cli/commands/cli.py`
- `src/thegent/session/` (new server session store module)
- `src/thegent/protocols/` (new JSON-RPC wire models)
- `src/thegent/agents/` (turn streaming adapters)
- `tests/protocols/`
- `tests/session/`

## Execution Steps
1. Add wire schemas for requests, responses, errors, notifications.
2. Add stdio message loop (`read line -> parse JSON -> dispatch -> write JSON`).
3. Implement session lifecycle endpoints first (`session/start`, `resume`, `list`, `read`).
4. Implement turn lifecycle (`turn/submit`, `turn/cancel`) with streamed notification fanout.
5. Add approval handshake (`approval/requested` + grant/reject correlation IDs).
6. Add fail-loud protocol errors for malformed payloads and unsupported methods.

## Validation Commands
- `uv run pytest -q tests/protocols`
- `uv run pytest -q tests/session`
- `uv run pytest -q tests/test_codex_proxy_improvements.py`
- `python -m py_compile src/thegent/cli/commands/cli.py`

## Acceptance Criteria
- JSON-RPC endpoints above pass contract tests.
- Notification ordering is deterministic for a single turn.
- Cancel path emits terminal turn event and no further deltas.
- Approval flow blocks gated action until grant/reject response.

## Wave-2 Do-Next Slice (Implementation-Ready)

### Deliverable
- Land protocol contract layer and server loop skeleton only (no agent execution wiring yet).

### Files for First Slice
- `src/thegent/protocols/jsonrpc_agent_server.py` (new)
- `src/thegent/cli/apps/main.py` (register `agent-server` command)
- `tests/protocols/test_jsonrpc_agent_server_contract.py` (new)

### Concrete Tasks
1. Define typed wire contracts for request/response/error/notification plus strict method whitelist.
2. Implement newline-delimited stdin loop with parse/dispatch/write and deterministic error envelopes.
3. Add stub handlers for `session/start`, `session/list`, `config/read` returning explicit `NOT_IMPLEMENTED` payloads.
4. Fail closed on unknown methods and malformed JSON with stable error codes.

### Focused Validation
- `uv run pytest -q tests/protocols/test_jsonrpc_agent_server_contract.py`
- `python -m py_compile src/thegent/protocols/jsonrpc_agent_server.py`

### Unblock Handoff
- Once `WL-102` confirms stable session/turn contract objects, replace stub handlers with real adapters in a follow-up slice.
