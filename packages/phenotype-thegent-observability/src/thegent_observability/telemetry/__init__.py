"""OTel GenAI instrumentation and run correlation (WP-Y6, NFR-013).

Provides OpenTelemetry spans with GenAI semantic conventions and run_id correlation
across orchestration, agent calls, and status. Re-exports from observability for
unified access.

Usage:
    from thegent_observability.telemetry import instrument_genai_call, instrument_run_bg_status

    with instrument_genai_call(agent_name="claude", model="claude-3-5-sonnet", run_id=run_id):
        ...
"""

from thegent_observability.observability.otel_instrumentation import (
    GEN_AI_REQUEST_MODEL,
    GEN_AI_SYSTEM,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    THEGENT_AGENT,
    THEGENT_CONFIDENCE,
    THEGENT_EXIT_CODE,
    THEGENT_LANE,
    THEGENT_MODEL,
    THEGENT_PROVIDER,
    THEGENT_SESSION_ID,
    instrument_genai_call,
    instrument_run_bg_status,
    instrument_run_bg_status_decorator,
    record_usage,
)

__all__ = [
    "GEN_AI_REQUEST_MODEL",
    "GEN_AI_SYSTEM",
    "GEN_AI_USAGE_INPUT_TOKENS",
    "GEN_AI_USAGE_OUTPUT_TOKENS",
    "THEGENT_AGENT",
    "THEGENT_CONFIDENCE",
    "THEGENT_EXIT_CODE",
    "THEGENT_LANE",
    "THEGENT_MODEL",
    "THEGENT_PROVIDER",
    "THEGENT_SESSION_ID",
    "instrument_genai_call",
    "instrument_run_bg_status",
    "instrument_run_bg_status_decorator",
    "record_usage",
]
