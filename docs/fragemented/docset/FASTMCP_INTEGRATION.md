# FastMCP 3.0 Integration Reference for Thegent

**Date:** 2026-02-14
**Purpose:** Consolidated reference for FastMCP integration in thegent MCP server. Covers API usage, configuration, middleware, storage, telemetry, and deployment.
**Source:** Extracted from FastMCP 3.0 docs, gofastmcp.com, and thegent planning docs.

---

## Table of Contents

1. [Context API Usage Map](#1-context-api-usage-map)
2. [Middleware Stack](#2-middleware-stack)
3. [Storage Backends](#3-storage-backends)
4. [Telemetry Integration](#4-telemetry-integration)
5. [Elicitation Patterns](#5-elicitation-patterns)
6. [Task Management](#6-task-management)
7. [Deployment Configuration](#7-deployment-configuration)
8. [Verification Checklist](#8-verification-checklist)

---

## 1. Context API Usage Map

The `Context` object (`ctx`) is injected via `CurrentContext()` dependency or passed to tools. It provides logging, progress, elicitation, sampling, and stream management.

### 1.1 Core API Methods

| Method | Signature | Purpose | Thegent Use |
|--------|-----------|---------|-------------|
| `ctx.elicit()` | `async def elicit(message: str, response_type: type[T] \| list[str] \| dict \| None) -> AcceptedElicitation[T] \| DeclinedElicitation \| CancelledElicitation` | Request user input; awaits client response | Ask for cwd, owner when ambiguous |
| `ctx.info()` | `async def info(message: str, logger_name: str \| None = None, extra: Mapping = None) -> None` | Send INFO level log | Tool entry/exit logging |
| `ctx.debug()` | `async def debug(message: str, logger_name: str \| None = None, extra: Mapping = None) -> None` | Send DEBUG level log | Internal operations, troubleshooting |
| `ctx.warning()` | `async def warning(message: str, logger_name: str \| None = None, extra: Mapping = None) -> None` | Send WARNING level log | Degraded mode (missing optional deps) |
| `ctx.error()` | `async def error(message: str, logger_name: str \| None = None, extra: Mapping = None) -> None` | Send ERROR level log | Exceptions, validation failures |
| `ctx.report_progress()` | `async def report_progress(progress: float, total: float \| None = None, message: str \| None = None) -> None` | Update progress for client | Track thegent_run execution progress |
| `ctx.sample()` | `async def sample(messages: str, result_type: type[T] \| None = None) -> SamplingResult[T]` | Request LLM generation (client or fallback) | thegent_suggest_prompt tool |
| `ctx.close_sse_stream()` | `async def close_sse_stream() -> None` | Close HTTP response for reconnect (SSE only) | Avoid LB timeouts during long runs every ~30s |

### 1.2 Response Types for `ctx.elicit()`

**When to use each:**

| Scenario | response_type | Example | Return Type |
|----------|---------------|---------|-------------|
| Free-form string | `str` | `ctx.elicit("Working directory?", response_type=str)` | `AcceptedElicitation[str]` with `.data: str` |
| Single-select (list) | `list[str]` | `ctx.elicit("Mode?", response_type=["sync", "bg"])` | `AcceptedElicitation[str]` with selected value |
| Single-select (dict) | `dict[str, dict[str, str]]` | `{"sync": {"title": "Synchronous"}, ...}` | `AcceptedElicitation[str]` with key |
| Multi-select (list) | `list[list[str]]` | `ctx.elicit("Options?", response_type=[["opt1", "opt2"]])` | `AcceptedElicitation[list[str]]` |
| Multi-select (dict) | `list[dict[str, dict[str, str]]]` | `[{"a": {"title": "Option A"}}, ...]` | `AcceptedElicitation[list[str]]` |
| Pydantic model | `type[MyModel]` | `ctx.elicit("Config?", response_type=RunConfig)` | `AcceptedElicitation[RunConfig]` |
| No response needed | `None` | `ctx.elicit("Press OK to continue", response_type=None)` | `AcceptedElicitation[dict]` (empty dict) |

**Handling responses:**

```python
result = await ctx.elicit("Working directory?", response_type=str)
if isinstance(result, AcceptedElicitation):
    cwd = result.data  # User accepted; use data
elif isinstance(result, DeclinedElicitation):
    # User declined; use default or raise ToolError
    cwd = os.getcwd()
elif isinstance(result, CancelledElicitation):
    # User cancelled; raise ToolError
    raise ToolError("User cancelled cwd input")
```

### 1.3 Logging Injection in Tools

```python
from fastmcp.dependencies import CurrentContext

@mcp.tool()
async def thegent_run(agent: str, prompt: str, cd: str | None = None, ctx: Context = CurrentContext()) -> ToolResult:
    await ctx.info(f"Running agent={agent}, cd={cd}")
    try:
        result = await run_impl(agent, prompt, cd)
        await ctx.info(f"Agent completed with exit code {result['exit_code']}")
        return ToolResult(content=result['stdout'])
    except Exception as e:
        await ctx.error(f"Agent failed: {e}")
        raise ToolError(str(e))
```

### 1.4 Dependency Injection with CurrentContext

```python
from fastmcp.dependencies import CurrentContext, Progress

@mcp.tool(task=TaskConfig(mode="optional"))
async def thegent_run(
    agent: str,
    prompt: str,
    cd: str | None = None,
    ctx: Context = CurrentContext(),
    progress: ProgressLike = Progress()
) -> ToolResult:
    # ctx and progress are automatically injected
    await progress.set_total(timeout)
    for i in range(steps):
        await progress.increment()
        await ctx.report_progress(i, steps, f"Step {i}/{steps}")
    return result
```

---

## 2. Middleware Stack

Middleware processes requests in **order added** (first added = outermost, runs first).

### 2.1 Recommended Stack for Thegent

**Order of addition (outermost first):**

```python
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.caching import ResponseCachingMiddleware, CallToolSettings, ListToolsSettings
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware

# 1. Error handling (outer; catches all errors)
mcp.add_middleware(ErrorHandlingMiddleware())

# 2. Rate limiting (protect from abuse)
mcp.add_middleware(RateLimitingMiddleware(
    max_requests_per_second=10.0,
    burst_capacity=20
))

# 3. Timing (measure execution)
mcp.add_middleware(TimingMiddleware())

# 4. Response caching (cache read-heavy ops)
mcp.add_middleware(ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="/var/cache/thegent") if use_disk else None,
    list_tools_settings=ListToolsSettings(ttl=30),
    call_tool_settings=CallToolSettings(
        included_tools=["thegent_ps", "thegent_list_agents", "thegent_list_droids", "thegent_list_models"],
        ttl=30
    )
))

# 5. Response limiting (bound size for thegent_logs)
mcp.add_middleware(ResponseLimitingMiddleware(
    max_size=500_000,
    tools=["thegent_logs"]  # Limit only these tools
))

# 6. Logging (innermost; logs all requests)
mcp.add_middleware(LoggingMiddleware())
```

### 2.2 Middleware Details

#### ErrorHandlingMiddleware

Centralized error logging and structured error responses.

```python
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

mcp.add_middleware(ErrorHandlingMiddleware())
```

**Behavior:** Catches exceptions in tools; logs with context; returns structured error.

---

#### RateLimitingMiddleware

Token bucket rate limiter; protects `thegent_run` from abuse.

```python
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

mcp.add_middleware(RateLimitingMiddleware(
    max_requests_per_second=10.0,  # Sustained rate
    burst_capacity=20              # Max burst
))
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_requests_per_second | float | 10.0 | Sustained request rate |
| burst_capacity | int | 20 | Maximum burst size |
| client_id_func | Callable | None | Custom client identification (e.g., from headers) |

**Thegent:** `max_requests_per_second=10, burst_capacity=20` limits parallel runs to ~2–3 concurrent operations.

---

#### TimingMiddleware

Measures execution duration per request.

```python
from fastmcp.server.middleware.timing import TimingMiddleware

mcp.add_middleware(TimingMiddleware())
```

**Output:** Adds `execution_time_ms` to response meta.

---

#### ResponseCachingMiddleware

Caches tool, resource, and prompt responses.

```python
from fastmcp.server.middleware.caching import (
    ResponseCachingMiddleware,
    CallToolSettings,
    ListToolsSettings,
    ReadResourceSettings,
    ListResourcesSettings,
    ListPromptsSettings,
    GetPromptSettings
)
from key_value.aio.stores.disk import DiskStore
from key_value.aio.stores.memory import MemoryStore

# Development (in-memory)
mcp.add_middleware(ResponseCachingMiddleware(
    list_tools_settings=ListToolsSettings(ttl=30),
    call_tool_settings=CallToolSettings(
        included_tools=["thegent_ps", "thegent_list_agents", "thegent_list_droids", "thegent_list_models"],
        ttl=30
    ),
    read_resource_settings=ReadResourceSettings(
        included_resources=["thegent://sessions", "thegent://agents"],
        ttl=30
    )
))

# Production (with disk/redis storage)
mcp.add_middleware(ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="/var/cache/thegent"),
    list_tools_settings=ListToolsSettings(ttl=30),
    call_tool_settings=CallToolSettings(
        included_tools=["thegent_ps", "thegent_list_agents"],
        ttl=30
    )
))
```

**Settings classes:**

| Class | Configures | Keys |
|-------|-----------|------|
| ListToolsSettings | tools/list caching | `ttl`, `enabled` |
| CallToolSettings | tools/call caching | `included_tools`, `excluded_tools`, `ttl`, `enabled` |
| ListResourcesSettings | resources/list caching | `included_resources`, `excluded_resources`, `ttl`, `enabled` |
| ReadResourceSettings | resources/read caching | `included_resources`, `excluded_resources`, `ttl`, `enabled` |
| ListPromptsSettings | prompts/list caching | `ttl`, `enabled` |
| GetPromptSettings | prompts/get caching | `included_prompts`, `excluded_prompts`, `ttl`, `enabled` |

**Thegent application:**

- **Read-heavy tools** (thegent_ps, thegent_list_agents, etc.) with `ttl=30`
- **Resources** (thegent://sessions, thegent://agents) with `ttl=30`
- **Storage:** DiskStore for single-server, RedisStore for distributed

---

#### ResponseLimitingMiddleware

Truncates responses exceeding max size (prevents context overflow).

```python
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

mcp.add_middleware(ResponseLimitingMiddleware(
    max_size=500_000,           # Max response size in bytes
    tools=["thegent_logs"]      # Limit only these tools
))
```

**Thegent:** Limit `thegent_logs` to prevent OOM when tail is large.

---

#### LoggingMiddleware

Request/response logging (text) or StructuredLoggingMiddleware (JSON for Datadog/Splunk).

```python
from fastmcp.server.middleware.logging import LoggingMiddleware, StructuredLoggingMiddleware

# Text logs (development)
mcp.add_middleware(LoggingMiddleware())

# JSON logs (production)
mcp.add_middleware(StructuredLoggingMiddleware())
```

### 2.3 on_call_tool Hook

Use middleware or custom handler to intercept tool calls:

```python
from fastmcp.server.middleware import MiddlewareContext

class CustomToolMiddleware:
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments

        # Log before call
        print(f"Calling {tool_name} with {args}")

        # Call next middleware
        result = await call_next(context)

        # Log after call
        print(f"Result: {result}")

        return result

mcp.add_middleware(CustomToolMiddleware())
```

**MiddlewareContext attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| method | str | MCP method (e.g., "tools/call") |
| message.name | str | Tool name |
| message.arguments | dict | Tool arguments |
| fastmcp_context | Context | FastMCP context (if available) |

---

## 3. Storage Backends

FastMCP uses pluggable storage for caching, OAuth state, and event store.

### 3.1 Backend Options

#### MemoryStore (Default)

In-process, in-memory store.

```python
from key_value.aio.stores.memory import MemoryStore

store = MemoryStore()
```

**Use:** Development, single-process, data OK to lose on restart.

---

#### DiskStore

File-based persistent store (single server).

```python
from key_value.aio.stores.disk import DiskStore

store = DiskStore(directory="/var/cache/thegent")
```

**Use:** Single-server production, data persists across restarts.

**Setup:**

```bash
mkdir -p /var/cache/thegent /var/lib/thegent/oauth
chmod 700 /var/cache/thegent /var/lib/thegent/oauth
```

---

#### RedisStore

Distributed persistent store (multi-server, horizontal scaling).

```python
from key_value.aio.stores.redis import RedisStore

store = RedisStore(
    host="redis.example.com",
    port=6379,
    password="your-redis-password"  # Optional
)

# Or URL format
store = RedisStore(url="redis://:password@redis.example.com:6379")
```

**Use:** Multi-server production, distributed cache, horizontal scaling.

**Install:** `pip install 'py-key-value-aio[redis]'`

---

#### FernetEncryptionWrapper (OAuth)

Encrypts sensitive data (e.g., OAuth tokens) before storage.

```python
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from cryptography.fernet import Fernet

key = os.environ["STORAGE_ENCRYPTION_KEY"]  # Base64-encoded key
encrypted_store = FernetEncryptionWrapper(
    key_value=RedisStore(url="redis://..."),
    fernet=Fernet(key.encode())
)
```

**Generate key:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Use:** Production OAuth with tokens; required for security.

---

#### PrefixCollectionsWrapper (Multi-tenant)

Namespaces keys in shared storage.

```python
from key_value.aio.wrappers.prefix_collections import PrefixCollectionsWrapper

base_store = RedisStore(url="redis://...")
namespaced = PrefixCollectionsWrapper(
    key_value=base_store,
    prefix="thegent"  # All keys prefixed with "thegent:"
)
```

**Use:** Multi-tenant deployments to avoid key collisions.

---

### 3.2 Thegent Storage Configuration

| Use Case | Backend | Config | Environment |
|----------|---------|--------|-------------|
| Response cache (ps, list_agents) | DiskStore or RedisStore | `cache_storage=DiskStore(...)` | `THGENT_CACHE_STORAGE=disk:/var/cache/thegent` |
| EventStore (SSE polling for long runs) | MemoryStore or RedisStore | `EventStore(storage=...)` | `FASTMCP_EVENTSTORE=redis://...` |
| OAuth tokens (if added) | RedisStore + FernetEncryptionWrapper | `client_storage=FernetEncryptionWrapper(...)` | `STORAGE_ENCRYPTION_KEY=...` |
| Docket tasks (background) | Redis | Task backend | `FASTMCP_DOCKET_URL=redis://...` |

**Environment Variables:**

```bash
# Storage backend
export THGENT_CACHE_STORAGE=memory                      # Default: in-memory
export THGENT_CACHE_STORAGE=disk:/var/cache/thegent    # Persistent
export THGENT_CACHE_STORAGE=redis://localhost:6379     # Distributed

# EventStore (SSE polling)
export FASTMCP_EVENTSTORE=memory                        # Default
export FASTMCP_EVENTSTORE=redis://localhost:6379       # Distributed

# Task backend (Docket)
export FASTMCP_DOCKET_URL=memory://                     # Default
export FASTMCP_DOCKET_URL=redis://localhost:6379       # Distributed

# OAuth encryption (if added)
export STORAGE_ENCRYPTION_KEY=<base64-encoded-fernet-key>
```

---

## 4. Telemetry Integration

FastMCP exposes OpenTelemetry (OTel) integration for tracing, metrics, and logging.

### 4.1 Tracing with get_tracer()

```python
from fastmcp.telemetry import get_tracer
from opentelemetry.trace import Status, StatusCode

@mcp.tool()
async def thegent_run(agent: str, prompt: str) -> ToolResult:
    tracer = get_tracer()

    # Create span for parse phase
    with tracer.start_as_current_span("parse_input") as span:
        span.set_attribute("input.length", len(prompt))
        span.set_attribute("agent", agent)
        parsed = parse_prompt(prompt)

    # Create span for execution
    with tracer.start_as_current_span("execute_agent") as span:
        span.set_attribute("agent.name", agent)
        try:
            result = await run_impl(agent, prompt)
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("error.type", type(e).__name__)
            raise

    return ToolResult(content=result['stdout'])
```

### 4.2 Auto-Instrumented Spans

FastMCP automatically creates spans for:

| Span Name | Type | Attributes |
|-----------|------|------------|
| `tools/call {name}` | Automatic | `mcp.method.name=tools/call`, `mcp.session.id=...`, `fastmcp.component.type=tool`, `fastmcp.component.key=tool:{name}` |
| `resources/read {uri}` | Automatic | `mcp.method.name=resources/read`, `fastmcp.component.type=resource`, `fastmcp.component.key=resource:{uri}` |
| `prompts/get {name}` | Automatic | `mcp.method.name=prompts/get`, `fastmcp.component.type=prompt`, `fastmcp.component.key=prompt:{name}` |

### 4.3 OpenTelemetry Instrumentation

#### Setup

```bash
# Install packages
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Bootstrap instrumentation
opentelemetry-bootstrap -a install
```

#### Run with Auto-Instrumentation

```bash
# Via CLI
opentelemetry-instrument \
  --service_name thegent-mcp \
  --exporter_otlp_endpoint http://localhost:4317 \
  python -m thegent.main serve --host 127.0.0.1 --port 3847

# Via environment
export OTEL_SERVICE_NAME=thegent-mcp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
opentelemetry-instrument python -m thegent.main serve
```

### 4.4 Telemetry in Thegent

| Feature | Use | Example |
|---------|-----|---------|
| `get_tracer()` | Custom spans in thegent_run | Parse, route, execute phases |
| Auto spans | Tool calls, resource reads | Every MCP operation gets span |
| `ctx.info()`, `ctx.error()` | Logging | Entry/exit, errors |
| OTel exporter | Production traces | Ship to Datadog, Jaeger, or New Relic |

---

## 5. Elicitation Patterns

Elicitation asks the MCP client for user input during tool execution.

### 5.1 Use Cases for Thegent

| Scenario | API | Example |
|----------|-----|---------|
| Missing working directory | `ctx.elicit("Working directory?", response_type=str)` | User provides cwd if not in args |
| Missing session owner | `ctx.elicit("Session owner tag?", response_type=str)` | User provides owner tag for `thegent_bg` |
| Mode selection | `ctx.elicit("Mode?", response_type=["sync", "bg"])` | User chooses sync or background |

### 5.2 Implementation Pattern

```python
@mcp.tool()
async def thegent_run(
    agent: str,
    prompt: str,
    cd: str | None = None,
    ctx: Context = CurrentContext()
) -> ToolResult:
    # If cd not provided, elicit from user
    if not cd:
        result = await ctx.elicit("Working directory?", response_type=str)
        if isinstance(result, AcceptedElicitation):
            cd = result.data
        elif isinstance(result, (DeclinedElicitation, CancelledElicitation)):
            cd = os.getcwd()  # Default fallback

    # Validate cd
    if not os.path.isdir(cd):
        raise ToolError(f"Directory not found: {cd}")

    # Continue with run_impl
    return await run_impl(agent, prompt, cd)
```

### 5.3 Response Type Mapping

| Prompt | response_type | Client UI | Return |
|--------|---------------|-----------|--------|
| Free text | `str` | Text input | `AcceptedElicitation[str]` |
| Single choice | `["a", "b", "c"]` | Dropdown/buttons | `AcceptedElicitation[str]` (selected) |
| Multiple choice | `[["a", "b"], ["c", "d"]]` | Checkboxes | `AcceptedElicitation[list[str]]` (selected list) |
| Structured | `RunConfig` (Pydantic) | Form fields | `AcceptedElicitation[RunConfig]` |
| Confirmation | `None` | "OK/Cancel" button | `AcceptedElicitation[dict]` (empty) |

---

## 6. Task Management

FastMCP Tasks (via Docket) enable background job execution and polling.

### 6.1 Task Configuration

```python
from fastmcp.server.tasks import TaskConfig, TaskMode

@mcp.tool(task=TaskConfig(
    mode="optional",           # "forbidden", "optional", or "required"
    poll_interval=timedelta(seconds=5)
))
async def thegent_run(agent: str, prompt: str) -> ToolResult:
    # Run implementation
    return await run_impl(agent, prompt)
```

### 6.2 TaskMode Behavior

| Mode | Behavior | Response |
|------|----------|----------|
| forbidden | No task support; reject with -32601 | Tool must run sync only |
| optional | Client chooses sync or background | Client decides; server handles both |
| required | Must run as task; reject sync with -32601 | Always returns task_id for polling |

### 6.3 Thegent Task Configuration

**Recommended:**

- **`thegent_run`:** `mode="optional"` — let client choose sync or background
- **`thegent_bg`:** `mode="forbidden"` — always background; no task wrapper needed
- **Read-only tools** (ps, status, logs): `mode="forbidden"` — no async needed

```python
from fastmcp.server.tasks import TaskConfig

# Optional task for long-running sync operation
@mcp.tool(task=TaskConfig(mode="optional", poll_interval=timedelta(seconds=5)))
async def thegent_run(agent: str, prompt: str, timeout: int = 300) -> ToolResult:
    # Wrap sync run_impl in asyncio.to_thread to avoid blocking event loop
    result = await asyncio.to_thread(run_impl, agent, prompt, timeout)
    return ToolResult(content=result['stdout'])

# No task for background launch
@mcp.tool()
async def thegent_bg(agent: str, prompt: str, owner: str | None = None) -> ToolResult:
    result = await bg_impl(agent, prompt, owner)
    return ToolResult(structured_content={"session_id": result['session_id']})

# No task for read-only
@mcp.tool()
async def thegent_ps(owner: str | None = None) -> ToolResult:
    result = await ps_impl(owner)
    return ToolResult(structured_content={"sessions": result})
```

### 6.4 Docket Backend Configuration

Docket manages task state and results. Backend options:

| Backend | URL | Use |
|---------|-----|-----|
| Memory | `memory://` | Development; lost on restart |
| Redis | `redis://localhost:6379` | Production; persistent across restarts |

**Environment:**

```bash
export FASTMCP_DOCKET_URL=memory://                    # Development
export FASTMCP_DOCKET_URL=redis://localhost:6379      # Production
```

---

## 7. Deployment Configuration

### 7.1 HTTP Server Setup

```python
from fastmcp import FastMCP
from fastmcp.server.event_store import EventStore
from key_value.aio.stores.redis import RedisStore
import os

# Create FastMCP instance
mcp = FastMCP(
    name="thegent",
    lifespan=thegent_lifespan,  # Optional startup/shutdown hook
    list_page_size=50           # For pagination (optional)
)

# Add middleware stack (see Middleware Stack section)
# ... (middleware setup)

# Create event store for SSE polling (long runs)
event_store = EventStore(
    storage=RedisStore(url=os.environ.get("FASTMCP_EVENTSTORE", "redis://localhost"))
    if os.environ.get("FASTMCP_EVENTSTORE") else None,
    max_events_per_stream=100,
    ttl=3600  # Events expire after 1 hour
)

# Get HTTP app
app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",  # For SSE polling + resumability
    event_store=event_store,
    retry_interval=2000,          # Client reconnects after 2s
    stateless_http=False          # False for single-server; True for load-balanced
)
```

### 7.2 Configuration Environment Variables

```bash
# Server binding
export THGENT_MCP_HOST=127.0.0.1
export THGENT_MCP_PORT=3847
export THGENT_MCP_PATH=/mcp

# Storage
export THGENT_CACHE_STORAGE=disk:/var/cache/thegent
export FASTMCP_EVENTSTORE=redis://localhost:6379

# Task backend (Docket)
export FASTMCP_DOCKET_URL=redis://localhost:6379

# Telemetry
export OTEL_SERVICE_NAME=thegent-mcp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# OAuth (if added)
export STORAGE_ENCRYPTION_KEY=<base64-encoded-fernet-key>

# Logging
export LOG_LEVEL=INFO
```

### 7.3 Lifespan (Startup/Shutdown)

```python
from fastmcp.server.lifespan import lifespan
from datetime import datetime, UTC

@lifespan
async def thegent_lifespan(server):
    # Startup
    print("thegent MCP server starting")
    start_time = datetime.now(UTC)

    try:
        # Yield context available to tools
        yield {
            "started_at": start_time.isoformat(),
            "version": "1.0"
        }
    finally:
        # Cleanup/shutdown
        print("thegent MCP server shutting down")
        # Close connections, cleanup sessions, etc.
        uptime = (datetime.now(UTC) - start_time).total_seconds()
        print(f"Uptime: {uptime}s")

mcp = FastMCP("thegent", lifespan=thegent_lifespan)
```

**Access in tools:**

```python
@mcp.tool()
async def thegent_health(ctx: Context = CurrentContext()) -> ToolResult:
    lifespan_ctx = ctx.lifespan_context  # Dict from lifespan yield
    return ToolResult(structured_content={
        "status": "ok",
        "started_at": lifespan_ctx.get("started_at"),
        "version": lifespan_ctx.get("version")
    })
```

### 7.4 Stateless HTTP (Horizontal Scaling)

For load-balanced deployments without shared state:

```python
app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    event_store=EventStore(storage=RedisStore(...)),  # Must use Redis
    retry_interval=2000,
    stateless_http=True  # New transport per request; enables horizontal scaling
)
```

**Requirements:**

- `event_store` with Redis backend (shared across servers)
- Session state in Redis (not process-local)
- All instances identical (same code, config)

---

## 8. Verification Checklist

### Phase 1: Core Tools

- [ ] `thegent serve` starts HTTP server at configured host/port
- [ ] `GET /mcp` responds with MCP schema (tools, resources, prompts)
- [ ] Tools visible in Cursor/Claude Code MCP settings
- [ ] `thegent_run` tool callable; returns stdout/stderr
- [ ] `thegent_bg` returns session_id; `thegent_ps` lists it
- [ ] All 11 tools present and callable (run, bg, ps, status, logs, wait, stop, list_agents, list_droids, list_models, dag_list)

**Test:**

```bash
# Start server
python -m thegent.main serve --host 127.0.0.1 --port 3847 &

# List tools
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Call tool
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"thegent_list_agents"}}'
```

---

### Phase 2: Resources and Prompts

- [ ] Resources listed: `thegent://sessions`, `thegent://session/{id}/meta`, `thegent://session/{id}/logs`, `thegent://dag`, `thegent://agents`, `thegent://models`
- [ ] Resources readable; return correct MIME types and content
- [ ] Prompts listed: `thegent_run_agent`, `thegent_create_wbs`, `thegent_bg_task`
- [ ] Prompts render with arguments

**Test:**

```bash
# List resources
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"resources/list"}'

# Read resource
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"resources/read","params":{"uri":"thegent://agents"}}'

# List prompts
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"prompts/list"}'
```

---

### Phase 3: Progress and Background Tasks

- [ ] Long `thegent_run` reports progress updates (ctx.report_progress)
- [ ] Progress visible in MCP client as percentage/status
- [ ] `thegent_run` with `task=optional` can run sync or return task_id
- [ ] Task polling returns in-progress status and final result

**Test:**

```bash
# Run with progress tracking (client-side polling for task)
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"thegent_run","arguments":{"agent":"gemini","prompt":"test"}}}'
```

---

### Phase 4: Elicitation, Logging, and Polish

- [ ] `ctx.info()` logs visible in client (notification messages)
- [ ] `ctx.error()` logs on failures with remediation hint
- [ ] When cwd missing and ambiguous, `ctx.elicit()` prompts user
- [ ] When owner missing for bg, `ctx.elicit()` prompts user
- [ ] Tool results include `structured_content` with session_id, status, etc.
- [ ] Tool annotations present: `read_only`, `destructive`, `idempotent`

**Test:**

```bash
# Call thegent_bg without owner; expect elicitation
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"thegent_bg","arguments":{"agent":"gemini","prompt":"test"}}}'

# Should return elicitation schema in response
```

---

### Phase 5: Production Readiness (Phase 6+)

- [ ] Middleware stack active: ErrorHandling, RateLimiting, Timing, ResponseCaching, ResponseLimiting, Logging
- [ ] `thegent_ps`, `thegent_list_agents` cached with TTL 30s
- [ ] Rate limiting active: >10 requests/sec rejected with 429
- [ ] `thegent_logs` truncated at 500KB
- [ ] Health check endpoint responds <10ms
- [ ] OpenTelemetry traces exported (if configured)
- [ ] Storage backend working (Disk or Redis)

**Test:**

```bash
# Check rate limit
for i in {1..15}; do
  curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$i,\"method\":\"tools/list\"}" &
done
wait

# Should see some 429 responses after burst_capacity exceeded

# Check middleware timing (in response)
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/list"}' | jq '.result.meta'
```

---

### Phase 6: Middleware and Caching

- [ ] ResponseCachingMiddleware active for read-heavy tools
- [ ] Cache TTL 30s verified (repeated calls return cached result within 30s)
- [ ] DiskStore or RedisStore used (not MemoryStore in production)
- [ ] EventStore operational for long runs

**Test:**

```bash
# Call thegent_ps; get response and timestamp
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"thegent_ps"}}' | jq '.result.content'

# Call again immediately; should have same cached result
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"thegent_ps"}}' | jq '.result.content'

# Wait 31s; call again; should be updated
```

---

### Phase 7: Sampling and Advanced Context

- [ ] `thegent_suggest_prompt` tool present and callable
- [ ] `ctx.sample()` requests LLM generation (if client supports) or fallback handler activates
- [ ] Fallback sampling_handler (OpenAI) used when client lacks sampling
- [ ] Prompts rendered with suggested arguments

**Test:**

```bash
# Call thegent_suggest_prompt
curl http://127.0.0.1:3847/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"thegent_suggest_prompt","arguments":{"raw_prompt":"fix bug"}}}'

# Should return refined prompt
```

---

### Deployment Verification

- [ ] Environment variables set correctly (host, port, storage, telemetry)
- [ ] Logs are structured (JSON if StructuredLoggingMiddleware)
- [ ] Traces exported to OTel endpoint (if configured)
- [ ] Health check returns 200 OK: `GET http://<host>:<port>/health` (optional custom route)
- [ ] Server gracefully shuts down on SIGTERM (lifespan cleanup)
- [ ] No orphan sessions or tasks after server restart
- [ ] Storage backend persists data (test with Redis restart)

---

### Integration Points

| Component | Verification | Link |
|-----------|---|---|
| **CLI** | `thegent run/bg/ps/...` returns same result as MCP tools | `/src/thegent/cli.py` vs `/src/thegent/mcp_server.py` |
| **Docket** | Background tasks persisted in Redis; polling works | `FASTMCP_DOCKET_URL=redis://...` |
| **Storage** | Cache hit rate; no memory leaks | Monitor `cache_storage` hit/miss metrics |
| **Telemetry** | Traces/spans visible in Jaeger/Datadog | `OTEL_EXPORTER_OTLP_ENDPOINT` |
| **Auth** | Bearer token / OAuth enforced (if added) | Phase 5 work item |
| **Load Balancer** | Stateless HTTP works across instances | `stateless_http=True` + EventStore Redis |

---

## Cross-References

### Planning Documents

- **Implementation Plan:** `/docs/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md`
  - Phases 1–7 roadmap
  - File structure and refactoring guidance
  - Extended features (pagination, versioning, dependency injection)

### Research Documents

- **Elicitation & Context API:** `/docs/research/FASTMCP_ELICITATION_CONTEXT.md`
- **Progress & Tasks:** `/docs/research/FASTMCP_PROGRESS_TASKS.md`
- **Transforms & Deployment:** `/docs/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md`
- **Storage & EventStore:** `/docs/research/FASTMCP_STORAGE_EVENTSTORE.md`
- **Sampling & Telemetry:** `/docs/research/FASTMCP_SAMPLING_TELEMETRY.md`
- **Middleware:** `/docs/research/FASTMCP_MIDDLEWARE.md`

### External References

- [FastMCP 3.0 Documentation](https://gofastmcp.com)
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP HTTP Deployment](https://gofastmcp.com/deployment/http)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

---

**Last Updated:** 2026-02-14
**Maintainer:** thegent FastMCP implementation team
**Status:** Active (Phases 1–7 in progress)
