"""Autosync onboarding wizard for setup workflow.

# @trace WL-218
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class OnboardingStep:
    """Represents a single step in the onboarding process.

    Attributes:
        step_id: Unique identifier for the step.
        title: Display title for the step.
        description: Detailed description of the step.
        completed: Whether the step has been completed.
    """

    step_id: str
    title: str
    description: str
    completed: bool = False


class OnboardingWizard:
    """Wizard to manage autosync onboarding steps."""

    STEPS: ClassVar[list[dict]] = [
        {
            "step_id": "configure_connectors",
            "title": "Configure Connectors",
            "description": "Set up and configure data source connectors",
        },
        {
            "step_id": "validate_auth",
            "title": "Validate Authentication",
            "description": "Verify credentials and authentication for connectors",
        },
        {
            "step_id": "run_startup_check",
            "title": "Run Startup Check",
            "description": "Execute initial validation checks",
        },
        {
            "step_id": "set_mapping",
            "title": "Set Field Mapping",
            "description": "Configure field mappings between source and target",
        },
        {
            "step_id": "take_baseline_snapshot",
            "title": "Take Baseline Snapshot",
            "description": "Create initial data snapshot for comparison",
        },
        {
            "step_id": "enable_autosync",
            "title": "Enable Autosync",
            "description": "Activate automatic synchronization",
        },
    ]

    def __init__(self) -> None:
        """Initialize the onboarding wizard."""
        self._completed_steps: set[str] = set()

    def get_steps(self) -> list[OnboardingStep]:
        """Get all onboarding steps.

        Returns:
            List of OnboardingStep objects with current completion status.
        """
        steps = []
        for step_dict in self.STEPS:
            steps.append(
                OnboardingStep(
                    step_id=step_dict["step_id"],
                    title=step_dict["title"],
                    description=step_dict["description"],
                    completed=step_dict["step_id"] in self._completed_steps,
                )
            )
        return steps

    def complete_step(self, step_id: str) -> None:
        """Mark a step as completed.

        Args:
            step_id: The ID of the step to complete.

        Raises:
            KeyError: If the step_id does not exist.
        """
        valid_step_ids = {s["step_id"] for s in self.STEPS}
        if step_id not in valid_step_ids:
            raise KeyError(f"Step '{step_id}' not found in onboarding wizard")
        self._completed_steps.add(step_id)

    def next_incomplete(self) -> OnboardingStep | None:
        """Get the first incomplete step.

        Returns:
            The first incomplete OnboardingStep, or None if all steps completed.
        """
        for step in self.get_steps():
            if not step.completed:
                return step
        return None

    def is_complete(self) -> bool:
        """Check if all steps are completed.

        Returns:
            True if all steps are completed, False otherwise.
        """
        return len(self._completed_steps) == len(self.STEPS)

    def progress(self) -> tuple[int, int]:
        """Get progress as (completed, total).

        Returns:
            Tuple of (number_completed, total_steps).
        """
        return (len(self._completed_steps), len(self.STEPS))
