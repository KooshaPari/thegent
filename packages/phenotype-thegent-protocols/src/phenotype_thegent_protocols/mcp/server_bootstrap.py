"""Bootstrap helpers for the MCP server extraction surface (WL-120)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

_SERVER_PY = Path(__file__).parent / "server.py"


def load_auth(load_module: Any) -> Any:
    """Load the auth helper module from server/auth.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="auth.py",
        module_import_name="thegent.mcp._server_auth",
        failure_message="Unable to load auth helpers",
    )


def load_lifecycle(load_module: Any) -> Any:
    """Load the lifecycle helper module from server/lifecycle.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="lifecycle.py",
        module_import_name="thegent.mcp._server_lifecycle",
        failure_message="Unable to load lifecycle helpers",
    )


def build_elicitation_helpers(
    *,
    create_elicitation_cache: Callable[..., Any],
    elicitation_cache_key: Callable[[str, type], str],
    get_cached_elicitation: Callable[..., Any | None],
    cache_elicitation_response: Callable[..., None],
    resolve_cwd_elicitation: Callable[..., tuple[Path | None, str | None]],
    resolve_owner_elicitation: Callable[..., tuple[str | None, str | None]],
    default_cwd_from_context: Callable[[Any], Path | None],
    default_owner_from_context: Callable[[Any], str | None],
    accepted_elicitation_type: type,
    declined_elicitation_type: type,
    cancelled_elicitation_type: type,
    cache_maxsize: int = 100,
    cache_ttl_seconds: int = 300,
) -> tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    """Build server-compatible helper callables and cache instance."""
    elicitation_cache = create_elicitation_cache(maxsize=cache_maxsize, ttl_seconds=cache_ttl_seconds)

    def _cache_elicitation_key(prompt: str, response_type: type) -> str:
        return elicitation_cache_key(prompt, response_type)

    def _get_cached_elicitation(prompt: str, response_type: type) -> Any | None:
        return get_cached_elicitation(elicitation_cache, prompt=prompt, response_type=response_type)

    def _cache_elicitation_response(prompt: str, response_type: type, response: Any) -> None:
        cache_elicitation_response(elicitation_cache, prompt=prompt, response_type=response_type, response=response)

    def _resolve_cwd_elicitation(response: Any) -> tuple[Path | None, str | None]:
        return resolve_cwd_elicitation(
            response,
            accepted_elicitation_type=accepted_elicitation_type,
            declined_elicitation_type=declined_elicitation_type,
            cancelled_elicitation_type=cancelled_elicitation_type,
        )

    def _resolve_owner_elicitation(response: Any, *, default_owner_tag: str) -> tuple[str | None, str | None]:
        return resolve_owner_elicitation(
            response,
            default_owner_tag=default_owner_tag,
            accepted_elicitation_type=accepted_elicitation_type,
            declined_elicitation_type=declined_elicitation_type,
            cancelled_elicitation_type=cancelled_elicitation_type,
        )

    def get_default_cwd(ctx: Any) -> Path | None:
        return default_cwd_from_context(ctx)

    def get_default_owner(ctx: Any) -> str | None:
        return default_owner_from_context(ctx)

    return (
        elicitation_cache,
        _cache_elicitation_key,
        _get_cached_elicitation,
        _cache_elicitation_response,
        _resolve_cwd_elicitation,
        _resolve_owner_elicitation,
        get_default_cwd,
        get_default_owner,
    )


def build_lifespan(
    *,
    lifespan_decorator: Callable[[Any], Any],
    lifespan_proxy: Callable[..., AsyncIterator[dict[str, Any] | None]],
    run_lifecycle: Callable[..., AsyncIterator[dict[str, Any] | None]],
    log: Any,
    ps_impl: Callable[..., Any],
    auto_init_on_startup: Callable[..., Any],
) -> Any:
    """Build the FastMCP lifespan function with injected lifecycle dependencies."""

    @lifespan_decorator
    async def _thegent_lifespan(mcp_app: Any) -> AsyncIterator[dict[str, Any] | None]:
        async for payload in lifespan_proxy(
            mcp_app=mcp_app,
            run_lifecycle=run_lifecycle,
            log=log,
            ps_impl=ps_impl,
            auto_init_on_startup=auto_init_on_startup,
        ):
            yield payload

    return _thegent_lifespan
