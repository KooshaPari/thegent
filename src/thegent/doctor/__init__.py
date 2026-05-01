"""STUB MODULE - thegent.doctor

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


class CheckResult:
    """Result of a doctor check."""

    def __init__(self, name: str, passed: bool, message: str = "") -> None:
        self.name = name
        self.passed = passed
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "message": self.message}


def _check_mcp_tools() -> list[CheckResult]:
    """Check MCP tools status."""
    return []


# Stub implementation - functionality not available
__all__ = ["CheckResult", "_check_mcp_tools"]
