"""WP-29003: Human-in-the-Loop Moral Arbitration.
Provides a UI interface for humans to resolve moral dilemmas encountered by agents.
"""

import logging
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class MoralDilemma(BaseModel):
    """Represents a moral conflict that needs arbitration."""

    id: str
    description: str
    conflicting_principles: list[str]
    proposed_options: list[dict[str, Any]]
    context: dict[str, Any]


class ArbitrationResult(BaseModel):
    """The result of human moral arbitration."""

    dilemma_id: str
    selected_option_id: str
    reasoning: str
    arbitrator_id: str


class MoralUI:
    """Manages the UI flow for moral arbitration."""

    def __init__(self) -> None:
        self.active_dilemmas: dict[str, MoralDilemma] = {}

    def present_dilemma(self, dilemma: MoralDilemma) -> None:
        """Register a dilemma for human review."""
        _log.info("Presenting moral dilemma for arbitration: %s", dilemma.id)
        self.active_dilemmas[dilemma.id] = dilemma
        # In a real UI, this would push to a dashboard or terminal

    def resolve_dilemma(self, result: ArbitrationResult) -> bool:
        """Apply the human decision to a pending dilemma."""
        if result.dilemma_id not in self.active_dilemmas:
            _log.warning("Attempted to resolve unknown dilemma: %s", result.dilemma_id)
            return False

        _log.info("Moral dilemma %s resolved by human: %s", result.dilemma_id, result.selected_option_id)
        del self.active_dilemmas[result.dilemma_id]
        return True
