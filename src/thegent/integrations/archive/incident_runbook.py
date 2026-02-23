"""Incident Runbook for incident response and rollback procedures.

# @trace WL-234
Provides structured incident response runbooks with ordered steps for operational
procedures like rollback, recovery, and escalation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunbookStep:
    """A single step in an incident runbook."""

    step_id: str
    title: str
    instructions: str


class IncidentRunbook:
    """Manages incident response runbooks with ordered steps."""

    def __init__(self) -> None:
        """Initialize the incident runbook."""
        self._steps: dict[str, RunbookStep] = {}
        self._step_order: list[str] = []

    def add_step(self, step_id: str, title: str, instructions: str) -> RunbookStep:
        """Add a step to the runbook.

        Args:
            step_id: Unique identifier for the step.
            title: Human-readable title for the step.
            instructions: Detailed instructions for this step.

        Returns:
            The created RunbookStep.
        """
        step = RunbookStep(step_id=step_id, title=title, instructions=instructions)
        self._steps[step_id] = step
        if step_id not in self._step_order:
            self._step_order.append(step_id)
        return step

    def get_step(self, step_id: str) -> RunbookStep:
        """Get a step by ID.

        Args:
            step_id: The step ID to retrieve.

        Returns:
            The RunbookStep with the given ID.

        Raises:
            KeyError: If the step ID does not exist.
        """
        return self._steps[step_id]

    def steps(self) -> list[RunbookStep]:
        """Get all steps in order.

        Returns:
            List of RunbookSteps in the order they were added.
        """
        return [self._steps[step_id] for step_id in self._step_order]

    def render_markdown(self) -> str:
        """Render the runbook as a numbered markdown list.

        Returns:
            Markdown-formatted string with numbered steps.
        """
        lines = []
        for i, step_id in enumerate(self._step_order, 1):
            step = self._steps[step_id]
            lines.append(f"{i}. **{step.title}** (`{step.step_id}`)")
            lines.append(f"   {step.instructions}")
            lines.append("")
        return "\n".join(lines)
