"""Zero-Touch Operator Quick Start for onboarding.

WL-180: Zero-Touch Operator Quick Start
Provides quick start steps and progress tracking for zero-touch operator onboarding.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QuickStartStep:
    """A single step in the quick start guide."""

    step_id: str
    description: str
    completed: bool = False


class ZeroTouchQuickStart:
    """Quick start manager for zero-touch operator onboarding."""

    def __init__(self) -> None:
        """Initialize the zero-touch quick start."""
        self._steps: dict[str, QuickStartStep] = {}

    def add_step(self, step_id: str, description: str) -> QuickStartStep:
        """Add a step to the quick start guide.

        Args:
            step_id: Unique identifier for the step.
            description: Description of the step.

        Returns:
            The created QuickStartStep.
        """
        step = QuickStartStep(step_id=step_id, description=description)
        self._steps[step_id] = step
        return step

    def complete_step(self, step_id: str) -> None:
        """Mark a step as completed.

        Args:
            step_id: Unique identifier for the step.

        Raises:
            KeyError: If step not found.
        """
        if step_id not in self._steps:
            raise KeyError(f"Step not found: {step_id}")
        self._steps[step_id].completed = True

    def progress(self) -> tuple[int, int]:
        """Get progress as (completed_count, total_count).

        Returns:
            Tuple of (number of completed steps, total number of steps).
        """
        completed = sum(1 for step in self._steps.values() if step.completed)
        total = len(self._steps)
        return (completed, total)

    def render_checklist(self) -> str:
        """Render the quick start as a markdown checklist.

        Returns:
            Markdown formatted checklist string.
        """
        lines = []
        for step_id in sorted(self._steps.keys()):
            step = self._steps[step_id]
            checkbox = "[x]" if step.completed else "[ ]"
            lines.append(f"{checkbox} {step_id}: {step.description}")
        return "\n".join(lines)
