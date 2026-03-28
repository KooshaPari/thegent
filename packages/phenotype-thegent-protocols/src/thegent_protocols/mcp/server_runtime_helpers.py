"""Runtime/lifecycle helpers extracted from the MCP server module."""

from __future__ import annotations

import warnings
from collections.abc import AsyncIterator, Callable, Mapping
from typing import Any

from starlette.responses import JSONResponse, Response


async def lifespan_proxy(
    *,
    mcp_app: Any,
    run_lifecycle: Callable[..., AsyncIterator[dict[str, Any] | None]],
    log: Any,
    ps_impl: Callable[..., Any],
    auto_init_on_startup: Callable[..., Any],
) -> AsyncIterator[dict[str, Any] | None]:
    """Run the server lifecycle and stream startup/shutdown payloads."""
    async for payload in run_lifecycle(
        mcp_app,
        log,
        ps_impl=ps_impl,
        auto_init_on_startup=auto_init_on_startup,
    ):
        yield payload


def health_response() -> Response:
    """Build the standard health payload."""
    return JSONResponse({"status": "ok", "server": "thegent"})


def create_event_store(
    *,
    env: Mapping[str, str],
    event_store_cls: Callable[..., Any],
    redis_store_cls: Callable[..., Any],
) -> Any:
    """Create EventStore using Redis when FASTMCP_EVENT_STORE_URL is set."""
    url = env.get("FASTMCP_EVENT_STORE_URL")
    if url:
        return event_store_cls(storage=redis_store_cls(url=url))
    return event_store_cls()


def create_http_app(
    *,
    mcp: Any,
    event_store: Any,
    bearer_auth_middleware: Any,
    log: Any,
    stateless_http: bool = True,
) -> Any:
    """Create the ASGI app and wire middleware and responses routes."""
    app = mcp.http_app(
        event_store=event_store,
        retry_interval=2000,
        transport="http",
        stateless_http=stateless_http,
    )
    if hasattr(app, "add_middleware"):
        app.add_middleware(bearer_auth_middleware)

    if hasattr(app, "add_route") and hasattr(app, "add_websocket_route"):
        from thegent_core.utils.routing_impl.litellm_responses_handler import (
            handle_responses_request,
            handle_responses_websocket,
        )

        app.add_route(
            "/v1/responses",
            handle_responses_request,
            methods=["POST"],
        )
        app.add_websocket_route(
            "/v1/responses/ws",
            handle_responses_websocket,
        )
        log.info("registered /v1/responses (POST) and /v1/responses/ws (WebSocket) via LiteLLM Router")
    else:
        log.warning(
            "http_app: ASGI app does not support add_route/add_websocket_route; /v1/responses routes NOT registered"
        )

    return app


def run_server(
    *,
    host: str | None,
    port: int | None,
    reload: bool,
    settings: Any,
    http_app_factory_import_path: str,
    http_app_builder: Callable[..., Any],
) -> None:
    """Run uvicorn with reload-safe import string and lifecycle enabled."""
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="websockets.legacy",
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="uvicorn.protocols.websockets.websockets_impl",
    )

    import uvicorn

    if reload:
        uvicorn.run(
            http_app_factory_import_path,
            host=host or settings.mcp_host,
            port=port or settings.mcp_port,
            reload=True,
            factory=True,
        )
        return

    app = http_app_builder(stateless_http=True)
    uvicorn.run(
        app,
        host=host or settings.mcp_host,
        port=port or settings.mcp_port,
        lifespan="on",
    )
