"""WL-109: Typed MCP LSP tool implementations - server-layer thin wrapper.

Re-exports the typed dataclasses and async impl functions from thegent.mcp.lsp_tools
for server.py registration. This module is loaded by server.py via importlib.

The canonical implementations live in thegent.mcp.lsp_tools to allow direct
import in tests without requiring the server/ directory to be a Python package.

# @trace WL-109
"""

from __future__ import annotations

# Re-export typed contracts and async impls from the proper importable package.
# server.py loads this module via importlib and can call these symbols directly.
from thegent_protocols.mcp.lsp_tools import (
    Diagnostic,
    HoverInfo,
    LspToolAdapter,
    SymbolInfo,
    lsp_diagnostics_impl,
    lsp_hover_impl,
    lsp_symbol_lookup_impl,
)

__all__ = [
    "Diagnostic",
    "HoverInfo",
    "LspToolAdapter",
    "SymbolInfo",
    "lsp_diagnostics_impl",
    "lsp_hover_impl",
    "lsp_symbol_lookup_impl",
]
