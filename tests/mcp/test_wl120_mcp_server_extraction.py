# @trace WL-120 B90-W2-D1
"""Tests for the WL-120 B90-W2-D1 mcp/server.py dynamic registry extraction.

Verifies:
1. The extracted module imports cleanly.
2. register_dynamic_registry_tools() is callable and returns a 3-tuple.
3. The server module still surfaces the three tool names via re-import
   (parity check: names exist and are callable in the registered FastMCP app).
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MODULE_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "thegent"
    / "mcp"
    / "server"
    / "tools_dynamic_registry.py"
)
_MODULE_KEY = "thegent.mcp._server_tools_dynamic_registry_test"


def _import_extracted_module() -> types.ModuleType:
    """Import the extracted dynamic registry module directly by file path.

    The server/ directory is NOT a Python package (server.py is the package
    entry point), so we must load via importlib.util.spec_from_file_location.
    """
    if _MODULE_KEY in sys.modules:
        return sys.modules[_MODULE_KEY]

    spec = importlib.util.spec_from_file_location(_MODULE_KEY, _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {_MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_KEY] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# D1-1: Extracted module imports cleanly
# ---------------------------------------------------------------------------


def test_extracted_module_imports_cleanly() -> None:
    """tools_dynamic_registry module must import without raising."""
    mod = _import_extracted_module()
    assert mod is not None, "Module failed to import"


def test_extracted_module_exports_register_function() -> None:
    """register_dynamic_registry_tools must be callable."""
    mod = _import_extracted_module()
    assert callable(getattr(mod, "register_dynamic_registry_tools", None)), (
        "register_dynamic_registry_tools not found or not callable"
    )


# ---------------------------------------------------------------------------
# D1-2: register_dynamic_registry_tools returns a 3-tuple of callables
# ---------------------------------------------------------------------------


def test_register_returns_three_callables() -> None:
    """register_dynamic_registry_tools must return exactly 3 callables."""
    mod = _import_extracted_module()

    # Build a minimal FastMCP mock that supports @mcp.tool() decoration.
    registered: list[str] = []

    def _tool_decorator(*args: Any, **kwargs: Any):
        """Mock @mcp.tool() that returns the decorated function unchanged."""
        def _inner(fn: Any) -> Any:
            registered.append(fn.__name__)
            return fn
        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator

    mock_sessions = MagicMock()
    mock_sessions._dynamic_registry = MagicMock()

    result = mod.register_dynamic_registry_tools(
        mcp=mock_mcp,
        server_tools_sessions=mock_sessions,
        error_result=MagicMock(),
    )

    assert isinstance(result, tuple), "Expected a tuple return"
    assert len(result) == 3, f"Expected 3 items, got {len(result)}"
    for item in result:
        assert callable(item), f"Expected callable, got {type(item)}"


def test_register_registers_expected_tool_names() -> None:
    """register_dynamic_registry_tools must register the three canonical tool names."""
    mod = _import_extracted_module()

    registered_names: list[str] = []

    def _tool_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered_names.append(fn.__name__)
            return fn
        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator
    mock_sessions = MagicMock()
    mock_sessions._dynamic_registry = MagicMock()

    mod.register_dynamic_registry_tools(
        mcp=mock_mcp,
        server_tools_sessions=mock_sessions,
        error_result=MagicMock(),
    )

    expected = {"thegent_register_tool", "thegent_complete_tool_call", "thegent_list_dynamic_tools"}
    assert expected <= set(registered_names), (
        f"Missing tool names: {expected - set(registered_names)}"
    )


# ---------------------------------------------------------------------------
# D1-3: server.py still exports the three tool names (parity check)
# ---------------------------------------------------------------------------


def test_server_module_still_has_dynamic_tool_names() -> None:
    """server.py must still expose thegent_register_tool etc. as module attributes."""
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:
        # If the full server fails to init (no live DB etc.), skip gracefully.
        import pytest
        pytest.skip(f"server.py import raised: {exc}")

    for name in ("thegent_register_tool", "thegent_complete_tool_call", "thegent_list_dynamic_tools"):
        assert hasattr(server_mod, name), (
            f"server.py missing expected tool name: {name}"
        )


def test_tool_loader_dynamic_registry_contract_is_stable() -> None:
    """server_tool_loader.load_tools_dynamic_registry should target the extracted module."""
    from thegent.mcp import server_tool_loader

    captured: dict[str, object] = {}

    def _fake_load_module(*, server_file: Path, module_filename: str, module_import_name: str, failure_message: str) -> object:
        captured["server_file"] = server_file
        captured["module_filename"] = module_filename
        captured["module_import_name"] = module_import_name
        captured["failure_message"] = failure_message
        return {"ok": True}

    result = server_tool_loader.load_tools_dynamic_registry(_fake_load_module)

    assert result == {"ok": True}
    assert isinstance(captured["server_file"], Path)
    assert captured["module_filename"] == "tools_dynamic_registry.py"
    assert captured["module_import_name"] == "thegent.mcp._server_tools_dynamic_registry"
    assert captured["failure_message"] == "Unable to load dynamic registry tool registrations"


def test_server_source_wires_dynamic_registry_loader_and_assignments() -> None:
    """server.py should wire the extracted loader and assign returned tool callables."""
    import thegent.mcp.server as server_mod

    source = inspect.getsource(server_mod)
    assert "_server_tools_dynamic_registry = _load_tools_dynamic_registry(_load_server_module_shared)" in source
    assert ") = _server_tools_dynamic_registry.register_dynamic_registry_tools(" in source
    assert "thegent_register_tool," in source
    assert "thegent_complete_tool_call," in source
    assert "thegent_list_dynamic_tools," in source


def test_server_source_keeps_impl_import_surface_for_command_routing() -> None:
    """server.py should keep importing the impl command functions used by MCP tools."""
    import thegent.mcp.server as server_mod

    source = inspect.getsource(server_mod)
    assert "from thegent.cli.commands.impl import (" in source
    for name in ("do_next_impl", "wait_next_impl", "incorporate_impl", "work_stream_claim_impl", "work_stream_complete_impl"):
        assert name in source, f"Expected {name} import in server.py impl surface"
