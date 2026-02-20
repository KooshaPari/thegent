"""Agent workflow for auto-populating documentation."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AgentWorkflow:
    """Workflow for agents to auto-populate documentation."""

    def __init__(self) -> None:
        """Initialize agent workflow."""
        self.steps: list[dict[str, Any]] = []

    def register_step(self, name: str, func: callable, dependencies: list[str] | None = None) -> None:
        """Register a workflow step.

        Args:
            name: Step name
            func: Step function
            dependencies: List of step names this depends on
        """
        self.steps.append(
            {
                "name": name,
                "func": func,
                "dependencies": dependencies or [],
            }
        )
        logger.info(f"Registered workflow step: {name}")

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the workflow.

        Args:
            context: Execution context

        Returns:
            Execution results
        """
        results = {}
        executed = set()

        # Topological sort to execute in dependency order
        while len(executed) < len(self.steps):
            progress = False
            for step in self.steps:
                if step["name"] in executed:
                    continue

                # Check if all dependencies are executed
                if all(dep in executed for dep in step["dependencies"]):
                    logger.info(f"Executing step: {step['name']}")
                    try:
                        result = step["func"](context)
                        results[step["name"]] = result
                        executed.add(step["name"])
                        progress = True
                    except Exception as e:
                        logger.error(f"Error in step {step['name']}: {e}")
                        results[step["name"]] = {"error": str(e)}
                        executed.add(step["name"])
                        progress = True

            if not progress:
                logger.error("Circular dependency or missing step detected")
                break

        return results

    def create_docgen_workflow(self) -> "AgentWorkflow":
        """Create a standard documentation generation workflow.

        Returns:
            Configured workflow
        """
        workflow = AgentWorkflow()

        # Register standard steps
        workflow.register_step(
            "scan_structure",
            lambda ctx: {"files": list(Path(ctx.get("docs_root", ".")).rglob("*.md"))},
        )

        workflow.register_step(
            "generate_sidebar",
            lambda ctx: {"sidebar": []},
            dependencies=["scan_structure"],
        )

        workflow.register_step(
            "generate_api_docs",
            lambda ctx: {"api_docs": []},
            dependencies=["scan_structure"],
        )

        workflow.register_step(
            "generate_llm_output",
            lambda ctx: {"llm_files": []},
            dependencies=["generate_api_docs"],
        )

        return workflow
