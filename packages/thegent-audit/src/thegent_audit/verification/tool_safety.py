"""WP-25002: Safety Invariants for Tool Composition.
Analyzes chains of tool calls to ensure safety properties are maintained.
Prevents "compositional escalation" where benign tools combined produce unsafe effects.
"""

import logging

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class SafetyViolation(BaseModel):
    """Details of a detected safety invariant violation."""

    chain: list[str]  # List of tool_ids
    violated_invariant: str
    risk_score: float


class ToolSafetyChecker:
    """Verifies safety invariants across tool execution chains."""

    def __init__(self) -> None:
        # Define forbidden transitions/compositions
        self.forbidden_compositions = {
            ("read_file", "broadcast_network"): "Potential data exfiltration chain.",
            ("get_credentials", "write_file"): "Credential leakage to disk.",
            ("shell_exec", "escalate_privileges"): "Unauthorized privilege escalation.",
        }

    def analyze_chain(self, tool_chain: list[str]) -> list[SafetyViolation]:
        """Analyze a sequence of tool calls for safety violations."""
        violations = []

        _log.info("Analyzing safety invariants for tool chain: %s", " -> ".join(tool_chain))

        # Check pairwise transitions
        for i in range(len(tool_chain) - 1):
            pair = (tool_chain[i], tool_chain[i + 1])
            if pair in self.forbidden_compositions:
                violations.append(
                    SafetyViolation(
                        chain=list(pair), violated_invariant=self.forbidden_compositions[pair], risk_score=0.9
                    )
                )

        # Check global chain properties (e.g. max destructive actions)
        destructive_count = sum(1 for t in tool_chain if t in ["delete_file", "purge_data", "drop_table"])
        if destructive_count > 2:
            violations.append(
                SafetyViolation(
                    chain=tool_chain,
                    violated_invariant="Excessive destructive actions in a single chain.",
                    risk_score=0.8,
                )
            )

        return violations

    def check_pre_flight(self, proposed_chain: list[str]) -> bool:
        """Pre-flight check for a proposed tool chain."""
        violations = self.analyze_chain(proposed_chain)
        if violations:
            for v in violations:
                _log.error("SAFETY VIOLATION: %s (Risk: %.2f)", v.violated_invariant, v.risk_score)
            return False
        return True
