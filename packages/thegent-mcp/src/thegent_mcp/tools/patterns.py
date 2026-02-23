"""Reusable FastMCP tool patterns using elicitation and Context API.

Provides higher-order decorator patterns for tool authors:

- confirm_before_action: ask user to confirm before executing the wrapped tool
- progress_with_fallback: report progress via ctx.report_progress; fallback on error
- choice_with_retry: present choices via elicit_choice; retry on invalid/None selection
- retry_on_error: retry tool on specified exceptions using tenacity exponential backoff
- ToolAborted: exception raised when user aborts a tool action

Usage example::

    from thegent.mcp_tool_patterns import confirm_before_action, ToolAborted

    @confirm_before_action("Delete session {session_id}?")
    async def thegent_delete_session(session_id: str, ctx=None):
        ...  # only runs if user confirms

# @trace FR-MCP-PATTERNS-001
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from fastmcp.tools.tool import ToolResult
from tenacity import retry, stop_after_attempt, wait_random_exponential

from thegent.mcp.tools.elicitation import elicit_choice, elicit_confirmation

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ToolAborted exception
# ---------------------------------------------------------------------------


class ToolAborted(Exception):
    """Raised when a user aborts a tool action via elicitation.

    Tool authors should catch this at the boundary and return an appropriate
    ToolResult payload rather than letting it propagate as a tool error.
    """


# ---------------------------------------------------------------------------
# confirm_before_action
# ---------------------------------------------------------------------------


def confirm_before_action(action_description: str) -> Callable:
    """Decorator: ask the user to confirm before executing the wrapped tool.

    The action_description is a format string that may reference any keyword
    arguments of the wrapped function (e.g. "Delete session {session_id}?").
    If the user confirms, the wrapped function runs normally. If the user
    declines or cancels, ToolAborted is raised instead of calling the function.

    The decorator expects the wrapped function to accept a ``ctx`` keyword
    argument (FastMCP Context). If ctx is None or elicitation is unavailable,
    the wrapped function runs without confirmation (fail-open behaviour keeps
    non-interactive clients working).

    Args:
        action_description: Format string describing the action. May reference
            keyword arguments of the wrapped function by name.

    Returns:
        Decorator that wraps an async tool function with confirmation flow.

    Raises:
        ToolAborted: If user declines or cancels the confirmation.

    Example::

        @confirm_before_action("Delete session {session_id}?")
        async def thegent_delete_session(session_id: str, ctx=None):
            ...

    # @trace FR-MCP-PATTERNS-001
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = kwargs.get("ctx")

            # Render description with available kwargs (best-effort)
            try:
                description = action_description.format(**kwargs)
            except (KeyError, IndexError):
                description = action_description

            if ctx is not None:
                confirmed = await elicit_confirmation(ctx, f"Confirm: {description}")
                if confirmed is None:
                    # Elicitation unavailable or cancelled — fail-open
                    _log.warning(
                        "confirm_before_action: elicitation unavailable or cancelled for '%s'; proceeding",
                        description,
                    )
                elif not confirmed:
                    raise ToolAborted(f"User aborted: {description}")

            return await fn(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# progress_with_fallback
# ---------------------------------------------------------------------------


def progress_with_fallback(
    total_steps: int,
    fallback_result: Any = None,
) -> Callable:
    """Decorator: report progress via ctx.report_progress at each step.

    Wraps an async tool function and injects a ``report_step`` async callable
    into the function's kwargs. Tool authors call ``await report_step(step, label)``
    to emit progress. If ctx or report_progress is unavailable, progress calls
    are silently swallowed.

    On unexpected exception, returns fallback_result (wrapped in a dict) instead
    of raising, so clients receive a degraded but non-error response.

    Args:
        total_steps: Denominator for progress fraction (used in report_progress).
        fallback_result: Value returned (as ``{"result": fallback_result,
            "fallback": true}``) when the function raises an unexpected exception.

    Returns:
        Decorator that wraps an async tool function with progress reporting.

    Example::

        @progress_with_fallback(total_steps=5)
        async def thegent_bulk_operation(items: list[str], ctx=None, report_step=None):
            for i, item in enumerate(items):
                await report_step(i + 1, f"Processing {item}")
                ...

    # @trace FR-MCP-PATTERNS-002
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = kwargs.get("ctx")
            steps_done: list[int] = []

            async def report_step(step: int, label: str = "") -> None:
                """Emit a progress update for the given step number."""
                steps_done.append(step)
                if ctx is None:
                    return
                report_fn = getattr(ctx, "report_progress", None)
                if report_fn is None:
                    return
                try:
                    progress = step / max(total_steps, 1)
                    await report_fn(progress=progress, total=1.0)
                    if label:
                        info_fn = getattr(ctx, "info", None)
                        if info_fn:
                            await info_fn(f"[{step}/{total_steps}] {label}")
                except Exception as exc:
                    _log.debug("progress_with_fallback: report_progress error: %s", exc)

            kwargs["report_step"] = report_step

            try:
                return await fn(*args, **kwargs)
            except ToolAborted:
                raise
            except Exception as exc:
                _log.warning(
                    "progress_with_fallback: caught exception in '%s': %s; returning fallback",
                    fn.__name__,
                    exc,
                )
                return {"result": fallback_result, "fallback": True, "error": str(exc)}

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# choice_with_retry
# ---------------------------------------------------------------------------


def choice_with_retry(
    options: list[str],
    prompt: str,
    max_retries: int = 3,
) -> Callable:
    """Decorator: present choices via elicit_choice and retry on None/invalid selection.

    Before calling the wrapped function, this decorator asks the user to
    select from ``options``. The chosen value is injected into kwargs as
    ``user_choice``. If the user declines or the response is not in ``options``,
    up to ``max_retries`` additional prompts are shown. After exhausting retries,
    ToolAborted is raised.

    Args:
        options: Non-empty list of string options to present.
        prompt: The prompt text shown to the user.
        max_retries: Maximum number of re-prompts before aborting. Default 3.

    Returns:
        Decorator that wraps an async tool function with interactive choice flow.

    Raises:
        ToolAborted: If user fails to make a valid selection after max_retries.
        ValueError: If options list is empty (detected at decoration time).

    Example::

        @choice_with_retry(["low", "medium", "high"], "Select priority level:")
        async def thegent_set_priority(item_id: str, ctx=None, user_choice=None):
            ...  # user_choice is the selected option

    # @trace FR-MCP-PATTERNS-003
    """
    if not options:
        raise ValueError("choice_with_retry: options list must not be empty")

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = kwargs.get("ctx")

            if ctx is None:
                # No ctx — inject None and let tool decide
                kwargs["user_choice"] = None
                return await fn(*args, **kwargs)

            chosen: str | None = None
            attempts = 0
            max_attempts = 1 + max_retries

            while attempts < max_attempts:
                attempts += 1
                retry_suffix = f" (attempt {attempts}/{max_attempts})" if attempts > 1 else ""
                value = await elicit_choice(ctx, f"{prompt}{retry_suffix}", options)

                if value is not None and value in options:
                    chosen = value
                    break

                if value is None:
                    _log.debug(
                        "choice_with_retry: elicitation declined/cancelled (attempt %d/%d)",
                        attempts,
                        max_attempts,
                    )
                else:
                    _log.debug(
                        "choice_with_retry: invalid selection '%s' not in options (attempt %d/%d)",
                        value,
                        attempts,
                        max_attempts,
                    )

            if chosen is None:
                raise ToolAborted(
                    f"User did not make a valid selection after {max_attempts} attempt(s). Options were: {options}"
                )

            kwargs["user_choice"] = chosen
            return await fn(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# retry_on_error
# ---------------------------------------------------------------------------


def retry_on_error(
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable:
    """Decorator: retry tool on specified exceptions with exponential backoff.

    Uses tenacity's wait_random_exponential for jitter-aware retries. Only
    exceptions in ``exceptions`` tuple trigger a retry; others propagate
    immediately. After ``max_attempts`` total attempts, the last exception
    is re-raised.

    Args:
        max_attempts: Total number of attempts (1 = no retry). Default 3.
        exceptions: Tuple of exception types that trigger a retry. Default (Exception,).

    Returns:
        Decorator that wraps an async tool function with tenacity retry logic.

    Example::

        @retry_on_error(max_attempts=3, exceptions=(OSError, TimeoutError))
        async def thegent_flaky_io(path: str, ctx=None):
            ...

    # @trace FR-MCP-PATTERNS-004
    """

    def decorator(fn: Callable) -> Callable:
        tenacity_retry = retry(
            stop=stop_after_attempt(max(max_attempts, 1)),
            wait=wait_random_exponential(multiplier=0.5, min=0.1, max=10),
            reraise=True,
            retry=_build_tenacity_retry_condition(exceptions),
        )

        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt_count: list[int] = [0]

            async def _attempt() -> Any:
                attempt_count[0] += 1
                _log.debug(
                    "retry_on_error: attempt %d/%d for '%s'",
                    attempt_count[0],
                    max_attempts,
                    fn.__name__,
                )
                return await fn(*args, **kwargs)

            retried = tenacity_retry(_attempt)
            return await retried()

        return wrapper

    return decorator


def _build_tenacity_retry_condition(
    exceptions: tuple[type[BaseException], ...],
) -> Any:
    """Build a tenacity retry condition that retries only on given exception types."""
    from tenacity import retry_any, retry_if_exception_type

    if len(exceptions) == 1:
        return retry_if_exception_type(exceptions[0])

    return retry_any(*(retry_if_exception_type(exc) for exc in exceptions))


# ---------------------------------------------------------------------------
# MCP tool registration
# ---------------------------------------------------------------------------


def register_tool_pattern_tools(mcp: Any) -> None:
    """Register example tools demonstrating the FastMCP tool patterns.

    Registers:
    - thegent_delete_session: uses @confirm_before_action
    - thegent_bulk_operation: uses @progress_with_fallback

    Args:
        mcp: The FastMCP application instance.
    """
    import json

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
        }
    )
    @confirm_before_action("Delete session {session_id}?")
    async def thegent_delete_session(
        session_id: str,
        ctx: Any = None,
    ) -> ToolResult:
        """Delete a session by ID after user confirmation.

        Uses confirm_before_action pattern: prompts the user before proceeding.
        Raises ToolAborted if user declines.

        Args:
            session_id: The session identifier to delete.
            ctx: FastMCP Context (injected automatically).

        Returns:
            JSON with deleted=true and session_id, or aborted=true if user declined.

        # @trace FR-MCP-PATTERNS-001
        """
        payload: dict[str, Any] = {
            "deleted": True,
            "session_id": session_id,
            "status": "success",
        }
        _log.info("thegent_delete_session: session_id=%s deleted", session_id)
        return ToolResult(
            content=json.dumps(payload).decode().decode(),
            structured_content=payload,
            meta={},
        )

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
        }
    )
    @progress_with_fallback(total_steps=5)
    async def thegent_bulk_operation(
        items: list[str],
        ctx: Any = None,
        report_step: Any = None,
    ) -> ToolResult:
        """Perform a bulk operation over a list of items with progress reporting.

        Uses progress_with_fallback pattern: calls report_step at each stage.
        Falls back gracefully on error rather than raising.

        Args:
            items: List of item identifiers to process.
            ctx: FastMCP Context (injected automatically).
            report_step: Injected by progress_with_fallback decorator — do not pass manually.

        Returns:
            JSON with processed count and list of results.

        # @trace FR-MCP-PATTERNS-002
        """
        results: list[dict[str, Any]] = []

        for i, item in enumerate(items[:5]):
            step_num = i + 1
            if report_step:
                await report_step(step_num, f"Processing item: {item}")
            await asyncio.sleep(0)
            results.append({"item": item, "status": "processed"})

        payload: dict[str, Any] = {
            "processed": len(results),
            "total": len(items),
            "results": results,
        }
        _log.info("thegent_bulk_operation: processed %d/%d items", len(results), len(items))
        return ToolResult(
            content=json.dumps(payload).decode().decode(),
            structured_content=payload,
            meta={},
        )

    _log.info(
        "registered tool pattern tools: %s, %s",
        thegent_delete_session.__name__,
        thegent_bulk_operation.__name__,
    )
