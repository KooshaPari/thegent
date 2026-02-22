"""Auto-generate CLI examples."""

import subprocess
from typing import Any


class CLIExamplesGenerator:
    """Generate CLI examples automatically."""

    def __init__(self, command: str = "thegent") -> None:
        """Initialize CLI examples generator.

        Args:
            command: Command name
        """
        self.command = command

    def get_all_commands(self) -> list[str]:
        """Get all available commands.

        Returns:
            List of command names
        """
        try:
            result = subprocess.run(
                [self.command, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            # Parse help output to extract commands
            commands = []
            for line in result.stdout.split("\n"):
                if line.strip().startswith(self.command):
                    commands.append(line.strip())
            return commands
        except Exception:
            return []

    def generate_examples(self, command: str) -> list[dict[str, Any]]:
        """Generate examples for a command.

        Args:
            command: Command name

        Returns:
            List of example dictionaries
        """
        examples = []

        # Generate basic example
        examples.append(
            {
                "command": f"{self.command} {command}",
                "description": f"Run {command} command",
            }
        )

        # Generate with common options
        examples.append(
            {
                "command": f"{self.command} {command} --help",
                "description": f"Show help for {command}",
            }
        )

        return examples

    def render_markdown(self, examples: list[dict[str, Any]]) -> str:
        """Render examples as markdown.

        Args:
            examples: List of example dictionaries

        Returns:
            Markdown string
        """
        lines = ["## Examples", ""]
        for ex in examples:
            lines.append("```bash")
            lines.append(ex["command"])
            lines.append("```")
            if ex.get("description"):
                lines.append(f"*{ex['description']}*")
            lines.append("")
        return "\n".join(lines)
