# Thegent FastMCP 3.0 Implementation Plan

Comprehensive plan for exposing thegent as a FastMCP 3.0 MCP server, leveraging all MCP/FastMCP features and paradigms.

---

## 1. Executive Summary

**Goal:** Expose thegent agent orchestration as a first-class MCP server so Cursor, Claude Code, Gemini CLI, and other MCP clients can invoke agents as tools. Use Streamable HTTP (not stdio) for long-running runs, progress streaming, and multi-client access.

**Scope:** Add FastMCP server alongside existing CLI; CLI remains primary for scripts; MCP is additive for IDE/agent integration.

---

## 2. MCP/FastMCP Feature Inventory

### 2.1 Components (What We Expose)

| Component | Purpose | thegent Mapping |
|-----------|---------|-----------------|
| **Tools** | Executable capabilities | run, bg, ps, status, logs, wait, stop, list-agents, list-droids, list-models, dag-list |
| **Resources** | Read-only data | Session logs, DAG session spec, agent config |
| **Prompts** | Parameterized templates | "Run agent X with prompt Y", "Create WBS for feature Z" |

### 2.2 FastMCP Paradigms to Leverage

| Paradigm | Use Case for thegent |
|----------|----------------------|
| **Progress** | `ctx.report_progress()` during long `run`; stream log tail |
| **Background Tasks** | `task=True` for `run`—client gets task ID, polls for result |
| **Context** | Logging, progress, session state (owner, cwd) |
| **Transforms** | Namespace (`thegent_*`) to avoid conflicts when composing servers |
| **Resources** | Session logs as `thegent://session/{id}/logs`; DAG as `thegent://dag` |
| **Prompts** | Pre-built "run agent" and "create WBS" templates |
| **Elicitation** | Ask for missing `--cd` or `--owner` when ambiguous |
| **Structured Output** | Return `ToolResult` with `structured_content` for session_id, status, etc. |
| **Tool Annotations** | `read_only`, `destructive`, `idempotent` hints |
| **Notifications** | `resources/list_changed` when sessions start/stop |

### 2.3 Transport: Streamable HTTP vs Stdio

| Aspect | Stdio | Streamable HTTP |
|--------|-------|-----------------|
| Long runs | Blocks; no progress | `ctx.report_progress()`; SSE polling; EventStore resumability |
| Log streaming | Pipe-based, single consumer | SSE stream; multiple subscribers |
| Multi-client | One process per client | Single server, many clients |
| Load balancer | N/A | SSE polling avoids idle timeouts (SEP-1699) |
| Deployment | Local/desktop only | Remote, centralized |

**Decision:** Streamable HTTP as default; stdio optional for local dev.

---

## 3. Component Design

### 3.1 Tools (Full Mapping)

| Tool | Args | Returns | Annotations | Task |
|------|------|---------|-------------|------|
| `thegent_run` | agent, prompt, cd?, mode?, timeout?, full?, model? | stdout/stderr summary | destructive | optional |
| `thegent_bg` | agent, prompt, cd?, mode?, timeout?, owner?, model? | session_id, log_path | destructive | forbidden |
| `thegent_ps` | owner?, all? | list of sessions | read_only, idempotent | forbidden |
| `thegent_status` | session_id | status, pid, owner | read_only, idempotent | forbidden |
| `thegent_logs` | session_id, tail?, stderr? | log content | read_only | forbidden |
| `thegent_wait` | session_id, timeout? | exit_code | read_only | optional |
| `thegent_stop` | session_id, force? | stopped | destructive | forbidden |
| `thegent_list_agents` | — | agent names + backends | read_only, idempotent | forbidden |
| `thegent_list_droids` | cd? | droid names | read_only, idempotent | forbidden |
| `thegent_list_models` | provider? | model list | read_only, idempotent | forbidden |
| `thegent_dag_list` | cd? | DAG tasks | read_only, idempotent | forbidden |
| `thegent_inspect` | session_ids?, owner?, tail?, stderr? | status+logs per session | read_only, idempotent | forbidden |

### 3.2 Resources

| URI | Template | Content | MIME |
|-----|----------|---------|------|
| `thegent://sessions` | — | List of sessions (JSON) | application/json |
| `thegent://session/{id}/meta` | {id} | Session metadata | application/json |
| `thegent://session/{id}/logs` | {id} | Stdout log tail | text/plain |
| `thegent://session/{id}/logs{?stderr,tail}` | {id}, stderr?, tail? | Logs with options | text/plain |
| `thegent://dag` | — | DAG session from .factory/dag-session.md | text/markdown |
| `thegent://agents` | — | Agent list | application/json |
| `thegent://models{?provider}` | provider? | Model list | application/json |

### 3.3 Prompts

| Prompt | Args | Returns |
|--------|------|---------|
| `thegent_run_agent` | agent, prompt, cd?, mode? | User message: "Run agent X with prompt Y" |
| `thegent_create_wbs` | feature, scope? | User message: "Create WBS for feature X" |
| `thegent_bg_task` | agent, prompt, owner? | User message: "Start background task with agent X" |

### 3.4 Transforms

- **Namespace:** `Namespace("thegent")` so tools appear as `thegent_run`, `thegent_bg`, etc. when composed with other servers.
- **Tool Transform:** Optional description overrides for agent-friendly docs.

### 3.5 Progress and Context

- **`thegent_run` (sync):** Run in threadpool; poll log file and call `ctx.report_progress(progress, total)` based on line count or time elapsed.
- **`thegent_run` (task=True):** Use `Progress` dependency; `set_total(timeout)`, `increment()` as work progresses; `set_message()` for status.
- **Logging:** `ctx.info()`, `ctx.debug()` for tool entry/exit; `ctx.error()` on failures.

### 3.6 Elicitation

- When `cd` is ambiguous (no .git, .factory, pyproject.toml): `ctx.elicit("Working directory?", response_type=str)`.
- When `owner` is needed for bg and not provided: `ctx.elicit("Session owner tag?", response_type=str)`.

---

## 4. Implementation Phases

### Phase 1: Minimal MCP Server (Core Tools)

**Goal:** Expose tools that wrap existing CLI commands; Streamable HTTP; no resources/prompts yet.

**Tasks:**
1. Add `fastmcp>=3.0.0rc1` as optional extra `mcp`.
2. Create `src/thegent/mcp_server.py`:
   - `FastMCP("thegent")`
   - Tools: `thegent_run`, `thegent_bg`, `thegent_ps`, `thegent_status`, `thegent_logs`, `thegent_wait`, `thegent_stop`, `thegent_list_agents`, `thegent_list_droids`, `thegent_list_models`, `thegent_dag_list`
   - Each tool calls internal helpers that return data (not print). Refactor `cli.py` to expose `*_impl` functions that return `str | dict` for MCP; keep `*_cmd` for CLI (print + typer.Exit).
3. Add `thegent serve` subcommand: `mcp.run(transport="http", host="127.0.0.1", port=8000)` or `mcp.http_app()`.
4. Config: `THGENT_MCP_PORT`, `THGENT_MCP_HOST`; default port 3847.

**Refactor:** Add `cli_impl.py` or internal helpers:
- `run_impl(...) -> dict` (stdout, stderr, exit_code, timed_out)
- `bg_impl(...) -> dict` (session_id, log_path, owner)
- `ps_impl(...) -> list[dict]`
- `status_impl(...) -> dict`
- `logs_impl(...) -> str`
- `wait_impl(...) -> int`
- `stop_impl(...) -> str`
- `list_agents_impl(...) -> list[dict]`
- `list_droids_impl(...) -> list[str]`
- `list_models_impl(...) -> dict[str, list[str]]`
- `dag_list_impl(...) -> dict`

**Deliverables:** `thegent serve`; MCP at `http://127.0.0.1:3847/mcp`; all tools callable from Cursor/Claude Code.

**CLI Single Source of Truth (prerequisite/maintenance):**
- Audit all thegent entry points: no Makefile targets, scripts, or docs wrap or bypass the CLI.
- Every capability must be reachable via `thegent <subcommand>`; no hidden features only in scripts.
- All docs use `thegent run`, `thegent bg`, etc. — never legacy `thegent <agent> <prompt>`.

---

### Phase 2: Resources and Prompts

**Goal:** Add resources and prompts for richer client integration.

**Tasks:**
1. Resources:
   - `thegent://sessions` — list sessions
   - `thegent://session/{id}/meta` — session metadata
   - `thegent://session/{id}/logs` — log content
   - `thegent://dag` — DAG session markdown
   - `thegent://agents` — agent list JSON
2. Prompts:
   - `thegent_run_agent`
   - `thegent_create_wbs`
   - `thegent_bg_task`
3. Add `Resources as Tools` transform if client is tool-only.

**Deliverables:** Clients can read session logs as resources; use prompts for guided workflows.

---

### Phase 3: Progress, Background Tasks, and Streaming

**Goal:** Long-running `thegent_run` reports progress; optional background task execution.

**Tasks:**
1. **Progress for `thegent_run`:**
   - Run agent in thread/process.
   - Poll log file or use callback from runner; call `ctx.report_progress(progress, total)`.
   - Total = timeout (seconds); progress = elapsed or log lines.
2. **Background Tasks:**
   - Add `fastmcp[tasks]` extra.
   - `@mcp.tool(task=TaskConfig(mode="optional"))` for `thegent_run`.
   - Async wrapper that delegates to sync `run_impl` via `asyncio.to_thread`.
3. **EventStore (optional):** For SSE polling on long runs; `ctx.close_sse_stream()` periodically to avoid LB timeouts.

**Deliverables:** Progress bar in clients; optional fire-and-forget `run` with task ID.

---

### Phase 4: Elicitation, Logging, and Polish

**Goal:** Interactive workflows; better observability.

**Tasks:**
1. **Elicitation:** When cwd/owner ambiguous, `ctx.elicit()`.
2. **Logging:** `ctx.info()`, `ctx.debug()`, `ctx.error()` in tools.
3. **Structured Output:** Return `ToolResult(content=..., structured_content={...})` for session_id, status, etc.
4. **Tool Annotations:** `read_only`, `destructive`, `idempotent` per tool.
5. **Health Route:** `@mcp.custom_route("/health")` for monitoring.

**Deliverables:** Interactive prompts when needed; structured responses; health check.

---

### Phase 5: Production Readiness

**Goal:** Auth, scaling, deployment.

**Tasks:**
1. **Auth:** Bearer token or OAuth for remote deployment.
2. **Stateless Mode:** `stateless_http=True` for horizontal scaling.
3. **Redis Backend:** `FASTMCP_DOCKET_URL=redis://...` for task persistence.
4. **Session State Store:** Redis for distributed session state.
5. **Documentation:** Cursor/Claude Code install instructions; `fastmcp install cursor` config.

**Deliverables:** Production deployment guide; auth; horizontal scaling.

---

## 5. File Structure

```
thegent/
├── pyproject.toml          # + mcp, mcp[tasks] extras
├── src/thegent/
│   ├── main.py             # + serve subcommand
│   ├── cli.py              # *_cmd (print); calls *_impl
│   ├── cli_impl.py         # NEW: *_impl (return data) for MCP
│   ├── mcp_server.py       # NEW: FastMCP server, tools, resources, prompts
│   └── ...
└── docs/plans/
    └── THGENT_FASTMCP_IMPLEMENTATION_PLAN.md  # this file
```

---

## 6. CLI vs MCP Coexistence

| Interface | Use Case |
|-----------|----------|
| **CLI** | Scripts, automation, direct human use, CI |
| **MCP** | Cursor, Claude Code, Gemini CLI, other MCP clients |

Both use the same core (`cli_impl`); no duplication of orchestration logic.

---

## 7. Dependencies

| Extra | Packages |
|-------|----------|
| (default) | typer, rich, pydantic, pydantic-settings, python-dotenv |
| mcp | fastmcp>=3.0.0rc1 |
| mcp[tasks] | fastmcp[tasks] (Docket for background tasks) |

---

## 8. Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| THGENT_MCP_HOST | 127.0.0.1 | Bind address |
| THGENT_MCP_PORT | 3847 | HTTP port |
| THGENT_MCP_PATH | /mcp | MCP endpoint path |
| FASTMCP_DOCKET_URL | memory:// | Task backend (memory or redis://) |

---

## 9. Verification

- [x] `thegent serve` starts; `http://127.0.0.1:3847/mcp` responds (Phase 1)
- [ ] Cursor MCP config: add thegent server; tools visible
- [ ] `thegent_run` with gemini/cursor-agent returns output
- [ ] `thegent_bg` returns session_id; `thegent_ps` lists it
- [ ] Progress updates during long `thegent_run` (Phase 3)
- [ ] Resources `thegent://session/{id}/logs` return log content (Phase 2)
- [ ] Prompts render correctly (Phase 2)

### 9.1 Verification Runbook

| Item | How to verify |
|------|---------------|
| Cursor MCP config | In Cursor: Settings → MCP → Add server. URL: `http://127.0.0.1:3847/mcp`. Restart Cursor; tools should appear. |
| `thegent_run` | From MCP client or CLI: call `thegent_run` with agent=gemini or cursor-agent, prompt="Hello". Expect stdout in result. |
| `thegent_bg` / `thegent_ps` | Call `thegent_bg` with agent, prompt; note session_id. Call `thegent_ps`; session should appear. |
| Progress updates | Run long `thegent_run`; check for progress notifications in MCP stream. |
| Resources | Call `thegent_bg`, get session_id. Read resource `thegent://session/{id}/logs`; expect log content. |
| Prompts | List prompts via MCP; render a prompt with args; verify output. |

---

## 10. Extended Feature Inventory (Research Deep Dive)

### 10.1 Storage Backends

| Backend | Use Case | thegent Applicability |
|---------|----------|------------------------|
| Memory | Default; dev | Session state, EventStore (single process) |
| Disk | Single-server prod | `DiskStore(directory="/var/cache/thegent")` for response cache |
| Redis | Multi-server, horizontal scaling | `RedisStore(host=...)` for EventStore, session_state, OAuth, Docket |

**Config:** `session_state_store`, `EventStore(storage=...)`, `ResponseCachingMiddleware(cache_storage=...)`, `FASTMCP_DOCKET_URL=redis://...`

### 10.2 Middleware (Built-in)

| Middleware | Purpose | thegent Use |
|------------|---------|-------------|
| `LoggingMiddleware` | Request/response logging | Observability |
| `StructuredLoggingMiddleware` | JSON logs for Datadog/Splunk | Production logging |
| `TimingMiddleware` | Execution duration | Per-request timing |
| `ResponseCachingMiddleware` | Cache tool/resource/prompt calls | Cache `thegent_ps`, `thegent_list_agents` (TTL) |
| `RateLimitingMiddleware` | Token bucket rate limit | Protect `thegent_run` from abuse |
| `ErrorHandlingMiddleware` | Centralized error logging | Production error handling |
| `PingMiddleware` | Keep connections alive | Long-lived HTTP sessions |
| `ResponseLimitingMiddleware` | Truncate large tool responses | Limit `thegent_logs` size |

**Order:** ErrorHandling → RateLimiting → Timing → Logging (first added = outermost).

### 10.3 Lifespan

```python
from fastmcp.server.lifespan import lifespan

@lifespan
async def thegent_lifespan(server):
    # Startup
    print("thegent MCP server starting")
    try:
        yield {"started_at": datetime.now(UTC).isoformat()}
    finally:
        # Teardown
        print("thegent MCP server shutting down")

mcp = FastMCP("thegent", lifespan=thegent_lifespan)
```

**Access in tools:** `ctx.lifespan_context["started_at"]`

### 10.4 Telemetry (OpenTelemetry)

- **Auto-instrumentation:** `opentelemetry-instrument fastmcp run mcp_server.py`
- **Spans:** `tools/call thegent_run`, `resources/read thegent://session/...`
- **Custom spans:** `get_tracer().start_as_current_span("parse_input")`
- **Attributes:** `mcp.method.name`, `mcp.session.id`, `fastmcp.component.type`

### 10.5 Pagination

- **Server:** `FastMCP("thegent", list_page_size=50)` — paginate tools/list, resources/list, prompts/list
- **When:** Many components (100+); thegent has ~11 tools, 5 resources, 3 prompts — optional
- **Client:** `list_tools_mcp(cursor=...)` for manual pagination

### 10.6 Versioning

- **Declare:** `@mcp.tool(version="1.0")` — clients see highest by default
- **Filter:** `VersionFilter(version_gte="2.0")` for API version surfaces
- **Request specific:** `call_tool("process", args, version="1.0")` or `_meta.fastmcp.version` in args

### 10.7 Dependency Injection

| Dependency | Purpose | thegent Use |
|------------|---------|-------------|
| `CurrentContext()` | ctx for logging, progress, elicitation | All tools |
| `Depends(get_default_cwd)` | Inject cwd from request meta | Hide from LLM schema |
| `CurrentHeaders()` | HTTP headers (x-user-id, etc.) | Optional auth |
| `CurrentRequest()` | Full Starlette Request | Client IP, user-agent |
| `Progress()` | Task progress (task=True only) | thegent_run background |

### 10.8 Sampling (ctx.sample)

- **Use case:** Tool requests LLM generation (e.g. "suggest prompt" tool)
- **API:** `result = await ctx.sample("Analyze this", result_type=SentimentResult)`
- **Fallback:** `sampling_handler=OpenAISamplingHandler(...)` when client lacks sampling
- **thegent fit:** Optional `thegent_suggest_prompt` tool that uses sampling to refine user prompt

### 10.9 EventStore (SSE Polling)

- **Location:** `fastmcp.server.event_store.EventStore`
- **Usage:** `app = mcp.http_app(event_store=EventStore(), retry_interval=2000)`
- **Storage:** `EventStore(storage=RedisStore(...))` for distributed; defaults to `MemoryStore`
- **Params:** `max_events_per_stream=100`, `ttl=3600` (seconds)
- **In tool:** `await ctx.close_sse_stream()` periodically during long run — client reconnects with `Last-Event-ID`
- **Redis:** `from key_value.aio.stores.redis import RedisStore; EventStore(storage=RedisStore(url="redis://localhost"))`

### 10.10 Tool Injection Middleware

- `PromptToolMiddleware` — expose prompts as tools (alternative to PromptsAsTools transform)
- `ResourceToolMiddleware` — expose resources as tools (alternative to ResourcesAsTools transform)
- Use when transforms don't fit (e.g. per-request injection)

---

## 11. Additional Research Tasks (thegent cursor)

```bash
# Storage + EventStore
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/storage-backends and fastmcp/server/event_store.py. Extract: (a) RedisStore, DiskStore usage, (b) EventStore(storage=), (c) FernetEncryptionWrapper for OAuth. Output to docs/research/FASTMCP_STORAGE_EVENTSTORE.md"

# Middleware pipeline
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/middleware. Extract: (a) add_middleware order, (b) ResponseCachingMiddleware with CallToolSettings, (c) RateLimitingMiddleware params, (d) on_call_tool hook for thegent_run. Output to docs/research/FASTMCP_MIDDLEWARE.md"

# Sampling + Telemetry
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/sampling and servers/telemetry. Extract: (a) ctx.sample with result_type, (b) get_tracer(), (c) opentelemetry-instrument. Output to docs/research/FASTMCP_SAMPLING_TELEMETRY.md"
```

---

## 12. Phase 6: Production Middleware and Storage

**Goal:** Production-grade observability, caching, rate limiting.

**Tasks:**
1. Add `TimingMiddleware` and `LoggingMiddleware` (or `StructuredLoggingMiddleware`).
2. Add `ResponseCachingMiddleware` for `thegent_ps`, `thegent_list_agents`, `thegent_list_droids`, `thegent_list_models` with TTL 30s.
3. Add `RateLimitingMiddleware(max_requests_per_second=10, burst_capacity=20)` — protect from runaway thegent_run.
4. Add `ResponseLimitingMiddleware(max_size=500_000)` for `thegent_logs` to avoid context overflow.
5. Optional: `DiskStore` or `RedisStore` for cache when `THGENT_CACHE_STORAGE` set.

---

## 13. Phase 7: Sampling and Advanced Context

**Goal:** LLM-assisted tools; richer context.

**Tasks:**
1. Add `thegent_suggest_prompt` tool: takes raw prompt, uses `ctx.sample()` to refine it, returns suggested prompt.
2. Configure `sampling_handler` (OpenAI/Anthropic) as fallback when client lacks sampling.
3. Use `Depends(get_default_cwd)` for tools that accept optional cd — inject from `ctx.request_context.meta`.

---

## 14. Design Excellence: Optimization, Polish, Robustness

Design principles for maximally engineered, intuitive, and production-grade behavior.

### 14.1 Optimization

| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Latency** | Cache read-heavy tools; lazy-load expensive data | `ResponseCachingMiddleware` for `thegent_ps`, `list_agents`, `list_models`; TTL 30s; cache key = `(tool, owner, all)` |
| **Throughput** | Avoid blocking; parallelize where safe | `asyncio.to_thread(run_impl)` for sync run; no blocking in event loop |
| **Memory** | Bound response size; stream large outputs | `ResponseLimitingMiddleware(max_size=500_000)`; `thegent_logs` with `tail=N` default (e.g. 100 lines) |
| **Connection reuse** | Keep-alive; avoid connection churn | Default HTTP keep-alive; `PingMiddleware` for long SSE sessions |
| **Idempotency** | Safe retries for read-only tools | `idempotent` annotation on ps, status, logs, list_*; clients can retry without side effects |
| **Batch hints** | Reduce round-trips | `thegent_ps` returns full session list; client filters client-side; avoid N+1 status calls |

### 14.2 Polish

| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Tool descriptions** | Agent-optimized; action-oriented | "Run agent X with prompt Y. Returns stdout/stderr. Use cd for project dir." — not "Executes run command" |
| **Parameter docs** | Clear defaults, units, constraints | `timeout`: "Seconds. Default 300. Max 3600."; `tail`: "Lines. Default 100. Max 10000." |
| **Error messages** | Actionable; include remediation | `"Session abc not found. Use thegent_ps to list sessions or thegent_bg to start one."` |
| **Response shape** | Consistent; machine-parseable | All tools return `ToolResult` with `structured_content` + `content` (human-readable); `meta.execution_time_ms` |
| **Naming** | Consistent; predictable | `session_id` everywhere (not `id`/`sid`); `cd` for cwd; `owner` for session owner tag |
| **Enums** | Expose valid values in schema | `mode`: `["sync","bg"]`; `provider`: from `list_models` keys |

### 14.3 Enhancement

| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Observability** | Structured logs; spans; metrics | `ctx.info("thegent_run", agent=agent, cd=cd)`; OpenTelemetry span per tool; `execution_time_ms` in meta |
| **Extensibility** | Hooks for custom behavior | `on_before_run`, `on_after_run` callbacks (if FastMCP supports); or middleware `on_call_tool` |
| **Discoverability** | Self-documenting; versioned | `thegent://meta` resource with server version, capabilities; `version="1.0"` on tools |
| **Composability** | Namespace; no collisions | `Namespace("thegent")`; all URIs `thegent://`; prompts `thegent_*` |
| **Graceful degradation** | Fallbacks when optional deps missing | No sampling? Return raw prompt; no Redis? Use memory EventStore; log warning, don't fail |
| **Progressive enhancement** | Core works; extras optional | Core tools work without tasks, elicitation, EventStore; add when configured |

### 14.4 Robustness

| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Timeouts** | Per-tool; per-request; fail-fast | `thegent_run`: `timeout` param (default 300s); `thegent_wait`: `timeout` param; HTTP request timeout > max tool timeout |
| **Retries** | Exponential backoff for transient failures | CLI impl retries subprocess spawn (1 retry, 2s delay); MCP layer: no retry (client responsibility) |
| **Input validation** | Strict; reject invalid early | `session_id`: non-empty, format check; `agent`: must exist in list_agents; `cd`: path exists or elicitation |
| **Resource limits** | Prevent runaway consumption | Rate limit `thegent_run` (2 concurrent per client?); max `tail` 10000; max `timeout` 3600 |
| **Error boundaries** | Catch, log, return structured error | `ToolError` for session-not-found; generic 500 → `{"error":"internal","message":"..."}`; never leak stack traces |
| **Cleanup** | Orphan prevention; TTL | Session logs TTL; EventStore `ttl=3600`; Docket task retention |
| **Concurrency safety** | No shared mutable state races | Session state in process-local dict or Redis; no global mutable caches without locking |
| **Graceful shutdown** | Drain in-flight; no orphan tasks | Lifespan teardown: stop accepting new runs; wait for active runs up to 30s; then exit |
| **Backpressure** | Limit concurrent heavy operations | Max N concurrent `thegent_run` per server; queue or reject excess with 503 + Retry-After |
| **Strict validation** | Reject malformed input at schema level | `strict_input_validation=True` for production; Pydantic models for tool args where beneficial |

### 14.5 Intuitive + Practical

| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Defaults** | Sensible for 80% case | `cd` = cwd; `owner` = "default"; `timeout` = 300; `tail` = 100; `mode` = sync |
| **Fail-fast** | Surface errors immediately | Invalid agent → error before spawn; missing session → error with hint |
| **Predictability** | Same input → same output (read-only) | `thegent_ps` with same args → deterministic order; cache invalidates on session change |
| **Discoverability** | Easy to explore | `thegent_list_agents` → use in run; `thegent_ps` → use session_id in status/logs/wait/stop |
| **Composability** | Works with other MCP servers | No global state; namespace avoids conflicts; resources/prompts as tools for tool-only clients |
| **Developer ergonomics** | Easy to debug | `ctx.debug()` on entry; `execution_time_ms` in response; health route with version |

### 14.6 Optimal Design Principles

| Principle | Application |
|-----------|-------------|
| **Single source of truth** | `cli_impl` is canonical; CLI and MCP both call it; no duplicated logic |
| **Separation of concerns** | MCP layer: transport, progress, elicitation; impl layer: business logic, subprocess, files |
| **Explicit over implicit** | `cd` passed explicitly or elicited; no magic env vars; config via env with docs |
| **Fail loudly** | Required deps missing → startup failure; invalid input → ToolError with message |
| **Minimal surface area** | Expose only what clients need; hide implementation details in resources |
| **Backward compatibility** | Version tools; `VersionFilter` for API surfaces; deprecate, don't remove |
| **Testability** | `*_impl` pure functions; inject cwd, owner; mock subprocess for unit tests |
| **Observability first** | Logging, tracing, metrics from day one; not bolted on later |

### 14.7 SLOs and Performance Budgets (Target)

| Metric | Target | Notes |
|--------|--------|-------|
| `thegent_ps` p50 | < 50ms | Cached; in-memory session list |
| `thegent_status` p50 | < 20ms | Single session lookup |
| `thegent_run` | User-controlled | Progress reported; timeout enforced |
| `thegent_logs` p95 | < 200ms | Bounded by `tail`; stream if very large |
| Health check | < 10ms | No DB; simple 200 |
| Tool list (tools/list) | < 100ms | 11 tools; no pagination needed |

### 14.8 Icons and UX Hints (Optional)

| Tool | Icon / Hint | Purpose |
|------|-------------|---------|
| `thegent_run` | `▶` or "play" | Indicates execution |
| `thegent_bg` | `⏸` or "background" | Fire-and-forget |
| `thegent_stop` | `⏹` or "stop" | Destructive; confirm in UI |
| `thegent_logs` | `📄` or "logs" | Read-only output |
| `thegent_ps` | `📋` or "list" | Discovery |

Use `icons=[...]` on tools when FastMCP supports; improves client UI discoverability.

### 14.9 Testing Strategy for Robustness

| Test Type | Scope | Examples |
|-----------|-------|----------|
| **Unit** | `*_impl` in isolation | Mock subprocess; assert return shape; invalid input → error |
| **Contract** | MCP schema stability | Tools list matches expected; params have correct types |
| **Integration** | Full MCP server | `thegent serve` + client; run → status → logs → stop |
| **Chaos** | Failure injection | Kill subprocess mid-run; assert clean error; reconnect after EventStore |
| **Load** | Rate limit, concurrency | N parallel runs; assert rate limit kicks in; no deadlock |
| **Timeout** | Long operations | Run with 5s timeout; assert exit; wait with 1s timeout; assert timeout error |

### 14.10 Anti-Patterns to Avoid

| Anti-pattern | Instead |
|--------------|---------|
| Silent failure when optional dep missing | Log warning; degrade gracefully; document in response |
| Blocking sync in async tool | `asyncio.to_thread(sync_fn)` |
| Generic "Error" message | Specific: "Session xyz not found. Use thegent_ps to list." |
| Exposing implementation details in errors | User-facing message; details in logs only |
| Global mutable cache without TTL | Bounded cache with invalidation or TTL |
| Duplicating logic between CLI and MCP | Single `*_impl`; both call it |
| Magic defaults (implicit cwd from unknown source) | Explicit param or elicitation |
| Unbounded `tail` or `timeout` | Cap with sensible max; document in schema |

### 14.11 Checklist: Before Each Phase

- [ ] Error messages include remediation hint
- [ ] Tool descriptions updated for agent consumption
- [ ] `ToolResult` with `structured_content` + `meta.execution_time_ms`
- [ ] Input validation at boundary; reject invalid early
- [ ] `ctx.info` on entry, `ctx.error` on failure
- [ ] No blocking in async tools; use `to_thread` for sync impl
- [ ] Rate limit and response limit considered for new tools
- [ ] Graceful degradation path for optional features (sampling, Redis)

---

## 15. Thegent Implementation Monitoring

### Monitor Prior/Active Sessions

```bash
# Inspect multiple sessions (status + logs) — no shell loop needed
thegent inspect <sid1> <sid2> <sid3> --tail 50

# Inspect all sessions for an owner
thegent inspect --owner fastmcp-p3b --tail 50

# List all sessions (including exited)
thegent ps --all

# Filter by owner
thegent ps --owner=fastmcp-p3b
thegent ps --owner=kooshapari:thegent

# Check status of specific session
thegent status <session_id>

# View logs (last 50 lines)
thegent logs <session_id> --tail 50

# Follow logs live
thegent logs <session_id> --follow
```

**MCP:** Use `thegent_inspect` tool with `session_ids` or `owner` for batch status+logs.

### Spawned Sessions (Implementation Agents)

| Phase | Session ID | Owner | Status | Notes |
|-------|------------|-------|--------|-------|
| 3A | 20260214T140659Z-copilot-p89542-7b1b2010 | kooshapari:thegent | exited | thegent_run async + progress + TaskConfig |
| 3C | 20260214T140659Z-copilot-p89604-992ab1bb | kooshapari:thegent | exited | ToolResult for bg, status, wait, stop |
| 3D | 20260214T140700Z-copilot-p89726-e962c049 | kooshapari:thegent | exited | ResourcesAsTools, PromptsAsTools |
| 3B | 20260214T141123Z-cursor-p91109-12d376df | fastmcp-p3b | exited | Elicitation |
| 4A | 20260214T141123Z-cursor-p91320-2b55bb6a | fastmcp-p4a | exited | EventStore + SSE polling |
| 4C | 20260214T141124Z-cursor-p91512-73ddddc9 | fastmcp-p4c | exited | Lifespan |
| 4B, 4log, 6, 7, pns | — | — | direct impl | Agent spawns failed (cursor/copilot/glm args); implemented directly |

### Phase 6–7 Direct Implementation (2026-02-14)

| Item | Status |
|------|--------|
| Middleware (ErrorHandling, RateLimiting, Timing, ResponseCaching, ResponseLimiting, Logging) | Done |
| thegent://models{?provider} resource | Done |
| thegent://meta resource | Done |
| thegent_suggest_prompt (ctx.sample) | Done |
| ctx.info / _log.info in tools | Done |
| close_sse_stream in thegent_run (every 30s) | Done (already present) |

### Spawn Commands (Reference)

```bash
# Phase 3B Elicitation
thegent bg cursor-agent -d <cwd> --owner=fastmcp-p3b "Phase 3B Elicitation: ..."

# Phase 4A EventStore
thegent bg cursor-agent -d <cwd> --owner=fastmcp-p4a "Phase 4A EventStore: ..."

# Phase 4C Lifespan
thegent bg cursor-agent -d <cwd> --owner=fastmcp-p4c "Phase 4C Lifespan: ..."
```

### Post-Spawn Verification

1. `thegent ps --owner=fastmcp-p3b` — confirm session running
2. `thegent logs <sid> --tail 100` — inspect progress
3. `thegent wait <sid>` — block until done (optional)
4. After exit: review logs for summary; verify mcp_server.py changes

---

## 16. References (Extended)

- [FastMCP 3.0 Docs](https://gofastmcp.com)
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP HTTP Deployment](https://gofastmcp.com/deployment/http)
- [FastMCP Progress](https://gofastmcp.com/servers/progress)
- [FastMCP Background Tasks](https://gofastmcp.com/servers/tasks)
- [FastMCP Context](https://gofastmcp.com/servers/context)
- [FastMCP Resources](https://gofastmcp.com/servers/resources)
- [FastMCP Prompts](https://gofastmcp.com/servers/prompts)
- [FastMCP Elicitation](https://gofastmcp.com/servers/elicitation)
- [FastMCP Storage Backends](https://gofastmcp.com/servers/storage-backends)
- [FastMCP Middleware](https://gofastmcp.com/servers/middleware)
- [FastMCP Lifespan](https://gofastmcp.com/servers/lifespan)
- [FastMCP Telemetry](https://gofastmcp.com/servers/telemetry)
- [FastMCP Pagination](https://gofastmcp.com/servers/pagination)
- [FastMCP Versioning](https://gofastmcp.com/servers/versioning)
- [FastMCP Dependency Injection](https://gofastmcp.com/servers/dependency-injection)
- [FastMCP Sampling](https://gofastmcp.com/servers/sampling)
