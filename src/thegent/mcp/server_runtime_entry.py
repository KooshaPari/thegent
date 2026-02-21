"""Runtime entrypoint MCP registration and wiring helpers."""

from __future__ import annotations

import os
from typing import Any, Callable, cast

from fastmcp.server.event_store import EventStore
from starlette.requests import Request
from starlette.responses import Response

def register_runtime_entry(
    *,
    mcp: Any,
    health_response: Callable[[], Response],
    create_event_store: Callable[..., Any],
    create_http_app: Callable[..., Any],
    bearer_auth_middleware: Any,
    log: Any,
    parse_acp_payload: Callable[[str], tuple[dict[str, Any] | None, str | None]],
    format_acp_response: Callable[..., str],
    run_server: Callable[..., None],
    settings_factory: Callable[[], Any],
    http_app_factory_import_path: str,
) -> tuple[object, object, object, object, object, object]:
    """Register runtime route/tool and return runtime entry helpers."""

    @mcp.custom_route("/health", methods=["GET"])
    async def health(request: Request) -> Response:
        """Health check endpoint for monitoring."""
        del request
        return health_response()

    def _get_event_store() -> EventStore:
        """EventStore: MemoryStore default, Redis when FASTMCP_EVENT_STORE_URL set."""
        from key_value.aio.stores.redis import RedisStore

        return cast(
            "EventStore",
            create_event_store(
                env=os.environ,
                event_store_cls=EventStore,
                redis_store_cls=RedisStore,
            ),
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_acp_invoke(
        agent_url: str,
        task: str,
        payload: str = "{}",
    ) -> str:
        """
        Invoke a remote ACP agent and return its result (FR-ACP-002).

        Uses the ACP <-> MCP bridge to call any ACP-compatible agent endpoint
        over HTTP and return the agent's plain-text response.

        Args:
            agent_url: Base URL of the remote ACP agent (e.g. http://localhost:8420)
            task:      Human-readable task description / prompt sent to the agent
            payload:   JSON string with extra context dict forwarded to the agent
                       (default: empty object)

        Returns: JSON string with {success, result, agent_id, elapsed_ms}
        """
        import time as _time

        from thegent.adapters.acp_client import ACPClient, ACPServerUnreachableError
        from thegent.adapters.acp_mcp_bridge import ACPAgentCallError, AcpMcpBridge

        context, payload_error = parse_acp_payload(payload)
        if payload_error:
            return format_acp_response(
                success=False,
                error=payload_error,
                result="",
                agent_url=agent_url,
                elapsed_ms=0,
            )

        bridge = AcpMcpBridge(acp_client=ACPClient(base_url=agent_url))

        start = _time.perf_counter()
        try:
            result_text = await bridge.acp_agent_to_mcp_tool(
                agent_url=agent_url,
                task=task,
                payload=context or {},
            )
            elapsed_ms = int((_time.perf_counter() - start) * 1000)
            return format_acp_response(
                success=True,
                result=result_text,
                agent_url=agent_url,
                elapsed_ms=elapsed_ms,
            )
        except ACPServerUnreachableError as exc:
            elapsed_ms = int((_time.perf_counter() - start) * 1000)
            return format_acp_response(
                success=False,
                error=f"ACP agent unreachable: {exc}",
                result="",
                agent_url=agent_url,
                elapsed_ms=elapsed_ms,
            )
        except ACPAgentCallError as exc:
            elapsed_ms = int((_time.perf_counter() - start) * 1000)
            return format_acp_response(
                success=False,
                error=str(exc),
                result="",
                agent_url=agent_url,
                elapsed_ms=elapsed_ms,
            )

    def http_app(stateless_http: bool = True) -> Any:
        """Return ASGI app with EventStore (mountable in FastAPI/Starlette)."""
        return create_http_app(
            mcp=mcp,
            event_store=_get_event_store(),
            bearer_auth_middleware=bearer_auth_middleware,
            log=log,
            stateless_http=stateless_http,
        )

    def http_app_factory() -> Any:
        """Factory for uvicorn --reload."""
        return http_app(stateless_http=True)

    def run(host: str | None = None, port: int | None = None, reload: bool = False) -> None:
        """Start the FastMCP server with EventStore and optional Docket."""
        settings = settings_factory()
        run_server(
            host=host,
            port=port,
            reload=reload,
            settings=settings,
            http_app_factory_import_path=http_app_factory_import_path,
            http_app_builder=http_app,
        )

    return (health, _get_event_store, thegent_acp_invoke, http_app, http_app_factory, run)
