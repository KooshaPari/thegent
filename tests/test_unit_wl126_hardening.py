"""WL-126 hardening tests for thegent.mcp re-export surface."""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# Import everything from the two public modules
# ---------------------------------------------------------------------------
from thegent.mcp import (
    hotreload,
    server_cache_elicitation_response,
    server_create_elicitation_cache,
    server_default_cwd_from_context,
    server_default_owner_from_context,
    server_elicitation_cache_key,
    server_error_result,
    server_get_cached_elicitation,
    server_load_module,
    server_resolve_cwd_elicitation,
    server_resolve_owner_elicitation,
    server_stable_json,
    server_tools_workstream_lsp,
)
from thegent.mcp.server_catalog_tools import (
    invoke_catalog_tool,
    register_catalog_tool,
    thegent_list_operations_impl,
)


# ---------------------------------------------------------------------------
# __init__.py symbol presence & callability
# ---------------------------------------------------------------------------
class TestMcpInitSymbols:
    """Every symbol in mcp.__all__ must exist and be callable."""

    def test_server_cache_elicitation_response_callable(self) -> None:
        assert callable(server_cache_elicitation_response)

    def test_server_create_elicitation_cache_callable(self) -> None:
        assert callable(server_create_elicitation_cache)

    def test_server_default_cwd_from_context_callable(self) -> None:
        assert callable(server_default_cwd_from_context)

    def test_server_default_owner_from_context_callable(self) -> None:
        assert callable(server_default_owner_from_context)

    def test_server_elicitation_cache_key_callable(self) -> None:
        assert callable(server_elicitation_cache_key)

    def test_server_error_result_callable(self) -> None:
        assert callable(server_error_result)

    def test_server_get_cached_elicitation_callable(self) -> None:
        assert callable(server_get_cached_elicitation)

    def test_server_load_module_callable(self) -> None:
        assert callable(server_load_module)

    def test_server_resolve_cwd_elicitation_callable(self) -> None:
        assert callable(server_resolve_cwd_elicitation)

    def test_server_resolve_owner_elicitation_callable(self) -> None:
        assert callable(server_resolve_owner_elicitation)

    def test_server_stable_json_callable(self) -> None:
        assert callable(server_stable_json)

    def test_server_tools_workstream_lsp_callable(self) -> None:
        assert callable(server_tools_workstream_lsp)

    def test_hotreload_callable(self) -> None:
        assert callable(hotreload)


# ---------------------------------------------------------------------------
# server_stable_json deterministic output
# ---------------------------------------------------------------------------
class TestServerStableJson:
    """server_stable_json must produce deterministic, sorted-key output."""

    def test_sorted_keys(self) -> None:
        payload = {"z": 1, "a": 2, "m": 3}
        result = server_stable_json(payload)
        parsed = json.loads(result)
        keys = list(parsed.keys())
        assert keys == sorted(keys)

    def test_deterministic_across_calls(self) -> None:
        payload = {"b": [3, 1], "a": {"y": 2, "x": 1}}
        first = server_stable_json(payload)
        second = server_stable_json(payload)
        assert first == second

    def test_indent_two(self) -> None:
        result = server_stable_json({"key": "value"})
        # indent=2 means the second line should start with 2 spaces
        lines = result.splitlines()
        assert lines[1].startswith("  ")


# ---------------------------------------------------------------------------
# server_error_result envelope shape
# ---------------------------------------------------------------------------
class TestServerErrorResult:
    """server_error_result must return the expected envelope."""

    def test_envelope_shape(self) -> None:
        result = server_error_result("something broke")
        assert result == {"ok": False, "error": "something broke"}

    def test_envelope_with_extra_kwargs(self) -> None:
        result = server_error_result("fail", code=42, detail="nested")
        assert result["ok"] is False
        assert result["error"] == "fail"
        assert result["code"] == 42
        assert result["detail"] == "nested"


# ---------------------------------------------------------------------------
# server_load_module can import a stdlib module
# ---------------------------------------------------------------------------
class TestServerLoadModule:
    """server_load_module must successfully import stdlib modules."""

    def test_import_json(self) -> None:
        mod = server_load_module("json")
        assert mod is not None
        assert hasattr(mod, "dumps")

    def test_import_os(self) -> None:
        mod = server_load_module("os")
        assert mod is not None
        assert hasattr(mod, "getcwd")


# ---------------------------------------------------------------------------
# thegent_list_operations_impl envelope
# ---------------------------------------------------------------------------
class TestListOperationsImpl:
    """thegent_list_operations_impl must return the expected envelope."""

    def test_empty_envelope(self) -> None:
        result = thegent_list_operations_impl()
        assert result == {"operations": [], "count": 0}

    def test_accepts_args(self) -> None:
        result = thegent_list_operations_impl("extra", key="val")
        assert result["operations"] == []
        assert result["count"] == 0


# ---------------------------------------------------------------------------
# register_catalog_tool / invoke_catalog_tool callability
# ---------------------------------------------------------------------------
class TestCatalogToolFunctions:
    """register_catalog_tool and invoke_catalog_tool must be callable."""

    def test_register_catalog_tool_callable(self) -> None:
        assert callable(register_catalog_tool)

    def test_register_catalog_tool_returns_envelope(self) -> None:
        result = register_catalog_tool("my_tool", description="a tool")
        assert result["registered"] is True
        assert result["tool_name"] == "my_tool"
        assert result["description"] == "a tool"

    def test_invoke_catalog_tool_callable(self) -> None:
        assert callable(invoke_catalog_tool)

    def test_invoke_catalog_tool_returns_envelope(self) -> None:
        result = invoke_catalog_tool("my_tool", args={"x": 1})
        assert result["ok"] is True
        assert result["tool_name"] == "my_tool"
        assert result["args"] == {"x": 1}
