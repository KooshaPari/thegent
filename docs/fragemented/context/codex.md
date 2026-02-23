# Codex Harness Context

> Definitive reference for implementing Codex support in thegent (agent harness integration, programmatic SDK, app-server protocol, MCP server, CLI invocation, sandbox/approval system).
> Primary source: Direct analysis of codex-upstream Rust monorepo at `/Users/kooshapari/temp-PRODVERCEL/485/API/codex-upstream/`. Verified 2026-02-20.
> Full research: `docs/research/CODEX_HARNESS_RESEARCH_2026-02-20.md`

---

## What is Codex

Codex is OpenAI's agentic coding harness: a compiled Rust binary (`codex-rs`) with a TypeScript CLI shim (`codex-cli`) and a TypeScript programmatic SDK (`@openai/codex-sdk`). Unlike web-based tools, Codex:

- Operates on files and shell via `apply_patch` and `shell_exec` tools registered with the OpenAI Responses API
- Enforces approval policies (untrusted / on-failure / on-request / never) for each command and file change
- Provides platform-specific sandboxing: Linux Landlock + seccomp, macOS sandbox profiles, Windows token restriction
- Exposes a bidirectional JSON-RPC-like protocol over stdio (`codex app-server`) for IDE/tool integration
- Provides a formal programmatic TypeScript SDK (`@openai/codex-sdk`) wrapping the exec subprocess
- Exposes a prototype MCP server mode (`codex mcp server`) with two tools
- Maintains layered TOML configuration: MDM > system > user > project > session flags

**Architecture**:

```
codex (binary, Rust)
├── codex-rs/app-server          <- App Server daemon (JSON-RPC-like over stdio)
├── codex-rs/app-server-protocol <- Protocol schemas (v1 deprecated + v2 current)
├── codex-rs/mcp-server          <- MCP server mode (prototype, 2 tools)
├── codex-rs/codex-api           <- Backend client (Responses API, exclusively streaming)
├── codex-rs/exec                <- `codex exec` non-interactive subcommand
├── codex-rs/tui                 <- Terminal UI (Ratatui-based)
└── sdk/typescript               <- @openai/codex-sdk (Node.js 18+)
```

The App Server powers ALL surfaces: CLI TUI, VS Code extension, JetBrains, Xcode, macOS desktop, web app, and Codex Cloud. The TypeScript SDK (`@openai/codex-sdk`) wraps `codex exec --experimental-json` as a subprocess — it does NOT use the app-server protocol.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| Thread | Persistent conversation session, recorded as rollout file in `$CODEX_HOME/sessions/` |
| Turn | One user-input → agent-response cycle within a thread |
| Item | Atomic event during a turn: agent_message, command_execution, file_change, mcp_tool_call, etc. |
| App Server | Codex daemon process communicating over bidirectional JSONL stdio |
| v1 protocol | Deprecated method namespace (`newConversation`, `sendUserTurn`); do not use |
| v2 protocol | Current method namespace (`thread/start`, `turn/start`); use exclusively |
| Sandbox policy | Filesystem/network access policy: `read-only`, `workspace-write`, `danger-full-access` |
| Approval policy | Human-in-the-loop gate: `untrusted`, `on-failure`, `on-request`, `never` |
| Dynamic tool | Client-registered tool that the model can invoke; execution routed back to the client |
| Skill | SKILL.md/SKILL.json reusable agent instructions discoverable from `.codex/skills/` directories |

---

## Backend API: `/v1/responses`

Codex exclusively uses the OpenAI **Responses API** (`POST /v1/responses`), always with `stream: true`. It does NOT use Chat Completions API (except for legacy local-provider fallback).

### Request Shape

```
POST /v1/responses
Content-Type: application/json
Authorization: Bearer $CODEX_API_KEY

{
  "model": "gpt-5.1-codex-max",
  "instructions": "...",
  "input": [...],               // ResponseItem array
  "tools": [...],               // apply_patch, shell_exec, web_search, etc.
  "tool_choice": "auto",
  "parallel_tool_calls": true,
  "reasoning": {                // o-series models
    "effort": "high",           // minimal | low | medium | high | xhigh
    "summary": "..."
  },
  "store": true,                // Azure: true; OpenAI direct: false
  "stream": true,               // always true
  "text": {                     // structured output
    "format": {
      "type": "json_schema",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Provider Routing

Codex only natively supports OpenAI and Azure. For other providers, use `OPENAI_BASE_URL` to proxy through a compatible gateway (LiteLLM, CLIProxy, etc.). The proxy MUST support the Responses API format (not just Chat Completions).

```bash
export OPENAI_BASE_URL="http://localhost:8317/v1"
export CODEX_API_KEY="your-proxy-key"
```

---

## CLI Subcommands and Flags

### Primary Subcommands

| Command | Description |
|---------|-------------|
| `codex` | Interactive TUI |
| `codex exec` | Non-interactive (alias: `codex e`) |
| `codex app-server` | App Server mode (JSON-RPC stdio) |
| `codex mcp server` | MCP server mode (prototype) |
| `codex resume <id>` | Resume previous session |
| `codex fork` | Fork previous session |
| `codex login` | Authenticate |
| `codex logout` | Remove credentials |

### Key Global Flags

| Flag | Values | Purpose |
|------|--------|---------|
| `--model, -m` | string | Override model |
| `--sandbox, -s` | `read-only` / `workspace-write` / `danger-full-access` | Sandbox policy |
| `--ask-for-approval, -a` | `untrusted` / `on-request` / `on-failure` / `never` | Approval policy |
| `--cd, -C` | path | Working directory |
| `--add-dir` | path | Additional writable directory |
| `--config, -c` | `key=value` | Config override (TOML key=value) |
| `--profile, -p` | string | Named config profile |
| `--image, -i` | path(s) | Attach local images |
| `--full-auto` | — | Alias for workspace-write sandbox |
| `--dangerously-bypass-approvals-and-sandbox` | — | No approvals, no sandbox |
| `--search` | — | Enable live web search |

### Exec-Mode-Specific Flags

| Flag | Purpose |
|------|---------|
| `--experimental-json` | REQUIRED for JSONL machine-parseable output |
| `--ephemeral` | Skip session persistence |
| `--output-schema <path>` | JSON Schema file for structured output |
| `--skip-git-repo-check` | Allow running outside git repos |
| `--output-last-message, -o <path>` | Write final agent message to file |

### IMPORTANT: Correct Flag Names

The following are correct flag names as of 2026. Earlier context docs had wrong names:

- CORRECT: `--ask-for-approval` (NOT `--approval-policy`)
- CORRECT: `--experimental-json` (NOT `--json`)
- CORRECT: `--sandbox` (same, but values use hyphens: `read-only`, `workspace-write`, `danger-full-access`)

---

## Programmatic TypeScript SDK

**Package**: `@openai/codex-sdk`
**Requirements**: Node.js 18+

The SDK spawns `codex exec --experimental-json` as a subprocess and parses JSONL output. It does NOT use the app-server protocol.

### Public API

```typescript
import { Codex } from "@openai/codex-sdk";

const client = new Codex({
  apiKey: "sk-...",              // or use CODEX_API_KEY env var
  baseUrl: "http://...",         // override for proxy routing
  config: { ... },              // CodexConfigObject flattened to --config flags
});

// Create a new thread
const thread = client.startThread({
  model: "gpt-5.1-codex-max",
  sandboxMode: "workspace-write",
  workingDirectory: "/path/to/project",
  skipGitRepoCheck: true,
  modelReasoningEffort: "high",   // minimal | low | medium | high | xhigh
  networkAccessEnabled: false,
  webSearchMode: "live",           // disabled | cached | live
  approvalPolicy: "never",         // never | on-request | on-failure | untrusted
  additionalDirectories: ["/extra/dir"],
});

// Resume an existing thread
const resumed = client.resumeThread("thread-id-123", { ... });

// Run (blocking, returns completed Turn)
const turn = await thread.run("Fix the TypeScript errors", {
  outputSchema: { type: "object", properties: { ... } },
  signal: new AbortController().signal,
});
console.log(turn.finalResponse);
console.log(turn.items);          // ThreadItem[]
console.log(turn.usage);          // { input_tokens, output_tokens }

// Run streamed (async generator)
const { events } = await thread.runStreamed("Build a REST API");
for await (const event of events) {
  if (event.type === "item.completed" && event.item.type === "agent_message") {
    console.log(event.item.text);
  }
}
```

### Input Types

```typescript
// Simple string
await thread.run("your prompt");

// Rich input array
await thread.run([
  { type: "text", text: "Analyze this image and fix the UI" },
  { type: "local_image", path: "/path/to/screenshot.png" },
]);
```

### ThreadItem Union (SDK)

```typescript
type ThreadItem =
  | { type: "agent_message"; id: string; text: string }
  | { type: "reasoning"; id: string; text: string }
  | { type: "command_execution"; id: string; command: string; aggregated_output: string; exit_code?: number; status: "in_progress" | "completed" | "failed" }
  | { type: "file_change"; id: string; changes: { path: string; kind: "add" | "delete" | "update" }[]; status: "completed" | "failed" }
  | { type: "mcp_tool_call"; id: string; server: string; tool: string; arguments: unknown; result?: { content: McpContentBlock[]; structured_content: unknown }; error?: { message: string }; status: "in_progress" | "completed" | "failed" }
  | { type: "web_search"; id: string; query: string }
  | { type: "todo_list"; id: string; items: { text: string; completed: boolean }[] }
  | { type: "error"; id: string; message: string }
```

### ThreadEvent Union (SDK streaming)

```typescript
type ThreadEvent =
  | { type: "thread.started"; thread_id: string }
  | { type: "turn.started" }
  | { type: "turn.completed"; usage: Usage }
  | { type: "turn.failed"; error: { message: string } }
  | { type: "item.started"; item: ThreadItem }
  | { type: "item.updated"; item: ThreadItem }
  | { type: "item.completed"; item: ThreadItem }
  | { type: "error"; message: string }
```

### How the SDK Invokes the Binary

```bash
codex exec --experimental-json \
    [--config key=val]... \
    [--model MODEL] \
    [--sandbox MODE] \
    [--cd DIR] \
    [--add-dir DIR]... \
    [--skip-git-repo-check] \
    [--output-schema FILE] \
    [--image FILE]... \
    [resume THREAD_ID]
```

The prompt is piped to stdin. JSONL events come from stdout. The SDK sets `CODEX_INTERNAL_ORIGINATOR_OVERRIDE=codex_sdk_ts` for telemetry. Platform-specific binaries are vendored in `vendor/{targetTriple}/codex/codex`.

---

## App Server Protocol (Advanced Integration)

The App Server is the highest-fidelity integration surface. It enables approval flows, dynamic tools, diff streaming, and full thread management that the TypeScript SDK does not expose.

### Transport

- Bidirectional JSONL over stdio
- NOT strict JSON-RPC 2.0: the `"jsonrpc": "2.0"` field is OMITTED from the wire
- Wire format: `{ id?, method, params? }` (request/notification) or `{ id, result }` / `{ id, error }` (response)

### Protocol Namespaces

- **v1**: `newConversation`, `sendUserTurn`, etc. — DEPRECATED. Do not use.
- **v2**: `thread/start`, `turn/start`, etc. — CURRENT. Use exclusively.

### Handshake

```
Client -> Server: { "id": 1, "method": "initialize", "params": { ... } }
Server -> Client: { "id": 1, "result": { ... } }
Client -> Server: { "method": "initialized" }   // notification, no id
```

### Key Client Requests (v2)

| Method | Params | Purpose |
|--------|--------|---------|
| `thread/start` | `ThreadStartParams` | Create new thread |
| `thread/resume` | `ThreadResumeParams` | Resume by id or path |
| `thread/list` | `ThreadListParams` | Paginated thread list |
| `thread/read` | `ThreadReadParams` | Read thread + items |
| `thread/rollback` | `ThreadRollbackParams` | Drop last N turns |
| `thread/fork` | `ThreadForkParams` | Fork existing thread |
| `turn/start` | `TurnStartParams` | Submit user input |
| `turn/interrupt` | `TurnInterruptParams` | Cancel in-flight turn |
| `review/start` | `ReviewStartParams` | Code review turn |
| `skills/list` | `SkillsListParams` | List available skills |
| `model/list` | — | List available models |
| `config/read` | `ConfigReadParams` | Read layered config |
| `config/value/write` | `ConfigValueWriteParams` | Write config key |
| `mcpServerStatus/list` | — | MCP server health |

### TurnStartParams (key fields)

```typescript
{
  thread_id: string,
  input: UserInput[],
  cwd?: string,
  approval_policy?: "untrusted" | "on-failure" | "on-request" | "never",
  sandbox_policy?: "read-only" | "workspace-write" | "danger-full-access",
  model?: string,
  effort?: "minimal" | "low" | "medium" | "high" | "xhigh",
  output_schema?: JsonValue,        // structured output (JSON Schema)
  collaboration_mode?: string,      // EXPERIMENTAL
}
```

### UserInput Union (v2)

```typescript
type UserInput =
  | { type: "Text"; text: string }
  | { type: "Image"; url: string }
  | { type: "LocalImage"; path: string }
  | { type: "Skill"; name: string; path: string }      // SKILL.md invocation
  | { type: "Mention"; name: string; path: string }    // file mention
```

### Key Server Notifications (v2)

| Notification | Content |
|-------------|---------|
| `thread/started` | Thread created with id |
| `turn/started` | Turn begin |
| `turn/completed` | Turn finished |
| `item/started` | Item lifecycle begin |
| `item/completed` | Item lifecycle complete |
| `item/agentMessage/delta` | Streaming text delta |
| `item/commandExecution/outputDelta` | Streaming shell output |
| `item/fileChange/outputDelta` | Streaming patch delta |
| `turn/diff/updated` | Aggregate unified diff update |
| `thread/tokenUsage/updated` | Per-turn token usage |

### Server Requests (Approval Flows)

The server sends these to the client and waits for a response:

| Method | Purpose |
|--------|---------|
| `item/commandExecution/requestApproval` | Human-in-the-loop exec approval |
| `item/fileChange/requestApproval` | Human-in-the-loop patch approval |
| `item/tool/call` | Client-side dynamic tool execution |
| `item/tool/requestUserInput` | EXPERIMENTAL: elicit user input |

### Dynamic Tools

Register client-side tools in `ThreadStartParams.dynamic_tools`:

```typescript
dynamic_tools: [
  {
    name: "open_file_in_editor",
    description: "Opens a file in the IDE editor",
    input_schema: { type: "object", properties: { path: { type: "string" } }, required: ["path"] }
  }
]
```

When the model calls a dynamic tool, the server sends `item/tool/call` with `{ callId, name, arguments }`. Client must respond with `{ output: string, success: boolean }`.

---

## MCP Server Mode (Prototype)

Start: `codex mcp server` (or `codex --mcp-server`)

Exposes exactly **two tools** over standard MCP protocol (JSON-RPC, JSONL stdio):

### Tool: `codex`

Starts a new Codex session. Input schema:

```json
{
  "required": ["prompt"],
  "properties": {
    "prompt": { "type": "string" },
    "model": { "type": "string" },
    "profile": { "type": "string" },
    "cwd": { "type": "string" },
    "approval-policy": { "type": "string", "enum": ["untrusted","on-failure","on-request","never"] },
    "sandbox": { "type": "string", "enum": ["read-only","workspace-write","danger-full-access"] },
    "config": { "type": "object" },
    "base-instructions": { "type": "string" },
    "developer-instructions": { "type": "string" },
    "compact-prompt": { "type": "string" }
  }
}
```

Output: `{ threadId: string, content: string }`

### Tool: `codex-reply`

Continues an existing session. Input schema:

```json
{
  "required": ["prompt"],
  "properties": {
    "threadId": { "type": "string" },
    "conversationId": { "type": "string", "description": "DEPRECATED: use threadId" },
    "prompt": { "type": "string" }
  }
}
```

### MCP Server Limitations

- Marked as prototype (`//! Prototype MCP server.` in source)
- Does NOT support approval flows, streaming events, or fine-grained item observation
- Use App Server protocol for serious integrations

---

## Configuration System

### Config Layers (precedence low to high)

1. MDM managed preferences (`com.openai.codex` domain on macOS)
2. System (`managed_config.toml`)
3. User (`~/.codex/config.toml` or `$CODEX_HOME/config.toml`)
4. Project (`.codex/config.toml` files from CWD up to repo root)
5. Session flags (`-c key=value` overrides)

### Key Config Fields

```toml
model = "gpt-5.1-codex-max"
approval_policy = "on-request"   # untrusted | on-failure | on-request | never
sandbox_mode = "workspace-write" # read-only | workspace-write | danger-full-access
web_search = "live"              # disabled | cached | live
model_reasoning_effort = "high"  # minimal | low | medium | high | xhigh
instructions = "..."
developer_instructions = "..."

[sandbox_workspace_write]
writable_roots = ["/path1"]
network_access = false

[profiles.fast]
model = "gpt-5.1"
approval_policy = "never"
```

### Session Flag Overrides

```bash
codex -c model="gpt-5.1" -c web_search="live" -c approval_policy="never" "query"
```

---

## Input/Output Modalities

### Text Input
- String prompt via stdin (exec mode)
- `UserInput::Text` with optional `text_elements` spans (app-server)

### Image Input
- `--image <path>` flag (one or more, exec mode)
- `{ type: "local_image", path }` in SDK input array
- `UserInput::Image { url }` for remote images (app-server only)

### Structured Output (JSON Schema)
- `--output-schema <json-schema-file>` (exec mode)
- `outputSchema` in SDK `TurnOptions`
- `output_schema` in `TurnStartParams` (app-server)
- Translated to `text.format.json_schema` with `strict: true` in Responses API

### Web Search
- Config: `web_search = "disabled" | "cached" | "live"`
- Flag: `--search` (enables live)
- SDK: `webSearchMode: "live"` in `ThreadOptions`

### Reasoning Control
- Config: `model_reasoning_effort = "minimal" | "low" | "medium" | "high" | "xhigh"`
- SDK: `modelReasoningEffort` in `ThreadOptions`
- App-server: `effort` in `TurnStartParams`

---

## Thread Persistence

- All sessions recorded as rollout files in `$CODEX_HOME/sessions/`
- `thread.id` is available after first turn starts (via `thread.started` event)
- Resume by thread ID: SDK `client.resumeThread(id)` or CLI `codex resume <id>`
- Fork: `thread/fork` creates new thread from existing rollout
- Rollback: `thread/rollback` drops N turns (does NOT revert file changes)

### Thread ID Capture (SDK)

```typescript
const thread = client.startThread({ ... });
const { events } = await thread.runStreamed("initial prompt");
for await (const event of events) {
  // thread.id is populated after thread.started event
}
const threadId = thread.id;  // persist this for resumption
```

---

## thegent Integration

### Current State

thegent integrates Codex via `codex exec --experimental-json` subprocess calls. Provider routing is done via `OPENAI_BASE_URL` pointing to CLIProxy.

### Correct Environment Variables

```python
env = {
    **os.environ,
    "OPENAI_BASE_URL": "http://localhost:8317/v1",  # CLIProxy
    "CODEX_API_KEY": proxy_api_key,                  # NOT OPENAI_API_KEY
}
```

Note: Codex reads `CODEX_API_KEY` (not `OPENAI_API_KEY`) as of the current version.

### Subprocess Invocation Pattern

```python
import asyncio
import json

async def invoke_codex_streamed(
    prompt: str,
    model: str = "gpt-5.1-codex-max",
    sandbox: str = "workspace-write",
    approval_policy: str = "never",
    working_dir: str | None = None,
    thread_id: str | None = None,
) -> AsyncGenerator[dict, None]:
    args = [
        "codex", "exec", "--experimental-json",
        "--sandbox", sandbox,
        "--ask-for-approval", approval_policy,
        "--skip-git-repo-check",
    ]
    if model:
        args.extend(["--model", model])
    if working_dir:
        args.extend(["--cd", working_dir])
    if thread_id:
        args.extend(["resume", thread_id])

    env = {
        **os.environ,
        "OPENAI_BASE_URL": "http://localhost:8317/v1",
        "CODEX_API_KEY": get_proxy_api_key(),
    }

    process = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    process.stdin.write(prompt.encode())
    process.stdin.close()

    async for line in process.stdout:
        line = line.decode().strip()
        if line:
            yield json.loads(line)

    await process.wait()
    if process.returncode != 0:
        stderr = await process.stderr.read()
        raise RuntimeError(f"Codex exited {process.returncode}: {stderr.decode()}")
```

### Recommended Overhaul Tiers

**Tier 1 — Config/Env (implement immediately):**
- Ensure `OPENAI_BASE_URL` + `CODEX_API_KEY` forwarded for proxy routing
- Map thegent model aliases to Codex `--model` values
- Expose sandbox and approval policy as thegent config
- Use `--config web_search=...` for web search toggle

**Tier 2 — TypeScript SDK wrapper (short term):**
- Thin Node.js wrapper using `@openai/codex-sdk`
- Thread persistence (store/restore `thread.id`)
- Structured output support via `outputSchema`
- Image input via `[{type:"local_image",path}]`
- Reasoning effort via `modelReasoningEffort`

**Tier 3 — App Server protocol client (medium term):**
- Full bidirectional JSON-RPC client
- Approval flows, dynamic tools, diff streaming
- TypeScript schema exports from protocol crate enable code generation

---

## Gaps vs Claude Code

| Feature | Codex | Claude Code |
|---------|-------|-------------|
| Structured JSON output | Yes (`output_schema`) | Yes |
| Image input | Yes (local + URL) | Yes |
| Programmatic SDK | Yes (`@openai/codex-sdk`) | No |
| Thread persistence/rollback | Yes (rollout files) | Yes |
| Multi-agent collab | Yes (`CollabAgentToolCall`) | No |
| App-server embedding protocol | Yes (JSON-RPC stdio) | No |
| MCP client | Yes | Yes |
| MCP server | Yes (2 tools, prototype) | No |
| Skills/extensions | Yes (SKILL.md) | Yes (CLAUDE.md) |
| Dynamic client tools | Yes | No |
| Code review mode | Yes (`review/start`) | No |
| Config layer system | Yes (MDM + system + user + project) | Limited |
| Model reasoning control | Yes (effort + summary + verbosity) | Yes |
| Context compaction | Yes (automated) | Yes |
| Approval flows | Yes (per-command, per-file) | Yes |
| Sandbox modes | Yes (read-only, workspace-write, full) | Limited |
| Provider routing | Only via proxy (`OPENAI_BASE_URL`) | No |

---

## Important Caveats

1. **Responses API only**: Codex is deeply coupled to the OpenAI Responses API. Any proxy must support it. Chat Completions is not sufficient.

2. **v1 protocol is deprecated**: Do not build against `newConversation`, `sendUserTurn`, or other v1 methods.

3. **UNSTABLE fields**: `chatgptAuthTokens` auth mode, `history` in `ThreadResumeParams`, `experimental_raw_events`, `CollaborationMode` — do not use in production integrations.

4. **MCP server is prototype**: The comment `//! Prototype MCP server.` signals not production-grade. Use App Server for serious integrations.

5. **Platform binary matrix**: SDK vendors platform-specific binaries for `x86_64-linux-musl`, `aarch64-linux-musl`, `x86_64-darwin`, `aarch64-darwin`, `x86_64-windows-msvc`, `aarch64-windows-msvc`.

6. **No computer use modality**: Codex does not have a `computer_use` tool. The "operator" positioning is marketing. Codex operates on files and shell only.

---

## Quick Reference

```bash
# Basic exec with proxy routing
OPENAI_BASE_URL=http://localhost:8317/v1 CODEX_API_KEY=key \
  codex exec --experimental-json --sandbox workspace-write \
  --ask-for-approval never --skip-git-repo-check \
  --model gpt-5.1-codex-max <<< "your prompt"

# Resume a thread
codex exec --experimental-json resume <thread-id> <<< "continue..."

# Config overrides
codex exec -c web_search="live" -c model_reasoning_effort="high" <<< "search and reason"

# With structured output
codex exec --experimental-json --output-schema ./schema.json <<< "extract data"

# MCP server mode (prototype)
codex mcp server   # JSONL stdin/stdout MCP protocol

# App Server mode (full protocol)
codex app-server   # JSONL stdin/stdout JSON-RPC-like protocol
```

```typescript
// SDK usage
import { Codex } from "@openai/codex-sdk";

const client = new Codex({ apiKey: "...", baseUrl: "http://localhost:8317/v1" });
const thread = client.startThread({
  model: "gpt-5.1-codex-max",
  sandboxMode: "workspace-write",
  approvalPolicy: "never",
  skipGitRepoCheck: true,
});
const turn = await thread.run("implement feature X");
console.log(turn.finalResponse);
// Persist thread.id for resumption
```

---

## Sources

- **Primary**: Direct source analysis of `/Users/kooshapari/temp-PRODVERCEL/485/API/codex-upstream/` (2026-02-20), specifically:
  - `codex-rs/app-server-protocol/src/protocol/v2.rs` — full v2 protocol types
  - `codex-rs/app-server-protocol/src/protocol/common.rs` — all method definitions
  - `codex-rs/app-server-protocol/src/jsonrpc_lite.rs` — wire format
  - `codex-rs/mcp-server/src/codex_tool_config.rs` — MCP tool schemas
  - `codex-rs/codex-api/src/requests/responses.rs` — Responses API request builder
  - `sdk/typescript/src/codex.ts`, `thread.ts`, `exec.ts`, `events.ts`, `items.ts`, `threadOptions.ts`
- Full research: `docs/research/CODEX_HARNESS_RESEARCH_2026-02-20.md`
