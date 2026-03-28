"""
CLI Framework - Shared CLI component interfaces.

Provides base classes and protocols for building CLI tools
following the Phenotype hand-roll rules.

Example usage:
    from cli_framework import BaseCommand, CommandRegistry, Flag, command

    # Define a command
    @command("greet", "Print a greeting")
    class GreetCommand(BaseCommand):
        def __init__(self):
            self.add_flag("name", short="n", description="Name to greet")
            self.add_flag("verbose", short="v", description="Verbose output")

        def execute(self, args: list[str]) -> int:
            name = self.get_flag("name") or "World"
            print(f"Hello, {name}!")
            return 0

    # Register and run
    registry = CommandRegistry()
    registry.register(GreetCommand)
    registry.run("greet", ["--name", "Alice"])
"""

from .command import BaseCommand, CommandMetadata, CommandResult, command
from .parser import Flag, PositionalArg, ArgumentParser, ParseError, SubcommandParser
from .registry import CommandRegistry, CommandRegistration, get_registry, register_command
from .help import HelpGenerator, HelpColors, MinimalHelpFormatter

__all__ = [
    # Core command classes
    "BaseCommand",
    "CommandMetadata",
    "CommandResult",
    "command",
    # Parser components
    "Flag",
    "PositionalArg",
    "ArgumentParser",
    "ParseError",
    "SubcommandParser",
    # Registry
    "CommandRegistry",
    "CommandRegistration",
    "get_registry",
    "register_command",
    # Help generation
    "HelpGenerator",
    "HelpColors",
    "MinimalHelpFormatter",
]

__version__ = "0.1.0"
