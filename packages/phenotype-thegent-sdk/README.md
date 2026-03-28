# thegent-sdk

Typed Python SDK slice for `thegent`.

## API Surface

- `ThegentClient.run(prompt, ...)` for one-shot runs.
- `ThegentClient.list_sessions()` for session metadata (`/v1/sessions` list or `{sessions: [...]}` payloads).
- `ThegentClient.resume(session_id, prompt=...)` for resume/continue semantics.
- `ThegentClient.run_stream(prompt, ...)` for line-delimited JSON stream events from `/v1/run`.
- `ThegentClient(..., protocol="mcp")` switches run/list/resume calls to MCP HTTP JSON-RPC (`/mcp`, `tools/call`) using `thegent_run`, `thegent_session_list`, and `thegent_resume`.
- `AsyncThegentClient.run(prompt, ...)` async parity for one-shot runs.
- `AsyncThegentClient.list_sessions()` async parity for session metadata listing.
- `AsyncThegentClient.resume(session_id, prompt=...)` async parity for resume semantics.
- `AsyncThegentClient.run_stream(prompt, ...)` async streamed parity with the same `StreamEvent` shape.

## HTTP Error Types

Non-2xx REST responses are raised as typed exceptions:

- `ThegentAuthenticationError` for `401`/`403`
- `ThegentNotFoundError` for `404`
- `ThegentRateLimitError` for `429`
- `ThegentRequestError` for other `4xx`
- `ThegentServerError` for `5xx`

Error details are extracted from `detail`, `message`, nested `error.message`/`error.detail` (including nested list payloads), and list-style validation payloads (for example `detail: [{"msg": "..."}]` or top-level list payloads like `[{"message": "..."}]`).

## Streamed API Parity Examples

Synchronous stream:

```python
from thegent_sdk import ThegentClient

with ThegentClient("http://localhost:3847") as client:
    for event in client.run_stream("summarize this"):
        print(event.type, event.payload)
```

Asynchronous stream:

```python
import asyncio
from thegent_sdk import AsyncThegentClient

async def main() -> None:
    async with AsyncThegentClient("http://localhost:3847") as client:
        async for event in client.run_stream("summarize this"):
            print(event.type, event.payload)

asyncio.run(main())
```
