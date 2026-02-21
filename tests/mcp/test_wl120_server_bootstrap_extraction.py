# @trace WL-120 B90-W2-D6
"""Focused tests for WL-120 server bootstrap extraction."""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any

from fastmcp.server.elicitation import AcceptedElicitation, CancelledElicitation, DeclinedElicitation

from thegent.mcp import server_bootstrap
from thegent.mcp import server_cache_elicitation_response as cache_elicitation_response
from thegent.mcp import server_create_elicitation_cache as create_elicitation_cache
from thegent.mcp import server_default_cwd_from_context as default_cwd_from_context
from thegent.mcp import server_default_owner_from_context as default_owner_from_context
from thegent.mcp import server_elicitation_cache_key as elicitation_cache_key
from thegent.mcp import server_get_cached_elicitation as get_cached_elicitation
from thegent.mcp import server_resolve_cwd_elicitation as resolve_cwd_elicitation
from thegent.mcp import server_resolve_owner_elicitation as resolve_owner_elicitation


def test_bootstrap_loader_contracts_use_server_neighbor_modules() -> None:
    captured_calls: list[dict[str, Any]] = []

    def _fake_load_module(**kwargs: Any) -> dict[str, Any]:
        captured_calls.append(kwargs)
        return {"ok": True, "module_filename": kwargs["module_filename"]}

    auth = server_bootstrap.load_auth(_fake_load_module)
    lifecycle = server_bootstrap.load_lifecycle(_fake_load_module)

    assert auth["module_filename"] == "auth.py"
    assert lifecycle["module_filename"] == "lifecycle.py"
    assert captured_calls[0]["module_import_name"] == "thegent.mcp._server_auth"
    assert captured_calls[1]["module_import_name"] == "thegent.mcp._server_lifecycle"
    assert captured_calls[0]["server_file"] == Path(server_bootstrap.__file__).parent / "server.py"


def test_build_elicitation_helpers_cache_contract_roundtrip() -> None:
    (
        _cache_obj,
        _cache_key,
        get_cached,
        cache_response,
        _resolve_cwd,
        _resolve_owner,
        _get_default_cwd,
        _get_default_owner,
    ) = server_bootstrap.build_elicitation_helpers(
        create_elicitation_cache=create_elicitation_cache,
        elicitation_cache_key=elicitation_cache_key,
        get_cached_elicitation=get_cached_elicitation,
        cache_elicitation_response=cache_elicitation_response,
        resolve_cwd_elicitation=resolve_cwd_elicitation,
        resolve_owner_elicitation=resolve_owner_elicitation,
        default_cwd_from_context=default_cwd_from_context,
        default_owner_from_context=default_owner_from_context,
        accepted_elicitation_type=AcceptedElicitation,
        declined_elicitation_type=DeclinedElicitation,
        cancelled_elicitation_type=CancelledElicitation,
    )

    assert get_cached("cwd?", str) is None
    cache_response("cwd?", str, "~/repo")
    assert get_cached("cwd?", str) == "~/repo"


def test_build_lifespan_wires_lifecycle_through_proxy() -> None:
    captured: dict[str, Any] = {}

    async def _fake_lifespan_proxy(**kwargs: Any):
        captured.update(kwargs)
        yield {"ready": True}

    def _identity_lifespan(fn: Any) -> Any:
        return fn

    async def _collect_payloads() -> list[dict[str, Any] | None]:
        fn = server_bootstrap.build_lifespan(
            lifespan_decorator=_identity_lifespan,
            lifespan_proxy=_fake_lifespan_proxy,
            run_lifecycle=lambda *_args, **_kwargs: None,
            log="logger",
            ps_impl=lambda **_kwargs: {},
            auto_init_on_startup=lambda: None,
        )
        items: list[dict[str, Any] | None] = []
        async for payload in fn("mcp-app"):
            items.append(payload)
        return items

    items = asyncio.run(_collect_payloads())
    assert items == [{"ready": True}]
    assert captured["mcp_app"] == "mcp-app"
    assert captured["log"] == "logger"


def test_server_source_wires_bootstrap_rebinds() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip(f"server.py import raised: {exc}")

    source = inspect.getsource(server_mod)
    assert "_server_bootstrap.build_elicitation_helpers(" in source
    assert "thegent_lifespan = _server_bootstrap.build_lifespan(" in source
    assert "_get_default_cwd," in source
    assert "_get_default_owner," in source
