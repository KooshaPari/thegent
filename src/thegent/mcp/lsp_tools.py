"""WL-109: MCP-facing LSP tool adapters with strict input/output contracts."""

# @trace WL-109

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

_BACKEND_UNAVAILABLE_PREFIX = "LSP_BACKEND_UNAVAILABLE"


class LspToolAdapter(Protocol):
    """Protocol for pluggable LSP backends used by MCP tool wrappers."""

    def diagnostics(self, *, file_path: str) -> list[dict[str, Any]]: ...

    def symbol_lookup(self, *, symbol_name: str, file_path: str | None) -> list[dict[str, Any]]: ...

    def hover(self, *, file_path: str, line: int, character: int) -> dict[str, Any] | None: ...


@dataclass
class _UnavailableAdapter:
    def diagnostics(self, *, file_path: str) -> list[dict[str, Any]]:
        raise RuntimeError("No LSP adapter is configured for diagnostics.")

    def symbol_lookup(self, *, symbol_name: str, file_path: str | None) -> list[dict[str, Any]]:
        raise RuntimeError("No LSP adapter is configured for symbol lookup.")

    def hover(self, *, file_path: str, line: int, character: int) -> dict[str, Any] | None:
        raise RuntimeError("No LSP adapter is configured for hover.")


@dataclass
class _PythonAstAdapter:
    """Concrete local Python backend for WL-109 default diagnostics/symbol/hover."""

    def diagnostics(self, *, file_path: str) -> list[dict[str, Any]]:
        source = Path(file_path).read_text(encoding="utf-8")
        try:
            compile(source, file_path, "exec")
        except SyntaxError as exc:
            return [
                {
                    "source": "python-compile",
                    "severity": "error",
                    "message": exc.msg,
                    "line": int(exc.lineno or 1),
                    "character": max(int((exc.offset or 1) - 1), 0),
                    "file_path": file_path,
                }
            ]
        return []

    def symbol_lookup(self, *, symbol_name: str, file_path: str | None) -> list[dict[str, Any]]:
        if file_path is None:
            raise RuntimeError("Python AST adapter requires file_path for symbol lookup.")

        source = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path)

        matches: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef | ast.AsyncFunctionDef)) and node.name == symbol_name:
                kind = "function" if isinstance(node, ast.FunctionDef) else "async_function"
                matches.append(
                    {
                        "name": node.name,
                        "kind": kind,
                        "line": int(node.lineno),
                        "character": int(getattr(node, "col_offset", 0)),
                        "file_path": file_path,
                    }
                )
            elif isinstance(node, ast.ClassDef) and node.name == symbol_name:
                matches.append(
                    {
                        "name": node.name,
                        "kind": "class",
                        "line": int(node.lineno),
                        "character": int(getattr(node, "col_offset", 0)),
                        "file_path": file_path,
                    }
                )
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id == symbol_name:
                matches.append(
                    {
                        "name": node.id,
                        "kind": "variable",
                        "line": int(node.lineno),
                        "character": int(getattr(node, "col_offset", 0)),
                        "file_path": file_path,
                    }
                )
        return matches

    def hover(self, *, file_path: str, line: int, character: int) -> dict[str, Any] | None:
        source = Path(file_path).read_text(encoding="utf-8")
        lines = source.splitlines()
        if line >= len(lines):
            return None

        current_line = lines[line]
        if character > len(current_line):
            return None

        token = _token_at_position(current_line, character)
        if token is None:
            return None

        matches = self.symbol_lookup(symbol_name=token, file_path=file_path)
        if not matches:
            return {
                "symbol": token,
                "line": line,
                "character": character,
                "detail": "No local definition found in file.",
            }

        top = matches[0]
        return {
            "symbol": token,
            "line": line,
            "character": character,
            "detail": f"{top['kind']} {top['name']} defined at {top['line']}:{top['character']}",
            "definition": top,
        }


def _validate_existing_file(file_path: str) -> Path:
    candidate = Path(file_path).expanduser().resolve()
    if not candidate.exists() or not candidate.is_file():
        raise ValueError(f"File not found: {file_path}")
    return candidate


def _ensure_position(line: int, character: int) -> tuple[int, int]:
    if isinstance(line, bool):
        raise ValueError("line must be an integer, not bool")
    if isinstance(character, bool):
        raise ValueError("character must be an integer, not bool")
    if line < 0:
        raise ValueError("line must be >= 0")
    if character < 0:
        raise ValueError("character must be >= 0")
    return line, character


def _token_at_position(line_text: str, character: int) -> str | None:
    for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", line_text):
        if match.start() <= character < match.end():
            return match.group(0)
    return None


def _resolve_default_adapter(*, file_path: str | None) -> LspToolAdapter:
    forced = os.getenv("THGENT_LSP_ADAPTER", "").strip().lower()
    if forced:
        if forced == "python-ast":
            return _PythonAstAdapter()
        raise RuntimeError(f"Unsupported THGENT_LSP_ADAPTER '{forced}'.")

    if file_path is not None and Path(file_path).suffix.lower() == ".py":
        return _PythonAstAdapter()

    return _UnavailableAdapter()


def _normalize_backend_error(exc: RuntimeError, *, operation: str) -> RuntimeError:
    message = str(exc)
    if "No LSP adapter is configured" in message:
        return RuntimeError(
            f"{_BACKEND_UNAVAILABLE_PREFIX}: {operation} is unavailable because no backend is configured for this file type."
        )
    if "Unsupported THGENT_LSP_ADAPTER" in message:
        return RuntimeError(
            f"{_BACKEND_UNAVAILABLE_PREFIX}: {operation} is unavailable because THGENT_LSP_ADAPTER is unsupported."
        )
    return exc


def _normalize_diagnostic(
    diagnostic: dict[str, Any],
    *,
    index: int,
    fallback_file_path: str,
) -> dict[str, Any]:
    message = diagnostic.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError(f"LSP diagnostics[{index}] must include a non-empty 'message'.")

    line_raw = diagnostic.get("line", 1)
    line = _coerce_position_field(line_raw, field="line", index=index, default=1)
    line = max(line, 1)

    character_raw = diagnostic.get("character", 0)
    character = _coerce_position_field(character_raw, field="character", index=index, default=0)
    character = max(character, 0)

    severity_raw = diagnostic.get("severity", "warning")
    if isinstance(severity_raw, str):
        severity = severity_raw.strip().lower()
    else:
        severity = "warning"
    severity_aliases = {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "info",
    }
    severity = severity_aliases.get(severity, severity)
    if severity not in {"error", "warning", "info", "hint"}:
        severity = "warning"

    source_raw = diagnostic.get("source")
    source = source_raw.strip() if isinstance(source_raw, str) and source_raw.strip() else "lsp"

    file_path_raw = diagnostic.get("file_path")
    file_path = file_path_raw if isinstance(file_path_raw, str) and file_path_raw.strip() else fallback_file_path

    return {
        "source": source,
        "severity": severity,
        "message": message.strip(),
        "line": line,
        "character": character,
        "file_path": file_path,
    }


def _coerce_position_field(raw: Any, *, field: str, index: int, default: int) -> int:
    if isinstance(raw, bool):
        raise ValueError(f"LSP diagnostics[{index}].{field} must be an integer-like value.")
    if isinstance(raw, (int | float)):
        return int(raw)
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return default
        try:
            return int(text)
        except ValueError as exc:
            raise ValueError(f"LSP diagnostics[{index}].{field} must be integer-like; got {raw!r}.") from exc
    return default


def _normalize_symbol_match(
    match: dict[str, Any],
    *,
    index: int,
    fallback_file_path: str | None,
) -> dict[str, Any]:
    name = match.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"LSP symbol matches[{index}] must include a non-empty 'name'.")

    kind = match.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError(f"LSP symbol matches[{index}] must include a non-empty 'kind'.")

    file_path_raw = match.get("file_path")
    file_path = (
        file_path_raw.strip() if isinstance(file_path_raw, str) and file_path_raw.strip() else fallback_file_path
    )
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError(f"LSP symbol matches[{index}] must include a non-empty 'file_path'.")

    line_raw = match.get("line", 1)
    if isinstance(line_raw, float) and not line_raw.is_integer():
        raise ValueError(f"LSP symbol matches[{index}].line must be integer-like; got {line_raw!r}.")
    line = max(_coerce_position_field(line_raw, field="line", index=index, default=1), 1)
    character_raw = match.get("character", 0)
    if isinstance(character_raw, float) and not character_raw.is_integer():
        raise ValueError(f"LSP symbol matches[{index}].character must be integer-like; got {character_raw!r}.")
    character = max(_coerce_position_field(character_raw, field="character", index=index, default=0), 0)
    return {
        "name": name.strip(),
        "kind": kind.strip(),
        "file_path": file_path,
        "line": line,
        "character": character,
    }


def lsp_diagnostics(file_path: str, adapter: LspToolAdapter | None = None) -> dict[str, Any]:
    """Return normalized diagnostics for a file path."""
    resolved = _validate_existing_file(file_path)
    try:
        client = adapter or _resolve_default_adapter(file_path=str(resolved))
        diagnostics = client.diagnostics(file_path=str(resolved))
    except RuntimeError as exc:
        raise _normalize_backend_error(exc, operation="diagnostics") from exc
    if not isinstance(diagnostics, list):
        raise ValueError("LSP diagnostics adapter must return a list.")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(diagnostics):
        if not isinstance(item, dict):
            raise ValueError(f"LSP diagnostics[{index}] must be an object.")
        normalized.append(_normalize_diagnostic(item, index=index, fallback_file_path=str(resolved)))
    return {"file_path": str(resolved), "diagnostics": normalized}


def lsp_symbol_lookup(
    symbol_name: str,
    file_path: str | None = None,
    adapter: LspToolAdapter | None = None,
) -> dict[str, Any]:
    """Return normalized symbol lookup results."""
    symbol = symbol_name.strip()
    if not symbol:
        raise ValueError("symbol_name must be non-empty.")

    resolved_file: str | None = None
    if file_path is not None:
        resolved_file = str(_validate_existing_file(file_path))

    try:
        client = adapter or _resolve_default_adapter(file_path=resolved_file)
        matches = client.symbol_lookup(symbol_name=symbol, file_path=resolved_file)
    except RuntimeError as exc:
        raise _normalize_backend_error(exc, operation="symbol_lookup") from exc
    if not isinstance(matches, list):
        raise ValueError("LSP symbol adapter must return a list.")

    normalized_matches: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            raise ValueError(f"LSP symbol matches[{index}] must be an object.")
        normalized_matches.append(_normalize_symbol_match(match, index=index, fallback_file_path=resolved_file))

    payload: dict[str, Any] = {"symbol_name": symbol, "matches": normalized_matches}
    if resolved_file is not None:
        payload["file_path"] = resolved_file
    return payload


def lsp_hover(
    file_path: str,
    line: int,
    character: int,
    adapter: LspToolAdapter | None = None,
) -> dict[str, Any]:
    """Return normalized hover info for a source position."""
    resolved = _validate_existing_file(file_path)
    line_num, col_num = _ensure_position(line, character)
    try:
        client = adapter or _resolve_default_adapter(file_path=str(resolved))
        hover_payload = client.hover(file_path=str(resolved), line=line_num, character=col_num)
    except RuntimeError as exc:
        raise _normalize_backend_error(exc, operation="hover") from exc
    if hover_payload is not None and not isinstance(hover_payload, dict):
        raise ValueError("LSP hover adapter must return an object or null.")
    return {
        "file_path": str(resolved),
        "line": line_num,
        "character": col_num,
        "hover": hover_payload,
    }


# ---------------------------------------------------------------------------
# WL-109: Typed public contracts exposed via MCP tools
# ---------------------------------------------------------------------------


@dataclass
class Diagnostic:
    """Typed representation of a single LSP diagnostic item."""

    file_path: str
    line: int
    character: int
    severity: str  # "error" | "warning" | "info" | "hint"
    message: str
    source: str | None = None


@dataclass
class SymbolInfo:
    """Typed representation of a single LSP symbol match."""

    name: str
    kind: str
    file_path: str
    line: int


@dataclass
class HoverInfo:
    """Typed representation of LSP hover result for a source position."""

    contents: str
    range: dict[str, Any] | None = None


async def lsp_diagnostics_impl(file_path: str, *, adapter: LspToolAdapter | None = None) -> list[dict[str, Any]]:
    """Async MCP entry-point: return normalized diagnostics for a file.

    Raises RuntimeError if no LSP adapter is available for this file type.
    Raises ValueError if the file does not exist.
    Fail loudly: no silent fallback.
    """
    result = lsp_diagnostics(file_path, adapter)
    return result["diagnostics"]


async def lsp_symbol_lookup_impl(
    symbol_name: str,
    file_path: str | None = None,
    *,
    adapter: LspToolAdapter | None = None,
) -> list[dict[str, Any]]:
    """Async MCP entry-point: return normalized symbol lookup results.

    Raises RuntimeError if no LSP adapter is available.
    Raises ValueError if symbol_name is empty or file_path does not exist.
    Fail loudly: no silent fallback.
    """
    result = lsp_symbol_lookup(symbol_name, file_path, adapter)
    return result["matches"]


async def lsp_hover_impl(
    file_path: str,
    line: int,
    character: int,
    *,
    adapter: LspToolAdapter | None = None,
) -> dict[str, Any]:
    """Async MCP entry-point: return normalized hover info for a source position.

    Raises RuntimeError if no LSP adapter is available.
    Raises ValueError if file_path does not exist or coordinates are negative.
    Fail loudly: no silent fallback.
    """
    result = lsp_hover(file_path, line, character, adapter)
    return result
