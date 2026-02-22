# @trace WL-120 wave-x
"""Regression checks for provider/model tool extraction from mcp/server.py."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

_MODULE_PATH = Path(__file__).parents[2] / "src" / "thegent" / "mcp" / "server" / "tools_provider_models.py"
_MODULE_KEY = "thegent.mcp._server_tools_provider_models_test"


def _import_extracted_module() -> types.ModuleType:
    """Import extraction module directly because server/ is not a package."""
    if _MODULE_KEY in sys.modules:
        return sys.modules[_MODULE_KEY]

    spec = importlib.util.spec_from_file_location(_MODULE_KEY, _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {_MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_KEY] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_provider_model_extracted_module_imports() -> None:
    mod = _import_extracted_module()
    assert mod is not None
    assert callable(getattr(mod, "register_provider_model_tools", None))


def test_provider_model_registration_returns_expected_tools() -> None:
    mod = _import_extracted_module()
    registered: list[str] = []

    def _tool_decorator(*args: Any, **kwargs: Any):
        def _inner(fn: Any) -> Any:
            registered.append(fn.__name__)
            return fn

        return _inner

    mock_mcp = MagicMock()
    mock_mcp.tool = _tool_decorator

    result = mod.register_provider_model_tools(mcp=mock_mcp)

    assert isinstance(result, tuple)
    assert len(result) == 13
    expected = {
        "list_providers",
        "get_provider",
        "add_provider",
        "update_provider",
        "delete_provider",
        "list_credentials",
        "add_api_key",
        "remove_api_key",
        "validate_provider",
        "discover_models",
        "list_models",
        "add_model_alias",
        "remove_model_alias",
    }
    assert expected <= set(registered)


def test_server_module_still_exposes_provider_model_tool_names() -> None:
    try:
        import thegent.mcp.server as server_mod
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"server.py import raised: {exc}")

    for name in (
        "list_providers",
        "get_provider",
        "add_provider",
        "update_provider",
        "delete_provider",
        "list_credentials",
        "add_api_key",
        "remove_api_key",
        "validate_provider",
        "discover_models",
        "list_models",
        "add_model_alias",
        "remove_model_alias",
    ):
        assert hasattr(server_mod, name), f"server.py missing expected tool: {name}"
