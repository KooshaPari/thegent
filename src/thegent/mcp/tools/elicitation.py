"""MCP tools exposing FastMCP elicitation API for interactive user input.

Provides three composable primitives for requesting user input mid-execution:
- elicit_confirmation: yes/no boolean
- elicit_choice: single selection from a list
- elicit_text: free-form text entry

Each function uses FastMCP's built-in ctx.elicit() mechanism and handles
AcceptedElicitation / DeclinedElicitation / CancelledElicitation outcomes.

Graceful fallback: if ctx.elicit is unavailable (older FastMCP), returns None
with a structured warning instead of raising.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any

from fastmcp.tools.tool import ToolResult

if TYPE_CHECKING:
    from fastmcp import FastMCP

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: safe elicit wrapper
# ---------------------------------------------------------------------------


async def _safe_elicit(ctx: Any, message: str, response_type: Any) -> Any:
    """Call ctx.elicit, returning None with a warning if unavailable.

    Args:
        ctx: FastMCP Context object.
        message: Prompt message shown to the user.
        response_type: Type hint passed to ctx.elicit (str, bool, list[str], etc.).

    Returns:
        AcceptedElicitation | DeclinedElicitation | CancelledElicitation | None.
        Returns None only when ctx.elicit is not available (older FastMCP).
    """
    elicit_fn = getattr(ctx, "elicit", None)
    if elicit_fn is None:
        warnings.warn(
            "ctx.elicit is not available on this FastMCP version; elicitation returning None",
            stacklevel=3,
        )
        _log.warning("ctx.elicit unavailable; skipping elicitation for: %s", message)
        return None
    return await elicit_fn(message, response_type)


def _try_import_accepted_elicitation() -> type | None:
    """Import AcceptedElicitation without suppression; return None if unavailable."""
    try:
        from fastmcp.server.elicitation import AcceptedElicitation

        return AcceptedElicitation
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Public elicitation primitives
# ---------------------------------------------------------------------------


async def elicit_confirmation(ctx: Any, message: str) -> bool | None:
    """Ask the user a yes/no question and return a boolean.

    Uses FastMCP's ctx.elicit with response_type=bool. The MCP client
    presents a confirmation dialog; the result is unwrapped from the
    AcceptedElicitation wrapper.

    Args:
        ctx: FastMCP Context object (injected by CurrentContext).
        message: The yes/no question to ask.

    Returns:
        True if the user accepted/confirmed, False if they chose no,
        None if elicitation was declined/cancelled or unavailable.

    Example::

        result = await elicit_confirmation(ctx, "Delete all logs?")
        if result is None:
            return "Elicitation unavailable or cancelled"
        if result:
            delete_logs()
    """
    accepted_cls = _try_import_accepted_elicitation()

    result = await _safe_elicit(ctx, message, bool)
    if result is None:
        return None

    if accepted_cls is not None and isinstance(result, accepted_cls):
        return bool(result.data)

    _log.debug("elicit_confirmation: user declined or cancelled (action=%s)", getattr(result, "action", "unknown"))
    return None


async def elicit_choice(ctx: Any, message: str, options: list[str]) -> str | None:
    """Ask the user to pick one option from a list.

    Uses FastMCP's ctx.elicit with response_type as a list of strings
    (single-select mode). Returns the selected string.

    Args:
        ctx: FastMCP Context object (injected by CurrentContext).
        message: The question or instruction to display.
        options: Non-empty list of string options to present.

    Returns:
        The chosen string if accepted, None if declined/cancelled/unavailable.

    Raises:
        ValueError: If options list is empty.

    Example::

        model = await elicit_choice(ctx, "Select model:", ["gpt-4", "claude-3", "gemini"])
        if model is None:
            model = "gpt-4"  # sensible default
    """
    if not options:
        raise ValueError("elicit_choice: options list must not be empty")

    accepted_cls = _try_import_accepted_elicitation()

    result = await _safe_elicit(ctx, message, options)
    if result is None:
        return None

    if accepted_cls is not None and isinstance(result, accepted_cls):
        return str(result.data)

    _log.debug("elicit_choice: user declined or cancelled (action=%s)", getattr(result, "action", "unknown"))
    return None


async def elicit_text(ctx: Any, message: str, placeholder: str = "") -> str | None:
    """Ask the user for free-form text input.

    Uses FastMCP's ctx.elicit with response_type=str. The placeholder
    is prepended to the message if provided (FastMCP does not natively
    support placeholder hints in the schema yet, so it is included inline).

    Args:
        ctx: FastMCP Context object (injected by CurrentContext).
        message: The prompt/question to display.
        placeholder: Optional example or hint text shown inline in the prompt.

    Returns:
        The entered string if accepted, None if declined/cancelled/unavailable.

    Example::

        cwd = await elicit_text(ctx, "Enter working directory:", placeholder="/home/user/project")
        if cwd is None:
            cwd = str(Path.cwd())
    """
    accepted_cls = _try_import_accepted_elicitation()

    prompt = f"{message} (e.g. {placeholder})" if placeholder else message
    result = await _safe_elicit(ctx, prompt, str)
    if result is None:
        return None

    if accepted_cls is not None and isinstance(result, accepted_cls):
        return str(result.data)

    _log.debug("elicit_text: user declined or cancelled (action=%s)", getattr(result, "action", "unknown"))
    return None


async def elicit_structured(ctx: Any, message: str, model_class: type) -> Any | None:
    """Ask the user for structured input matching a Pydantic model (FR-MCP-ELICIT-001).

    Uses FastMCP's ctx.elicit with response_type=model_class. The MCP client
    presents a form based on the Pydantic model's schema.

    Args:
        ctx: FastMCP Context object (injected by CurrentContext).
        message: The prompt/instruction for the structured input.
        model_class: The Pydantic model class defining the expected structure.

    Returns:
        An instance of model_class if accepted, None if declined/cancelled/unavailable.
    """
    accepted_cls = _try_import_accepted_elicitation()

    result = await _safe_elicit(ctx, message, model_class)
    if result is None:
        return None

    if accepted_cls is not None and isinstance(result, accepted_cls):
        return result.data

    _log.debug("elicit_structured: user declined or cancelled (action=%s)", getattr(result, "action", "unknown"))
    return None


# ---------------------------------------------------------------------------
# MCP tool registration
# ---------------------------------------------------------------------------


def register_elicitation_tools(mcp: FastMCP) -> None:
    """Register elicitation helper tools on the FastMCP server.

    Exposes elicit_confirmation, elicit_choice, and elicit_text as
    first-class MCP tools so that agent orchestrators can trigger
    user elicitation flows via the standard MCP tool-call protocol.

    Args:
        mcp: The FastMCP application instance.
    """
    import json
    import time

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_elicit_confirmation(
        message: str,
        ctx: Any = None,
    ) -> ToolResult:
        """Ask the user a yes/no confirmation question mid-execution.

        Sends an elicitation request to the MCP client and awaits the user's
        response. Returns {"confirmed": true/false} on acceptance, or
        {"confirmed": null, "status": "declined"|"cancelled"|"unavailable"}
        otherwise.

        Args:
            message: The yes/no question to ask the user.
            ctx: FastMCP Context (injected automatically).
        """
        start = time.perf_counter()
        if ctx is None:
            _log.warning("thegent_elicit_confirmation called without ctx; returning unavailable")
            result_payload: dict[str, Any] = {"confirmed": None, "status": "unavailable"}
            return ToolResult(
                content=json.dumps(result_payload),
                structured_content=result_payload,
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )

        value = await elicit_confirmation(ctx, message)
        elapsed = int((time.perf_counter() - start) * 1000)
        if value is None:
            payload: dict[str, Any] = {"confirmed": None, "status": "declined_or_cancelled"}
        else:
            payload = {"confirmed": value, "status": "accepted"}
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_elicit_choice(
        message: str,
        options: list[str],
        ctx: Any = None,
    ) -> ToolResult:
        """Ask the user to select one option from a list mid-execution.

        Sends a single-select elicitation request to the MCP client. Returns
        {"choice": "<selected>", "status": "accepted"} or
        {"choice": null, "status": "declined"|"cancelled"|"unavailable"}.

        Args:
            message: The prompt/instruction for the selection.
            options: Non-empty list of strings to choose from.
            ctx: FastMCP Context (injected automatically).
        """
        start = time.perf_counter()
        if not options:
            error_payload: dict[str, Any] = {"error": "options must not be empty", "choice": None}
            return ToolResult(
                content=json.dumps(error_payload),
                structured_content=error_payload,
                meta={"execution_time_ms": 0},
            )

        if ctx is None:
            _log.warning("thegent_elicit_choice called without ctx; returning unavailable")
            unavail_payload: dict[str, Any] = {"choice": None, "status": "unavailable"}
            return ToolResult(
                content=json.dumps(unavail_payload),
                structured_content=unavail_payload,
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )

        value = await elicit_choice(ctx, message, options)
        elapsed = int((time.perf_counter() - start) * 1000)
        if value is None:
            payload2: dict[str, Any] = {"choice": None, "status": "declined_or_cancelled"}
        else:
            payload2 = {"choice": value, "status": "accepted"}
        return ToolResult(
            content=json.dumps(payload2),
            structured_content=payload2,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_elicit_text(
        message: str,
        placeholder: str = "",
        ctx: Any = None,
    ) -> ToolResult:
        """Ask the user for free-form text input mid-execution.

        Sends a text elicitation request to the MCP client. Returns
        {"text": "<entered>", "status": "accepted"} or
        {"text": null, "status": "declined"|"cancelled"|"unavailable"}.

        Args:
            message: The prompt/question to display to the user.
            placeholder: Optional example value shown inline in the prompt.
            ctx: FastMCP Context (injected automatically).
        """
        start = time.perf_counter()
        if ctx is None:
            _log.warning("thegent_elicit_text called without ctx; returning unavailable")
            unavail_payload3: dict[str, Any] = {"text": None, "status": "unavailable"}
            return ToolResult(
                content=json.dumps(unavail_payload3),
                structured_content=unavail_payload3,
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )

        value = await elicit_text(ctx, message, placeholder)
        elapsed = int((time.perf_counter() - start) * 1000)
        if value is None:
            payload3: dict[str, Any] = {"text": None, "status": "declined_or_cancelled"}
        else:
            payload3 = {"text": value, "status": "accepted"}
        return ToolResult(
            content=json.dumps(payload3),
            structured_content=payload3,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_elicit_structured(
        message: str,
        schema_json: str,
        ctx: Any = None,
    ) -> ToolResult:
        """Ask the user for structured input matching a JSON schema mid-execution.

        Sends a structured elicitation request to the MCP client. Returns
        {"data": <object>, "status": "accepted"} or
        {"data": null, "status": "declined"|"cancelled"|"unavailable"}.

        Args:
            message: The prompt/instruction for the structured input.
            schema_json: JSON string representing the expected Pydantic model schema.
            ctx: FastMCP Context (injected automatically).
        """
        import json

        from pydantic import create_model

        start = time.perf_counter()
        if ctx is None:
            unavail_payload4: dict[str, Any] = {"data": None, "status": "unavailable"}
            return ToolResult(
                content=json.dumps(unavail_payload4),
                structured_content=unavail_payload4,
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )

        try:
            schema = json.loads(schema_json)
            # Simple dynamic model creation from schema (minimal support)
            properties = schema.get("properties", {})
            # create_model expects field definitions as (type, ...) tuples
            fields: dict[str, Any] = dict.fromkeys(properties, (Any, ...))
            DynamicModel = create_model("DynamicElicitationModel", **fields)  # type: ignore[arg-type]
            value = await elicit_structured(ctx, message, DynamicModel)
        except Exception as e:
            _log.error("thegent_elicit_structured: error creating dynamic model: %s", e)
            error_payload: dict[str, Any] = {"data": None, "status": "error", "error": str(e)}
            return ToolResult(
                content=json.dumps(error_payload),
                structured_content=error_payload,
                meta={"execution_time_ms": 0},
            )

        elapsed = int((time.perf_counter() - start) * 1000)
        if value is None:
            payload4: dict[str, Any] = {"data": None, "status": "declined_or_cancelled"}
        else:
            # value is an instance of DynamicModel, convert to dict
            payload4 = {"data": value.model_dump() if hasattr(value, "model_dump") else value, "status": "accepted"}
        return ToolResult(
            content=json.dumps(payload4),
            structured_content=payload4,
            meta={"execution_time_ms": elapsed},
        )

    _log.info(
        "registered elicitation tools: thegent_elicit_confirmation, thegent_elicit_choice, thegent_elicit_text, thegent_elicit_structured"
    )
