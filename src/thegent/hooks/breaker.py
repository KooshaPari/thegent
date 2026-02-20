"""Implement breaker-check/record/reset subcommands (circuit breaker)."""

import logging
from datetime import UTC, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class BreakerSubcommands:
    """Circuit breaker subcommands."""

    def __init__(self) -> None:
        """Initialize breaker subcommands."""
        self.breakers: dict[str, dict[str, Any]] = {}

    def check(self, breaker_id: str) -> dict[str, Any]:
        """Check circuit breaker status.

        Args:
            breaker_id: Breaker identifier

        Returns:
            Breaker status
        """
        breaker = self.breakers.get(breaker_id, {})
        return {
            "id": breaker_id,
            "state": breaker.get("state", "closed"),
            "failures": breaker.get("failures", 0),
            "last_failure": breaker.get("last_failure"),
        }

    def record(self, breaker_id: str, success: bool) -> None:
        """Record breaker event.

        Args:
            breaker_id: Breaker identifier
            success: Whether operation succeeded
        """
        if breaker_id not in self.breakers:
            self.breakers[breaker_id] = {
                "state": "closed",
                "failures": 0,
            }

        breaker = self.breakers[breaker_id]
        if not success:
            breaker["failures"] += 1
            breaker["last_failure"] = datetime.now(UTC).isoformat()
            if breaker["failures"] >= 5:
                breaker["state"] = "open"
                logger.warning(f"Breaker {breaker_id} opened")
        else:
            breaker["failures"] = 0
            breaker["state"] = "closed"

    def reset(self, breaker_id: str) -> None:
        """Reset circuit breaker.

        Args:
            breaker_id: Breaker identifier
        """
        if breaker_id in self.breakers:
            self.breakers[breaker_id] = {
                "state": "closed",
                "failures": 0,
            }
            logger.info(f"Reset breaker {breaker_id}")
