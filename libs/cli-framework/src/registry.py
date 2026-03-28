"""
Command Registry for CLI Framework.

Centralized registry for command discovery and execution.
"""

from typing import TYPE_CHECKING, Optional, Type
from dataclasses import dataclass, field

from .command import BaseCommand

if TYPE_CHECKING:
    from .parser import SubcommandParser


@dataclass
class CommandRegistration:
    """Registration information for a command."""

    name: str
    command_class: Type[BaseCommand]
    group: Optional[str] = None
    description: str = ""
    aliases: list[str] = field(default_factory=list)


class CommandRegistry:
    """
    Central registry for CLI commands.

    Provides command discovery, registration, and execution capabilities.

    Example:
        registry = CommandRegistry()

        @registry.command(group="admin")
        class MyCommand(BaseCommand):
            metadata = CommandMetadata(name="my-cmd", description="My command")

            def execute(self, args: list[str]) -> int:
                print("Running my command")
                return 0

        # List available commands
        registry.list_commands()

        # Execute a command
        registry.run("my-cmd", ["--verbose"])
    """

    def __init__(self) -> None:
        self._commands: dict[str, CommandRegistration] = {}
        self._groups: dict[str, list[str]] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        command_class: Type[BaseCommand],
        name: Optional[str] = None,
        group: Optional[str] = None,
        aliases: Optional[list[str]] = None,
    ) -> None:
        """Register a command class.

        Args:
            command_class: The command class to register
            name: Override the command name (defaults to metadata.name)
            group: Command group for organization
            aliases: Alternative names for the command
        """
        metadata = command_class.metadata
        cmd_name = name or metadata.name

        registration = CommandRegistration(
            name=cmd_name,
            command_class=command_class,
            group=group,
            description=metadata.description,
            aliases=aliases or metadata.aliases,
        )

        self._commands[cmd_name] = registration

        # Track aliases
        for alias in registration.aliases:
            self._aliases[alias] = cmd_name

        # Track groups
        if group:
            if group not in self._groups:
                self._groups[group] = []
            self._groups[group].append(cmd_name)

    def command(
        self, group: Optional[str] = None, aliases: Optional[list[str]] = None
    ) -> Type[BaseCommand]:
        """Decorator to register a command class.

        Example:
            @registry.command(group="admin")
            class MyCommand(BaseCommand):
                metadata = CommandMetadata(name="my-cmd", description="My command")
                ...
        """

        def decorator(cls: Type[BaseCommand]) -> Type[BaseCommand]:
            self.register(cls, group=group, aliases=aliases)
            return cls

        return decorator

    def get(self, name: str) -> Optional[Type[BaseCommand]]:
        """Get a command class by name or alias.

        Args:
            name: Command name or alias

        Returns:
            The command class or None if not found
        """
        # Direct lookup
        if name in self._commands:
            return self._commands[name].command_class

        # Alias lookup
        if name in self._aliases:
            return self._commands[self._aliases[name]].command_class

        return None

    def get_registration(self, name: str) -> Optional[CommandRegistration]:
        """Get the full registration for a command."""
        if name in self._commands:
            return self._commands[name]

        if name in self._aliases:
            return self._commands[self._aliases[name]]

        return None

    def run(self, name: str, args: list[str]) -> int:
        """Run a command by name.

        Args:
            name: Command name or alias
            args: Command-line arguments

        Returns:
            Exit code from the command
        """
        command_class = self.get(name)
        if command_class is None:
            print(f"Unknown command: {name}")
            return 1

        try:
            command_instance = command_class()
            return command_instance.run(args)
        except Exception as e:
            print(f"Error running command {name}: {e}")
            return 1

    def list_commands(self, group: Optional[str] = None) -> list[str]:
        """List registered command names.

        Args:
            group: Optional group to filter by

        Returns:
            List of command names
        """
        if group:
            return self._groups.get(group, [])

        return list(self._commands.keys())

    def list_groups(self) -> list[str]:
        """List all command groups."""
        return list(self._groups.keys())

    def commands_in_group(self, group: str) -> list[CommandRegistration]:
        """Get all commands in a group."""
        command_names = self._groups.get(group, [])
        return [self._commands[name] for name in command_names if name in self._commands]

    def get_all_commands(self) -> list[CommandRegistration]:
        """Get all registered commands."""
        return list(self._commands.values())

    def autocomplete(self, prefix: str) -> list[str]:
        """Get commands that match a prefix for shell completion.

        Args:
            prefix: Command name prefix

        Returns:
            List of matching command names
        """
        return [name for name in self._commands if name.startswith(prefix)]


# Global registry instance
_global_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """Get the global command registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CommandRegistry()
    return _global_registry


def register_command(
    command_class: Type[BaseCommand],
    name: Optional[str] = None,
    group: Optional[str] = None,
    aliases: Optional[list[str]] = None,
) -> None:
    """Register a command with the global registry."""
    get_registry().register(command_class, name, group, aliases)


def command(
    group: Optional[str] = None, aliases: Optional[list[str]] = None
) -> Type[BaseCommand]:
    """Decorator to register a command with the global registry."""
    return get_registry().command(group, aliases)
