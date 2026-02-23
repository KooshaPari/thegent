"""Operator command aliases for ergonomic CLI workflows.

# @trace WL-278
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CommandAlias:
    """Represents a command alias mapping."""

    alias: str
    command: str


class OperatorCommandAliases:
    """Registry for operator command aliases."""

    def __init__(self) -> None:
        """Initialize the operator command aliases registry."""
        self._aliases: dict[str, CommandAlias] = {}

    def register(self, alias: str, command: str) -> CommandAlias:
        """Register a command alias.

        Args:
            alias: The short alias.
            command: The full command to expand to.

        Returns:
            The created CommandAlias.
        """
        cmd_alias = CommandAlias(alias=alias, command=command)
        self._aliases[alias] = cmd_alias
        return cmd_alias

    def resolve(self, alias: str) -> str:
        """Resolve an alias to its full command.

        Args:
            alias: The alias to resolve.

        Returns:
            The expanded command string.

        Raises:
            KeyError: If the alias is not found.
        """
        if alias not in self._aliases:
            raise KeyError(f"Alias '{alias}' not found")
        return self._aliases[alias].command

    def all_aliases(self) -> list[CommandAlias]:
        """Get all registered aliases.

        Returns:
            A list of all CommandAlias objects.
        """
        return list(self._aliases.values())

    def unregister(self, alias: str) -> None:
        """Unregister a command alias.

        Args:
            alias: The alias to remove.

        Raises:
            KeyError: If the alias is not found.
        """
        if alias not in self._aliases:
            raise KeyError(f"Alias '{alias}' not found")
        del self._aliases[alias]
