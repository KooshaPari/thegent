# CLI Commands
# Part of thegent-cli sub-project
from typing import Any


def main() -> None:
    """Main CLI entry point."""


def run(command: str, **kwargs: Any) -> None:
    """Run a CLI command."""


def list_commands() -> list[str]:
    """List available commands."""
    return ["task", "agent", "serve", "status"]
