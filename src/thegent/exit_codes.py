"""Exit code constants and human-readable descriptions for CI/automation consumers."""

# Standard exit codes used by thegent (aligned with bash timeout: 124 = timeout)
EXIT_TIMEOUT = 124
EXIT_HEALTH_GATE_FAILED = 2

# Human-readable messages for common exit codes (for stop hooks, CI logs, etc.)
EXIT_CODE_MESSAGES: dict[int, str] = {
    EXIT_TIMEOUT: (
        "Operation timed out: the command exceeded the maximum allowed duration. "
        "For logs/wait: the session may have exited or still be running. "
        "For agent runs: the model did not complete within the timeout window."
    ),
    EXIT_HEALTH_GATE_FAILED: (
        "Governance gate failed: session contract health check did not pass. "
        "One or more sessions are blocked, unhealthy, or below the minimum healthy ratio. "
        "Review the health report for details."
    ),
}


def get_exit_message(code: int) -> str | None:
    """Return a human-readable description for a known exit code, or None."""
    return EXIT_CODE_MESSAGES.get(code)
