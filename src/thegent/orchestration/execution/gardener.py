"""MEM-AUD-02: Memory-to-Doc Synthesis Agent.
Consolidates raw memory audit logs into formal project documentation.
"""

import logging
from pathlib import Path

from thegent.agents.registry import get_runner
from thegent.orchestration.state.memory import MemorySystem

logger = logging.getLogger(__name__)


class Gardener:
    """The Project Gardener - prunes memory into documentation."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.memory_system = MemorySystem(project_root)
        self.agent = get_runner("gardener")

    async def run_synthesis(self) -> str:
        """Fetch memory, synthesize with agent, and return findings."""
        if not self.agent:
            return "Error: Gardener agent not found in registry."

        memory_md = self.memory_system.synthesize_to_markdown()
        if "No recent memory fragments" in memory_md:
            return memory_md

        prompt = f"""
I have collected the following recent memory fragments from the agent sessions.
Please synthesize these into a coherent set of documentation updates.

### RECENT MEMORY LOGS:
{memory_md}

### TARGET:
Review the logs and identify:
1. New workspace rules to add to CLAUDE.md.
2. New ADRs for architecture decisions made.
3. Bug reports for persistent frictions.
4. Progress updates for PRD.md.

Produce a set of proposed documentation edits.
"""

        # Use the agent to synthesize
        result = self.agent.run(
            prompt=prompt,
            cwd=self.project_root,
            mode="read-write",  # Gardener is allowed to update docs
            timeout=300,
        )

        return result.stdout if hasattr(result, "stdout") else str(result)
