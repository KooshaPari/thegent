"""Prompt constraint helpers extracted from cli.commands.impl (WL-125)."""

from __future__ import annotations

# AUDIT-N+16 (WL-125 closure): default seconds-per-tool-call budget used by
# :func:`inject_time_constraint` when callers don't override it. Exposed at
# module scope so ``thegent.cli.commands.impl._inject_time_constraint`` can
# forward the constant value verbatim (and tests can monkeypatch it).
# NOTE: defaults to 2.3 to match the AUDIT-N+9/N+11 observability contract;
# callers that need the larger 30s budget should pass the value explicitly.
SECONDS_PER_TOOL_CALL: float = 2.3


def inject_time_constraint(
    *,
    prompt: str,
    timeout: int,
    seconds_per_tool_call: float,
    summary_mode: bool = True,
) -> str:
    """Append timeout-aware tool budget guidance to an agent prompt."""
    n_calls = max(1, int(timeout / seconds_per_tool_call))
    suffix = (
        f"\n\n[TIME CONSTRAINT: You have approximately {n_calls} tool calls (~{timeout}s). "
        "When done or when approaching this limit, wrap up and report. "
        "Do not start new multi-step work.]"
    )
    if summary_mode:
        suffix += (
            "\n\n[OUTPUT FORMAT: End your response with a brief worker status report: "
            "**Summary** (1–2 sentences), **Items Done** (bullet list), **Issues** (if any), "
            "**Next Steps** (bullet list). Use markdown. This is the primary output shown.]"
        )
    return prompt + suffix


__all__ = ["inject_time_constraint", "SECONDS_PER_TOOL_CALL"]
