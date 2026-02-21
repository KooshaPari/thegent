# thegent VS Code Extension (WL-117)

VS Code extension for thegent — MCP client + session management UI.

Connects to `thegent agent-server` via `child_process.spawn` with JSON-RPC 2.0 over stdio (JSONL).

## Architecture

```
VS Code Extension
├── src/extension.ts             — activate/deactivate, command registration
├── src/agentServerClient.ts     — stdio transport client (child_process + JSONL)
├── src/sessionListProvider.ts   — TreeDataProvider for Sessions side panel
├── src/contextBudgetStatusBar.ts — status bar context budget indicator
├── src/approvalWebviewPanel.ts  — diff display + Approve/Reject webview
├── src/types.ts                 — shared wire-format types (JSON-RPC 2.0)
├── src/protocol/client.ts       — ProtocolClient interface (protocol contract)
└── src/__tests__/               — 15+ integration tests (Node, no VS Code host)
```

## Commands

| Command | ID | Description |
|---|---|---|
| Start New Session | `thegent.start` | Spawns agent-server, starts a new session |
| List Sessions | `thegent.listSessions` | Refreshes the session tree view |
| Resume Session | `thegent.resume` | Resumes a selected/named session |
| Start Session | `thegent.startSession` | Alias for thegent.start |
| Submit Turn | `thegent.submitTurn` | Prompts for input, submits to latest session |
| Show Sessions | `thegent.showSessions` | Alias for thegent.listSessions |

## Views

- **thegent Sessions** (Explorer panel): Live session list with status icons

## Status Bar

- Right-aligned status bar item shows context budget: `$(circuit-board) 45% context`
- Updates from `RunResult.context_usage_ratio`
- Warning color at 70%+, error color at 90%+

## Approval Webview

When `approval/requested` fires from agent-server, a webview panel opens showing:
- Approval ID, session ID, turn ID metadata
- Diff payload (if present in notification params)
- **Approve** and **Reject** buttons — calls `approval/grant` or `approval/reject`

## Configuration

| Setting | Default | Description |
|---|---|---|
| `thegent.agentServerCommand` | `thegent` | Binary/command to invoke |
| `thegent.agentServerArgs` | `["agent-server"]` | Arguments passed to command |

## Wire Format

JSON-RPC 2.0 over stdio (JSONL — newline-delimited JSON).

Transport: `child_process.spawn('thegent', ['agent-server'])` with `stdin`/`stdout` pipes.

### Supported Methods

- `health/check` — returns `{ status, service, transport }`
- `config/read` — returns `{ server, transport, supported_methods }`
- `session/start` — returns `{ session }`
- `session/resume` — params: `{ session_id }`, returns `{ session }`
- `session/list` — returns `{ sessions[] }`
- `session/read` — params: `{ session_id }`, returns `{ session, turns[] }`
- `turn/submit` — params: `{ session_id, input, requires_approval }`, returns `{ turn, approval? }`
- `turn/cancel` — params: `{ turn_id }`, returns `{ turn }`
- `approval/grant` — params: `{ approval_id }`, returns `{ approval, turn }`
- `approval/reject` — params: `{ approval_id }`, returns `{ approval, turn }`

### Notifications (server → client)

- `turn/started` — `{ session_id, turn_id }`
- `turn/completed` — `{ session_id, turn_id, status }`
- `item/agentMessage/delta` — `{ session_id, turn_id, delta }`
- `item/toolCall/started` — `{ session_id, turn_id, tool_call_id, tool_name }`
- `item/toolCall/completed` — `{ session_id, turn_id, tool_call_id, output }`
- `approval/requested` — `{ approval_id, session_id, turn_id, diff? }`

## Run Steps

```bash
cd extensions/vscode
npm install
npm run typecheck
npm run lint
npm run test
```

## Build

```bash
cd extensions/vscode
npm run compile   # TypeScript → out/
```

## Error Handling

All errors fail fast and loudly:
- `AgentServerConnectionError` — spawn failed, stdin write failed, process closed
- `AgentServerProtocolError` — JSON-RPC error response, parse error, unexpected message

No fallback code paths. If `thegent agent-server` is unavailable, the error surfaces to the user via `vscode.window.showErrorMessage`.

## Tests

15+ integration tests in `src/__tests__/` covering:
- Wire-format type guards
- Client request/response correlation
- Notification event routing
- Error propagation (protocol errors, connection errors)
- Session/turn/approval full lifecycle
- Context budget event emission
- Status bar ratio rendering
- Session list provider data logic

All test files carry `// @trace WL-117` comments.

Compile check: `cd extensions/vscode && npx tsc --noEmit`
