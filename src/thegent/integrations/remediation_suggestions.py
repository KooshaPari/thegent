"""Deterministic failure remediation suggestions for sync flows.

# @trace WL-262
"""

from __future__ import annotations


_SUGGESTIONS = {
    "AUTH_MISSING": "Set required credentials and re-run sync doctor before retrying.",
    "AUTH_AMBIGUOUS": "Remove duplicate credential sources and keep one explicit auth source.",
    "RATE_LIMIT": "Backoff and retry with reduced batch size; enable connector cooldown window.",
    "CONFLICT_SURFACE": "Run conflict triage command and resolve stale conflicts before write phase.",
    "REMOTE_5XX": "Pause connector writes and retry read-only mode to confirm remote health.",
    "CHECKPOINT_MISMATCH": "Run restore verifier against latest checkpoint before resuming writes.",
}



def suggest_remediation(failure_code: str) -> str:
    """Return deterministic remediation guidance for known sync failures."""
    if not failure_code or not failure_code.strip():
        raise ValueError("failure_code must be non-empty")

    code = failure_code.strip().upper()
    return _SUGGESTIONS.get(code, "Inspect sync logs, run doctor, and retry with dry-run enabled.")
