"""Context budget indicator for TUI status bar and ANSI CLI output.

# @trace WL-108
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thegent_agents.agents.base import RunResult

# ANSI color codes — intentionally self-contained; no external deps.
_ANSI_RESET = "\033[0m"
_ANSI_GREEN = "\033[32m"
_ANSI_YELLOW = "\033[33m"
_ANSI_RED = "\033[31m"

_COLOR_MAP: dict[str, str] = {
    "green": _ANSI_GREEN,
    "yellow": _ANSI_YELLOW,
    "red": _ANSI_RED,
}


@dataclass
class ContextBudget:
    """Computed context budget for a single agent run.

    # @trace WL-108
    """

    used: int
    max: int

    @property
    def ratio(self) -> float:
        """Fraction of context window consumed (0.0 – 1.0)."""
        if self.max <= 0:
            raise ValueError(f"context max must be > 0, got {self.max}")
        return self.used / self.max

    @property
    def color(self) -> str:
        """Severity color: 'green' (<60%), 'yellow' (<80%), 'red' (>=80%)."""
        r = self.ratio
        if r < 0.6:
            return "green"
        if r < 0.8:
            return "yellow"
        return "red"

    def format_bar(self, *, ansi: bool = True) -> str:
        """Format as ``[CTX: 12k/128k]`` with optional ANSI color escape codes.

        Args:
            ansi: When True (default), wrap output in ANSI color escapes.
                  Pass False for plain-text output (e.g. JSON serialisation).

        Returns:
            A string like ``[CTX: 12k/128k]``, optionally ANSI-colored.
        """
        from thegent_cli.tui.widgets.statusbar import compute_context_usage_display

        display, _css = compute_context_usage_display(self.used, self.max)
        bar = f"[CTX: {display}]"
        if not ansi:
            return bar
        ansi_code = _COLOR_MAP[self.color]
        return f"{ansi_code}{bar}{_ANSI_RESET}"


def context_budget_from_result(result: RunResult) -> ContextBudget | None:
    """Build a :class:`ContextBudget` from a :class:`~thegent.agents.base.RunResult`.

    Returns ``None`` when *result* does not carry full context token data
    (i.e. when either ``context_tokens_used`` or ``context_window_max`` is
    ``None`` or when ``context_window_max`` is zero).

    # @trace WL-108

    Args:
        result: The completed agent run result.

    Returns:
        A :class:`ContextBudget` instance, or ``None``.
    """
    if result.context_tokens_used is None or result.context_window_max is None:
        return None
    if result.context_tokens_used < 0:
        return None
    if result.context_window_max <= 0:
        return None
    return ContextBudget(used=result.context_tokens_used, max=result.context_window_max)


def context_budget_indicator(result: RunResult, *, ansi: bool = True) -> str | None:
    """Return a formatted ``[CTX: 12k/128k]`` indicator string for CLI/TUI use.

    Convenience wrapper around :func:`context_budget_from_result` and
    :meth:`ContextBudget.format_bar`.  Returns ``None`` when the result
    does not carry context token data.

    # @trace WL-108

    Args:
        result: The completed agent run result.
        ansi:   Forward to :meth:`ContextBudget.format_bar`.

    Returns:
        Formatted indicator string, or ``None``.
    """
    budget = context_budget_from_result(result)
    if budget is None:
        return None
    return budget.format_bar(ansi=ansi)
