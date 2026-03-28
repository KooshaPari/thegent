"""
Base Command Interface for CLI Framework.

Provides the foundation for building command-line tools following
hexagonal architecture principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CommandMetadata:
    """Metadata for a command."""

    name: str
    description: str
    help_text: Optional[str] = None
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    deprecated: bool = False
    deprecation_message: Optional[str] = None


class BaseCommand(ABC):
    """
    Abstract base class for CLI commands.

    Subclass this to create a new command. Define the `metadata` class
    attribute and implement `execute`.

    Example:
        class MyCommand(BaseCommand):
            metadata = CommandMetadata(
                name="my-command",
                description="Does something useful"
            )

            def __init__(self):
                super().__init__()
                self.add_flag("verbose", short="v", description="Verbose output")

            def execute(self, args: list[str]) -> int:
                if self.get_flag("verbose"):
                    print("Running in verbose mode")
                return 0
    """

    metadata: CommandMetadata

    def __init__(self) -> None:
        """Initialize command. Override to add flags and positional args."""
        # Initialize instance attributes
        object.__setattr__(self, '_flags', {})
        object.__setattr__(self, '_positional', [])
        self._setup()

    def _setup(self) -> None:
        """Hook for subclasses to set up flags and arguments."""
        pass

    def add_flag(
        self,
        name: str,
        short: Optional[str] = None,
        description: str = "",
        default: Any = None,
        required: bool = False,
    ) -> None:
        """Add a flag to this command.

        Args:
            name: Flag name (e.g., "verbose")
            short: Short flag (e.g., "v")
            description: Help text for the flag
            default: Default value
            required: Whether the flag is required
        """
        flags = object.__getattribute__(self, '_flags')
        flags[name] = {
            "short": short,
            "description": description,
            "default": default,
            "required": required,
            "value": default,
        }

    def add_positional(self, name: str, description: str = "", required: bool = True) -> None:
        """Add a positional argument to this command."""
        positional = object.__getattribute__(self, '_positional')
        positional.append({"name": name, "description": description, "required": required})

    def get_flag(self, name: str) -> Any:
        """Get the value of a parsed flag."""
        flags = object.__getattribute__(self, '_flags')
        return flags.get(name, {}).get("value")

    def get_positional(self, index: int) -> Optional[str]:
        """Get a positional argument by index."""
        positional = object.__getattribute__(self, '_positional')
        if 0 <= index < len(positional):
            return positional[index].get("value")
        return None

    def _get_flags(self) -> dict:
        """Get the flags dictionary."""
        return object.__getattribute__(self, '_flags')

    def _get_positional(self) -> list:
        """Get the positional arguments list."""
        return object.__getattribute__(self, '_positional')

    def _set_positional(self, value: list) -> None:
        """Set the positional arguments list."""
        object.__setattr__(self, '_positional', value)

    def parse_args(self, args: list[str]) -> bool:
        """Parse command-line arguments.

        Args:
            args: Command-line arguments (excluding command name)

        Returns:
            True if parsing succeeded, False otherwise
        """
        from .parser import ArgumentParser

        parser = ArgumentParser(self)
        return parser.parse(args)

    @abstractmethod
    def execute(self, args: list[str]) -> int:
        """Execute the command.

        Args:
            args: Remaining unparsed arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        ...

    def run(self, args: list[str]) -> int:
        """Parse arguments and execute the command.

        Args:
            args: Command-line arguments

        Returns:
            Exit code
        """
        if not self.parse_args(args):
            return 1
        return self.execute(args)

    def print_help(self) -> None:
        """Print help for this command."""
        from .help import HelpGenerator

        HelpGenerator.print_command_help(self)


@dataclass
class CommandResult:
    """Result of a command execution."""

    exit_code: int
    message: str = ""
    data: Any = None

    @property
    def success(self) -> bool:
        """Check if the command succeeded."""
        return self.exit_code == 0


def command(
    name: str,
    description: str,
    help_text: Optional[str] = None,
    aliases: Optional[list[str]] = None,
) -> type:
    """Decorator to create a command class.

    Example:
        @command("greet", "Print a greeting")
        class GreetCommand(BaseCommand):
            def execute(self, args: list[str]) -> int:
                print("Hello!")
                return 0
    """

    def decorator(cls: type) -> type:
        cls.metadata = CommandMetadata(
            name=name, description=description, help_text=help_text, aliases=aliases or []
        )
        return cls

    return decorator
