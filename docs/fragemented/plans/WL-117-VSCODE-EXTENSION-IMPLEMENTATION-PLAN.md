# WL-117 Implementation Plan: VS Code Extension (MCP Client + Session UI)

## Status
- `blocked` (depends on `WL-104`)

## Unblock Condition
- `WL-104` daemon protocol implemented with stable session/turn notifications.

## Goal
- Deliver VS Code extension at `extensions/vscode/` for session management + turn submission over stdio.

## Scope
- Extension host process launches `thegent agent-server`.
- Side panel for session list and active status.
- Chat input for `turn/submit`.
- Approval UI for `approval/requested` payloads.
- Skills tree using skill list API.

## Planned File Touches
- `extensions/vscode/package.json`
- `extensions/vscode/src/extension.ts`
- `extensions/vscode/src/protocol/client.ts`
- `extensions/vscode/src/views/`
- `extensions/vscode/src/state/`
- `extensions/vscode/test/`

## Execution Steps
1. Scaffold extension commands + activation events.
2. Implement stdio JSON-RPC client transport and reconnection policy.
3. Add session tree view (`session/list`, `session/read`) and active context bar.
4. Add chat input command path (`turn/submit`) and streaming output panel.
5. Add approval request panel with explicit Approve/Reject actions.
6. Package + integration tests for extension host flow.

## Validation Commands
- `cd extensions/vscode && npm test`
- `cd extensions/vscode && npm run lint`
- `cd extensions/vscode && npm run package`

## Acceptance Criteria
- Extension can start/resume a session and submit turns.
- Approval prompts render diff and return grant/reject responses.
- Skills list is visible and refreshable from command palette.

## Wave-2 Do-Next Slice (Implementation-Ready)

### Deliverable
- Land extension scaffold and protocol client abstraction with fake transport tests (no dependency on live daemon yet).

### Files for First Slice
- `extensions/vscode/package.json` (new)
- `extensions/vscode/src/extension.ts` (new)
- `extensions/vscode/src/protocol/client.ts` (new)
- `extensions/vscode/test/protocolClient.test.ts` (new)

### Concrete Tasks
1. Scaffold activation events, command registration, and extension host entrypoint.
2. Implement JSON-RPC client abstraction with request IDs, timeout handling, and event emitters.
3. Add fake transport tests for request/response correlation and notification fanout.
4. Defer UI panels (session tree/approval/chat) until `WL-104` wire protocol is available.

### Focused Validation
- `cd extensions/vscode && npm run test`
- `cd extensions/vscode && npm run lint`

### Unblock Handoff
- Once `WL-104` daemon notifications are stable, plug transport into stdio process launcher and wire concrete views.
