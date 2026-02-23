# FastMCP Context

> Definitive technical reference for implementing FastMCP servers in thegent and trace.
> Sources: gofastmcp.com/changelog, jlowin.dev/blog/fastmcp-3-whats-new, jlowin.dev/blog/fastmcp-3-launch, github.com/jlowin/fastmcp (fetched 2026-02-20).
> **Version covered: FastMCP 3.0.0 (GA, 2026-02-18)**

---

## What is FastMCP

**FastMCP** is a Pythonic framework for building MCP (Model Context Protocol) servers and clients. It wraps the raw `mcp` SDK with:

- **Declarative API**: Decorators (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`) for defining server capabilities
- **Composable Architecture**: Providers, Transforms, and Middleware form a three-layer pipeline
- **Context API**: User input elicitation, progress reporting, structured logging, LLM sampling, session state
- **Multiple Transports**: STDIO (default), Streamable HTTP (production), SSE (legacy)
- **Production Features**: OpenTelemetry tracing, background tasks, granular auth, component versioning

**Why FastMCP over raw MCP SDK?** FastMCP turns multi-hundred-line protocol boilerplate into 5-10 lines. Pydantic auto-generates tool schemas from type hints; the decorator pattern matches Python idioms.

**thegent Usage:** FastMCP is the core for thegent's MCP server (`src/thegent/mcp/server.py`) with 30+ tools, middleware pipeline (caching, rate limiting, timing, error handling), and bearer auth.

**trace Usage:** `fastmcp>=3.0.0b1` — uses FastMCP as the MCP layer for trace's MCP server.

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 3.0.0 | 2026-02-18 | GA release. Composable providers/transforms, component versioning, granular auth, OpenTelemetry |
| 3.0.0rc1 | 2026-02-12 | Release candidate |
| 3.0.0b2 | 2026-02-07 | Second beta; "2 Fast 2 Beta" |
| 3.0.0b1 | 2026-01-20 | First beta; initial 3.0 architecture |
| 2.x | 2025 | Previous stable; decorators returned component objects |

---

## Installation

```bash
# Stable (GA)
pip install fastmcp

# With background task support
pip install "fastmcp[tasks]"

# Check installed version
python -c "import fastmcp; print(fastmcp.__version__)"
# → 3.0.0
```

---

## Core Architecture (3.0)

FastMCP 3.0 is built on three composable primitives:

```
┌─────────────────────────────────────────────────┐
│              FastMCP Server                     │
├─────────────────────────────────────────────────┤
│ PROVIDERS (where components originate):         │
│   • LocalProvider — decorated functions         │
│   • FileSystemProvider — filesystem discovery   │
│   • OpenAPIProvider — REST API → tools          │
│   • ProxyProvider — remote MCP server           │
│   • SkillsProvider — agent skill files          │
│   • Custom — implement Provider base class      │
│                                                 │
│ TRANSFORMS (modify component pipeline):         │
│   • Namespace — prefix all names                │
│   • ToolTransform — rename/redescribe tools     │
│   • VersionFilter — expose by version           │
│   • ResourcesAsTools — expose resources as tools│
│   • PromptsAsTools — expose prompts as tools    │
│   • Custom — implement Transform base class     │
│                                                 │
│ MIDDLEWARE (intercept requests):                │
│   • CachingMiddleware, RateLimitingMiddleware   │
│   • TimingMiddleware, LoggingMiddleware         │
│   • ErrorHandlingMiddleware                     │
│   • AuthMiddleware — server-wide auth           │
│   • PingMiddleware — keep-alive pings           │
└─────────────────────────────────────────────────┘
```

### Transport Options

| Transport | Use Case | Status |
|-----------|----------|--------|
| **STDIO** | Local CLI, Claude Desktop, Cursor | Default |
| **Streamable HTTP** | Remote, web dashboards | Production-ready |
| **SSE** | Legacy clients | Deprecated |

---

## Core Decorators

### Tools (`@mcp.tool`)

Tools are callable operations that clients invoke.

```python
from fastmcp import FastMCP

mcp = FastMCP("thegent")

# Basic tool — decorators return the original function (callable)
@mcp.tool
def thegent_status() -> str:
    """Get thegent status."""
    return "Running"

# Callable normally (for testing)
thegent_status()  # → "Running"
```

**Tool with parameters and annotations:**

```python
@mcp.tool(
    readOnlyHint=True,           # Does not modify environment
    destructiveHint=False,
    idempotentHint=True,
    tags={"execution", "core"},
    timeout=60.0,                # Max execution seconds
    version="2.0",               # Component version for versioning system
)
def list_agents(include_stopped: bool = False) -> dict:
    """List all available agents.

    Args:
        include_stopped: Include stopped agents in results
    """
    return {"agents": []}
```

**Generated schema (auto from type hints + docstring):**

```json
{
  "name": "list_agents",
  "description": "List all available agents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_stopped": {
        "type": "boolean",
        "description": "Include stopped agents in results",
        "default": false
      }
    }
  }
}
```

**Structured output with ToolResult:**

```python
from fastmcp.tools.tool import ToolResult

@mcp.tool
def thegent_run(command: str) -> ToolResult:
    """Run a command."""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return ToolResult(
        content=f"Exit code: {result.returncode}",
        structured_content={
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        meta={"command": command},
    )
```

### Resources (`@mcp.resource`)

Resources expose readable data via URI.

```python
@mcp.resource("thegent://sessions")
def list_sessions() -> list[dict]:
    """List active sessions."""
    return [{"id": "sess_123", "status": "running"}]

# URI template parameters
@mcp.resource("thegent://session/{id}")
def get_session(id: str) -> dict:
    """Get session by ID."""
    return {"id": id, "status": "running"}

# Optional query parameters (RFC 6570)
@mcp.resource("thegent://session/{id}/meta{?include_logs}")
def get_session_meta(id: str, include_logs: bool = False) -> dict:
    meta = {"id": id}
    if include_logs:
        meta["logs"] = []
    return meta
```

### Prompts (`@mcp.prompt`)

```python
@mcp.prompt
def agent_instructions(agent_type: str = "general") -> str:
    """Get agent instructions."""
    return f"You are a {agent_type} agent. Execute tasks precisely."
```

---

## Context API

Inject `Context` for logging, progress, elicitation, and session state.

```python
from fastmcp.server.dependencies import CurrentContext
from fastmcp.server.context import (
    AcceptedElicitation,
    DeclinedElicitation,
    CancelledElicitation,
)
# Context type (use Any for flexibility in thegent pattern)
from typing import Any
Context = Any
```

### Logging

```python
@mcp.tool
async def my_tool(ctx: Context = CurrentContext()) -> str:
    await ctx.info("Starting operation")
    await ctx.debug("Debug detail")
    await ctx.warning("Watch out")
    await ctx.error("Something failed")
    return "done"

# Structured logging with logger name and extra fields
await ctx.info(
    "Agent spawned",
    logger_name="thegent.orchestration",
    extra={"agent_id": "123", "timeout": 30},
)
```

### Progress Reporting

```python
from fastmcp.server.dependencies import Progress, ProgressLike

@mcp.tool
async def batch_process(
    items: list[str],
    ctx: Context = CurrentContext(),
    progress: ProgressLike = Progress(),
) -> dict:
    await progress.set_total(len(items))
    results = []
    for item in items:
        await progress.set_message(f"Processing {item}...")
        results.append(await process_item(item))
        await progress.increment()
    return {"results": results}
```

### User Input Elicitation

```python
@mcp.tool
async def configure_env(ctx: Context = CurrentContext()) -> str:
    # Simple string prompt
    result = await ctx.elicit("Working directory?", response_type=str)
    if isinstance(result, AcceptedElicitation):
        return f"Using: {result.data}"
    elif isinstance(result, DeclinedElicitation):
        return "Declined"
    elif isinstance(result, CancelledElicitation):
        return "Cancelled"

# Single-select from options dict
options = {
    "dev": {"title": "Development"},
    "staging": {"title": "Staging"},
    "prod": {"title": "Production"},
}
result = await ctx.elicit("Select environment:", response_type=options)
env = result.data  # "dev", "staging", or "prod"

# Structured data (Pydantic model)
from pydantic import BaseModel
class AgentConfig(BaseModel):
    name: str
    timeout_secs: int

result = await ctx.elicit("Configure agent:", response_type=AgentConfig)
if isinstance(result, AcceptedElicitation):
    config: AgentConfig = result.data
```

### Session State (Async in 3.0)

```python
# v3: state methods are async (breaking change from v2)
@mcp.tool
async def set_config(key: str, value: str, ctx: Context = CurrentContext()) -> str:
    state = await ctx.get_state()
    state.setdefault("config", {})[key] = value
    await ctx.set_state(state)
    return f"Saved: {key}={value}"

@mcp.tool
async def get_config(key: str, ctx: Context = CurrentContext()) -> str:
    state = await ctx.get_state()
    return str(state.get("config", {}).get(key))
```

**Redis backend for session state:**

```python
from key_value.aio.stores.redis import RedisStore

mcp = FastMCP("server", session_state_store=RedisStore(url="redis://localhost:6379"))
```

### Transport Detection

```python
@mcp.tool
def my_tool(ctx: Context = CurrentContext()) -> str:
    if ctx.transport == "stdio":
        return "compact"      # Short output for CLI
    return "detailed"          # Rich output for HTTP
# ctx.transport: "stdio" | "sse" | "streamable-http"
```

---

## Providers

### LocalProvider (Decorators)

```python
from fastmcp.server.providers import LocalProvider

# Reusable provider (shared across multiple server instances)
provider = LocalProvider()

@provider.tool
def shared_tool() -> str:
    return "available everywhere"

server1 = FastMCP("Server1", providers=[provider])
server2 = FastMCP("Server2", providers=[provider])
```

### FileSystemProvider

```python
from fastmcp.server.providers import FileSystemProvider

# Discovers tools from .py files in directory; hot-reload on changes
mcp = FastMCP("server", providers=[
    FileSystemProvider("mcp/", reload=True)
])
```

### OpenAPIProvider

```python
from fastmcp.server.providers.openapi import OpenAPIProvider
import httpx

spec = {...}  # OpenAPI dict or URL
client = httpx.AsyncClient(base_url="https://api.example.com")
provider = OpenAPIProvider(openapi_spec=spec, client=client)
mcp = FastMCP("API Server", providers=[provider])
```

### ProxyProvider / create_proxy

```python
from fastmcp.server import create_proxy

# Proxy a remote MCP server
server = create_proxy("http://remote-mcp-server:3000/mcp")

# Mount subserver with namespace
main = FastMCP("Main")
sub = FastMCP("Sub")
main.mount(sub, prefix="sub")
# "greet" in sub becomes "sub_greet" in main
```

### SkillsProvider

```python
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from pathlib import Path

mcp = FastMCP("Skills Server")
mcp.add_provider(SkillsDirectoryProvider(
    roots=Path.home() / ".claude" / "skills"
))
# Exposes .md skill files as MCP resources
```

---

## Transforms

### Namespace

```python
from fastmcp.server.transforms import Namespace

provider.add_transform(Namespace("thegent"))
# "run" → "thegent_run"; "data://x" → "data://thegent/x"
```

### VersionFilter

```python
from fastmcp.server.transforms import VersionFilter

api_v1 = FastMCP("v1", providers=[components])
api_v1.add_transform(VersionFilter(version_lt="2.0"))

api_v2 = FastMCP("v2", providers=[components])
api_v2.add_transform(VersionFilter(version_gte="2.0"))
```

### ResourcesAsTools / PromptsAsTools

```python
from fastmcp.server.transforms import ResourcesAsTools, PromptsAsTools

mcp.add_transform(ResourcesAsTools(mcp))   # Resources → tools
mcp.add_transform(PromptsAsTools(mcp))     # Prompts → tools
```

### Visibility Control

```python
mcp.disable(tags={"admin"})           # Hide admin tools by default
mcp.disable(names={"dangerous_op"})   # Hide specific tool
mcp.enable(tags={"public"}, only=True)  # Allowlist: show only public

# Per-session visibility (via context)
@mcp.tool
async def unlock_premium(ctx: Context = CurrentContext()) -> str:
    await ctx.enable_components(tags={"premium"})
    return "Premium unlocked for this session"
```

---

## Middleware

thegent uses these middleware in `server.py`:

```python
from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware

mcp = FastMCP(
    "thegent",
    middleware=[
        ErrorHandlingMiddleware(),
        LoggingMiddleware(),
        TimingMiddleware(),
        RateLimitingMiddleware(requests_per_minute=60),
        ResponseCachingMiddleware(ttl=300),
        ResponseLimitingMiddleware(max_bytes=1024 * 1024),  # 1MB
    ],
)
```

---

## Authorization (3.0)

### Component-Level Auth

```python
from fastmcp.server.auth import require_auth, require_scopes

@mcp.tool(auth=require_auth)
def protected_tool(): ...

@mcp.resource("data://secret", auth=require_scopes("read"))
def secret_data(): ...

@mcp.prompt(auth=require_scopes("admin"))
def admin_prompt(): ...
```

### Server-Wide Auth (AuthMiddleware)

```python
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.auth import require_auth, restrict_tag

# All endpoints require auth
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# Tag-based restrictions
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"]))
])
```

**thegent pattern (Bearer token, custom middleware):**

```python
# src/thegent/mcp/server.py — BearerAuthMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.mcp_auth_mode == "bearer":
            if request.url.path == "/health":
                return await call_next(request)
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse({"error": "Missing Authorization"}, status_code=401)
            token = auth[7:]
            if token not in valid_tokens:
                return JSONResponse({"error": "Invalid token"}, status_code=401)
        return await call_next(request)
```

---

## Component Versioning

```python
# Register multiple versions of the same tool
@mcp.tool(version="1.0")
def add(x: int, y: int) -> int:
    return x + y

@mcp.tool(version="2.0")
def add(x: int, y: int, z: int = 0) -> int:
    return x + y + z

# Highest version served by default
# Client calls specific version:
result = await client.call_tool("add", {"x": 1, "y": 2}, version="1.0")
```

---

## Background Tasks

```python
from fastmcp.server.tasks.config import TaskConfig
from datetime import timedelta

@mcp.tool(task=TaskConfig(mode="optional", poll_interval=timedelta(seconds=5)))
async def long_running(command: str) -> str:
    """Client can choose sync or async execution."""
    import asyncio
    await asyncio.sleep(30)
    return "Done"

@mcp.tool(task=TaskConfig(mode="required"))
async def must_be_async() -> str:
    """Client MUST use async mode (exceeds HTTP timeout)."""
    ...

# Shorthand
@mcp.tool(task=True)
async def background_task() -> str: ...

# Sync code runs in threadpool automatically — no asyncio.to_thread needed
@mcp.tool
def sync_blocking() -> str:
    import time; time.sleep(10)  # Dispatched to threadpool automatically
    return "done"
```

**Install tasks extra:**

```bash
pip install "fastmcp[tasks]"
```

---

## Server Lifecycle (Lifespan)

```python
from fastmcp.server.lifespan import lifespan

@lifespan
async def db_lifespan(server):
    db = await connect_db()
    try:
        yield {"db": db}
    finally:
        await db.close()

@lifespan
async def cache_lifespan(server):
    cache = await connect_cache()
    try:
        yield {"cache": cache}
    finally:
        await cache.close()

# Compose lifespans with pipe operator
mcp = FastMCP("server", lifespan=db_lifespan | cache_lifespan)
```

---

## Transports

### STDIO (Local)

```python
import asyncio

async def main():
    async with mcp.stdio_server() as (read, write):
        await mcp.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

### Streamable HTTP (Remote)

```python
async def main():
    async with mcp.http_server(host="0.0.0.0", port=8000) as server:
        await server.wait()
```

**HTTP request:**

```
POST http://localhost:8000/mcp/tools/call
Authorization: Bearer <token>
Content-Type: application/json

{"tool": "thegent_run", "arguments": {"command": "thegent ps"}}
```

### CLI Run

```bash
# Run server
fastmcp run server.py

# Run with hot reload
fastmcp run server.py --reload
fastmcp dev server.py   # Shorthand (reload + inspector)

# List tools
fastmcp list server.py

# Call a tool
fastmcp call server.py tool_name --arg1 val1

# Install with harness
fastmcp install server.py --name "thegent"   # Claude Desktop, Cursor, Goose
```

---

## OpenTelemetry Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# FastMCP auto-instruments tool calls — no changes to tool code needed
mcp = FastMCP("server")
```

---

## Testing

```python
import pytest
from fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("test")

    @mcp.tool
    def sample_tool(value: str) -> str:
        return f"Result: {value}"

    return mcp

@pytest.mark.asyncio
async def test_tool_execution(mcp_server):
    # Direct call (decorators return original functions)
    result = mcp_server._tool_registry["sample_tool"].fn("test")
    assert result == "Result: test"

# In-process client testing
from fastmcp import Client

@pytest.mark.asyncio
async def test_with_client(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("sample_tool", {"value": "hello"})
        assert "Result: hello" in str(result)
```

---

## Breaking Changes: v2 → v3

| Change | v2 Behavior | v3 Behavior | Fix |
|--------|-------------|-------------|-----|
| Decorators | Return component objects | Return original function | Set `FASTMCP_DECORATOR_MODE=object` for v2 compat |
| `ctx.get_state()` | Synchronous | **Async** (must `await`) | Add `await` |
| `ctx.set_state()` | Synchronous | **Async** (must `await`) | Add `await` |
| `enabled=` parameter | `@mcp.tool(enabled=False)` | Removed | Use `mcp.disable(names={"tool"})` |
| Auth env vars | Auto-loaded from env | Must configure explicitly | Configure auth providers manually |
| `fastmcp dev` | Direct subcommand | `fastmcp dev inspector` | Update scripts |
| `ui=` parameter | `@mcp.tool(ui=...)` | Changed to `app=AppConfig(...)` | Update usage |
| Metadata namespace | `_fastmcp` | `fastmcp` (no underscore) | Update metadata readers |
| `require_auth` | `@mcp.tool(require_auth=True)` | `@mcp.tool(auth=require_auth)` | Use new auth param |

**Upgrade path:**

```bash
pip install fastmcp==3.0.0
# Run server; fix any async state calls; configure auth explicitly
```

---

## Sources & References

- **Official Docs**: https://gofastmcp.com (fetched 2026-02-20)
- **GitHub**: https://github.com/jlowin/fastmcp (fetched 2026-02-20)
- **What's New in 3.0**: https://www.jlowin.dev/blog/fastmcp-3-whats-new (fetched 2026-02-20)
- **3.0 GA Announcement**: https://www.jlowin.dev/blog/fastmcp-3-launch (fetched 2026-02-20)
- **Changelog**: https://gofastmcp.com/changelog (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/fastmcp/
- **thegent server**: `src/thegent/mcp/server.py`
- **Last Verified**: 2026-02-20

See also: `docs/context/mcp-protocol.md`

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `fastmcp>=3.0.0` |
| Extra (tasks) | `fastmcp[tasks]` |
| Latest stable | 3.0.0 (2026-02-18) |
| Transport default | STDIO |
| HTTP port | Configurable (thegent: 3847) |
| Auth | BearerAuthMiddleware (thegent pattern) |

### Decorator Quick Patterns

```python
@mcp.tool                                    # Basic tool
@mcp.tool(tags={"core"}, timeout=30.0)       # Annotated tool
@mcp.tool(task=TaskConfig(mode="optional"))  # Background task
@mcp.resource("scheme://path/{id}")          # Resource with template
@mcp.prompt                                  # Prompt template
```

### Context Quick Patterns

```python
ctx: Context = CurrentContext()         # Inject context
await ctx.info("message")              # Log
await ctx.get_state()                  # Session state (async in v3!)
await ctx.set_state(data)              # Session state (async in v3!)
await ctx.elicit("msg", response_type=str)  # User input
ctx.transport                          # "stdio" | "sse" | "streamable-http"
```

### Common Middleware Stack (thegent)

```python
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
```
