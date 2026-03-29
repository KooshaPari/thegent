# Merged Fragmented Markdown

## Source: /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/extensions/vscode/docs
## Source: protocol-contract.md

# thegent VS Code Extension — Protocol Contract (WL-117)

Contract between `extensions/vscode` and `thegent agent-server`.

## Transport

- **JSON-RPC 2.0 over stdio**
- Newline-delimited JSON (`jsonl`)
- Launched via `child_process.spawn('thegent', ['agent-server'])`
- Client writes requests to `stdin`; server writes responses + notifications to `stdout`

## Request Methods

| Method | Direction | Status | Notes |
| --- | --- | --- | --- |
| `health/check` | client→server | IMPLEMENTED | Returns `{ status, service, transport }` |
| `config/read` | client→server | IMPLEMENTED | Returns `{ server, transport, supported_methods[] }` |
| `session/start` | client→server | IMPLEMENTED | Returns `{ session }` |
| `session/resume` | client→server | IMPLEMENTED | Params: `{ session_id }`, returns `{ session }` |
| `session/list` | client→server | IMPLEMENTED | Returns `{ sessions[] }` |
| `session/read` | client→server | IMPLEMENTED | Params: `{ session_id }`, returns `{ session, turns[] }` |
| `turn/submit` | client→server | IMPLEMENTED | Params: `{ session_id, input, requires_approval }` |
| `turn/cancel` | client→server | IMPLEMENTED | Params: `{ turn_id }`, returns `{ turn }` |
| `approval/grant` | client→server | IMPLEMENTED | Params: `{ approval_id }`, returns `{ approval, turn }` |
| `approval/reject` | client→server | IMPLEMENTED | Params: `{ approval_id }`, returns `{ approval, turn }` |

## Notifications (server → client, no `id` field)

| Method | Params | Description |
| --- | --- | --- |
| `turn/started` | `{ session_id, turn_id }` | Turn processing begun |
| `turn/completed` | `{ session_id, turn_id, status }` | Turn reached terminal state |
| `item/agentMessage/delta` | `{ session_id, turn_id, delta }` | Streaming agent message chunk |
| `item/toolCall/started` | `{ session_id, turn_id, tool_call_id, tool_name }` | Tool invocation started |
| `item/toolCall/completed` | `{ session_id, turn_id, tool_call_id, output }` | Tool invocation completed |
| `approval/requested` | `{ approval_id, session_id, turn_id, diff? }` | Human-in-the-loop approval needed |

## Error Codes

| Code | Meaning |
| --- | --- |
| `-32700` | Parse error — invalid JSON |
| `-32600` | Invalid Request |
| `-32601` | Method not found |
| `-32602` | Invalid params |
| `-32001` | Session not found |
| `-32002` | Turn not found |
| `-32003` | Turn already terminal |
| `-32004` | Method recognized but not implemented (reserved) |
| `-32005` | Approval not found |
| `-32006` | Approval already resolved |

## Session Status Values

`active` | `paused` | `completed` | `failed`

## Turn Status Values

`in_progress` | `awaiting_approval` | `completed` | `cancelled` | `rejected`

## Approval Status Values

`requested` | `granted` | `rejected` | `cancelled`

## RunResult (context budget)

```typescript
interface RunResult {
  session_id: string;
  turn_id: string;
  context_usage_ratio: number; // 0.0–1.0
  output?: string;
}
```

The extension listens for `context/budgetUpdated` internal events (emitted by `AgentServerClient.notifyContextBudget()`) to update the status bar. The ratio maps to a percentage display: `$(circuit-board) 45% context`.

## Fail-Fast Contract

- If `thegent agent-server` process fails to spawn → `AgentServerConnectionError` thrown immediately
- If stdio connection closes unexpectedly → all pending requests rejected with `AgentServerProtocolError(-1, ...)`
- If server returns JSON-RPC error response → Promise rejects with `AgentServerProtocolError`
- No silent failures, no fallbacks, no legacy compatibility shims

---
